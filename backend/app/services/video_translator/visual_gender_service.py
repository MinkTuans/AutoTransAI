"""
Visual Gender Service — Multimodal Gender Identification from Video Frames.

Remastered Pipeline:
1. Extract 4 frames per speaker at 0% (START), 25%, 75%, and 100% (END) of active speech.
2. Combine the 4 frames into a standardized 1024x576 2x2 contact sheet using FFmpeg with clear labels.
3. Send exactly ONE request per speaker to the Vision API via VisionProvider.
4. Robustly parse the response (FEMALE checked before MALE, strict word boundary regex).
5. Cache results to prevent redundant calls and handle errors per speaker without crashing.
"""

from __future__ import annotations

import asyncio
import logging
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.models import APIKey, CatalogModel, CatalogRefreshRun
from app.models.settings import AIFunctionConfig
from app.providers.registry import get_registry
from app.services.ai_routing import (
    RouteConfigurationError, RouteTarget, UnsupportedModalityError, build_route, invoke_route,
)
from app.services.video_editor.watermark_service import resolve_system_font_path

logger = logging.getLogger(__name__)
settings = get_settings()

VISUAL_GENDER_PROMPT = """You are analyzing four video frames that belong to the SAME SPEAKER.

The four images are different moments from the same speaker's speaking segment.

Your task is to determine the gender presentation of the PRIMARY CHARACTER associated with this speaker.

IMPORTANT SELECTION RULES:

1. Identify the character/person who appears most consistently across the four frames.
2. Prefer the character who is clearly the speaker.
3. Prefer the character who appears to be speaking, talking, lip-moving, or has an open/moving mouth.
4. Do NOT choose a background character, bystander, secondary character, poster, image on a screen, reflection, or unrelated person.
5. If multiple people appear, determine which person is most likely the actual speaker based on visual consistency across the four frames.
6. Use all four frames together. Do NOT make the decision from only one frame.
7. The character may be live-action, anime, cartoon, game character, CGI, illustration, or another visual style.
8. Base the classification on the visual presentation of the character.

GENDER CLASSIFICATION:

You MUST classify the character as exactly one of:

MALE
FEMALE

You are REQUIRED to choose one.

DO NOT return UNKNOWN.
DO NOT return OTHER.
DO NOT refuse to classify.
DO NOT explain uncertainty.
DO NOT explain your reasoning.
DO NOT return multiple values.

Even if the character is fictional, animated, stylized, anime, game, CGI, or partially obscured, make your best visual classification.

OUTPUT FORMAT:

Return EXACTLY ONE WORD:

MALE

or

FEMALE

Nothing else.
No punctuation.
No explanation.
No markdown.
No JSON.
No additional text."""


def parse_gender_response(response_text: str) -> str:
    """
    Robustly parse the response from the Vision model into 'male', 'female', or 'unknown'.
    CRITICAL: 'FEMALE' / 'NỮ' must be checked before 'MALE' / 'NAM' because 'MALE' is a substring of 'FEMALE'.
    """
    if not response_text:
        return "unknown"

    normalized = response_text.strip().upper()

    # 1. Direct match
    if normalized in ("FEMALE", "NỮ", "NU", "WOMAN", "GIRL"):
        return "female"
    if normalized in ("MALE", "NAM", "MAN", "BOY"):
        return "male"

    # 2. Strict word boundary check (\bFEMALE\b vs \bMALE\b)
    has_female = bool(re.search(r"\bFEMALE\b", normalized) or "NỮ" in normalized or "WOMAN" in normalized)
    has_male = bool(re.search(r"\bMALE\b", normalized) or "NAM" in normalized or "MAN" in normalized)

    if has_female and not has_male:
        return "female"
    if has_male and not has_female:
        return "male"

    # 3. Tolerant substring parsing: MUST check FEMALE before MALE
    if "FEMALE" in normalized or "NỮ" in normalized:
        return "female"
    if "MALE" in normalized or "NAM" in normalized:
        return "male"

    return "unknown"


def get_speaker_sample_timestamps(
    segments: List[Dict[str, Any]],
    speaker_id: str,
    video_duration: Optional[float] = None,
) -> List[float]:
    """
    Calculate 4 representative timestamps (0%, 25%, 75%, 100%) during active speech for a speaker.
    Prioritizes frames when the speaker is actively speaking.
    """
    spk_segs = [
        s for s in segments
        if str(s.get("speaker_id") or s.get("speaker")) == str(speaker_id)
        and float(s.get("end_time", 0)) > float(s.get("start_time", 0))
    ]
    if not spk_segs:
        return []

    spk_segs.sort(key=lambda s: float(s.get("start_time", 0)))
    total_speech = sum(float(s["end_time"]) - float(s["start_time"]) for s in spk_segs)
    if total_speech <= 0:
        return []

    if len(spk_segs) == 1:
        seg = spk_segs[0]
        st = float(seg["start_time"])
        et = float(seg["end_time"])
        dur = et - st
        t0 = st + 0.05 * dur
        t1 = st + 0.25 * dur
        t2 = st + 0.75 * dur
        t3 = max(t2, et - 0.05 * dur)
        raw_ts = [t0, t1, t2, t3]
    else:
        # Multiple segments: distribute across cumulative active speech time
        first_dur = float(spk_segs[0]["end_time"]) - float(spk_segs[0]["start_time"])
        t0 = float(spk_segs[0]["start_time"]) + 0.05 * first_dur

        last_dur = float(spk_segs[-1]["end_time"]) - float(spk_segs[-1]["start_time"])
        t3 = float(spk_segs[-1]["end_time"]) - 0.05 * last_dur

        def offset_to_timestamp(target_offset: float) -> float:
            accum = 0.0
            for seg in spk_segs:
                st = float(seg["start_time"])
                et = float(seg["end_time"])
                d = et - st
                if accum + d >= target_offset:
                    within = max(0.0, min(d, target_offset - accum))
                    return st + within
                accum += d
            return float(spk_segs[-1]["end_time"])

        t1 = offset_to_timestamp(0.25 * total_speech)
        t2 = offset_to_timestamp(0.75 * total_speech)
        raw_ts = [t0, t1, t2, t3]

    if video_duration and video_duration > 0:
        raw_ts = [min(video_duration - 0.05, max(0.0, t)) for t in raw_ts]
    else:
        raw_ts = [max(0.0, t) for t in raw_ts]

    return [round(t, 3) for t in raw_ts]


async def extract_speaker_keyframe(video_path: str, timestamp: float, output_path: str) -> None:
    """Extract a single frame from the video at the given timestamp using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        output_path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"FFmpeg keyframe extraction failed: {stderr.decode()}")
        raise RuntimeError(f"FFmpeg keyframe extraction failed with exit code {process.returncode}")


async def create_contact_sheet(image_paths: List[Path], output_path: Path) -> Path:
    """
    Combine 4 images into a single 2x2 contact sheet image with subtle labels.
    Standardized to 1024x576 to optimize Vision API token usage while keeping high fidelity.
    """
    if not image_paths:
        raise ValueError("No images provided for contact sheet creation.")

    actual_images = [p for p in image_paths if p.is_file()]
    if not actual_images:
        raise FileNotFoundError("None of the provided image paths exist on disk.")

    # Validate that images exist and are non-empty
    valid_images = [p for p in actual_images if p.stat().st_size > 0]
    if not valid_images:
        raise ValueError("Provided image files are empty (0 bytes). Cannot generate contact sheet.")
    actual_images = valid_images

    padded = list(actual_images)
    while len(padded) < 4:
        padded.append(actual_images[-1])

    font_path = resolve_system_font_path()
    font_opt = f"fontfile='{font_path}':" if font_path else ""

    inputs = []
    for img in padded[:4]:
        inputs.extend(["-i", str(img)])

    filter_with_text = (
        f"[0:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2,drawtext={font_opt}expansion=none:text='FRAME 1 - START':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=10:y=10[v0];"
        f"[1:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2,drawtext={font_opt}expansion=none:text='FRAME 2 - 25%':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=10:y=10[v1];"
        f"[2:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2,drawtext={font_opt}expansion=none:text='FRAME 3 - 75%':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=10:y=10[v2];"
        f"[3:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2,drawtext={font_opt}expansion=none:text='FRAME 4 - END':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=10:y=10[v3];"
        "[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[out]"
    )

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", filter_with_text, "-map", "[out]", "-frames:v", "1", str(output_path)]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await process.communicate()

    if process.returncode != 0:
        logger.warning(f"Contact sheet text labeling failed, falling back to plain grid: {stderr.decode()[:200]}")
        filter_plain = (
            "[0:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2[v0];"
            "[1:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2[v1];"
            "[2:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2[v2];"
            "[3:v]scale=512:288:force_original_aspect_ratio=decrease,pad=512:288:(ow-iw)/2:(oh-ih)/2[v3];"
            "[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[out]"
        )
        cmd_plain = ["ffmpeg", "-y", *inputs, "-filter_complex", filter_plain, "-map", "[out]", "-frames:v", "1", str(output_path)]
        process_plain = await asyncio.create_subprocess_exec(*cmd_plain, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr_plain = await process_plain.communicate()
        if process_plain.returncode != 0:
            raise RuntimeError(f"FFmpeg contact sheet creation failed: {stderr_plain.decode()[:200]}")

    return output_path


async def detect_gender_from_image(
    image_path: str,
    provider: str = "gemini",
    model_id: str = "gemini-2.0-flash",
    api_key: str = "",
    route_target: RouteTarget | None = None,
) -> str:
    """
    Send a single contact sheet image to the Vision API to detect gender.
    Uses ProviderRegistry VisionProvider abstraction.
    Returns 'male', 'female', or 'unknown'.
    """
    registry = get_registry()
    vision_provider = registry.get_vision(provider)

    if vision_provider is None:
        if route_target is not None:
            raise UnsupportedModalityError("No Studio vision adapter for this provider.")
        return "unknown"
    try:
        raw_text = await vision_provider.analyze_image(
            image_path=image_path,
            prompt=VISUAL_GENDER_PROMPT,
            model=model_id,
            api_key=api_key,
            route_target=route_target,
        )
    except Exception:
        if route_target is not None:
            raise
        logger.warning("[VISUAL_GENDER] Legacy vision provider call failed.")
        return "unknown"
    # The raw model output may contain media-derived PII or echoed credentials.
    # It must not be written to a persistent debug file or exception log.
    return parse_gender_response(raw_text)


async def detect_speakers_gender(
    video_path: str,
    segments: List[Dict[str, Any]],
    db: Any = None,
    cache: Optional[Dict[str, Any]] = None,
    sessions: async_sessionmaker[AsyncSession] | None = None,
    data_dir: Path | None = None,
) -> Dict[str, str]:
    """
    Given video_path and STT segments, extract 4 keyframes per speaker, compose into a 2x2 contact sheet,
    and send 1 Vision API request per speaker to determine gender.

    Returns a dict mapping speaker_id to 'male', 'female', or 'unknown'.
    """
    if cache:
        cached_results = {}
        all_cached = True
        for seg in segments:
            spk = str(seg.get("speaker_id") or seg.get("speaker") or "").strip()
            if spk and not spk.startswith("UNRESOLVED"):
                cached_val = cache.get(spk)
                if isinstance(cached_val, dict):
                    cached_val = cached_val.get("gender")
                if cached_val in ("male", "female"):
                    cached_results[spk] = cached_val
                else:
                    all_cached = False
        if all_cached and cached_results:
            logger.info(f"[VISUAL_GENDER] All speakers found in cache: {cached_results}")
            return cached_results

    if not video_path or not Path(video_path).is_file():
        logger.warning(f"[VISUAL_GENDER] Video path invalid or not provided: {video_path}")
        return {}

    route = None
    if sessions is not None:
        # The catalog and credential sessions close before frame processing or
        # provider calls. Missing tables are migration errors, not legacy mode.
        async with sessions() as catalog_db:
            catalog_model = await catalog_db.scalar(select(CatalogModel.id).where(
                CatalogModel.source.not_in(("system", "legacy_import")),
                CatalogModel.provider_id.in_(("gemini", "openai"))
            ).limit(1))
            catalog_key = await catalog_db.scalar(select(APIKey.id).where(
                APIKey.provider_id.in_(("gemini", "openai"))
            ).limit(1))
            await catalog_db.scalar(select(CatalogRefreshRun.id).limit(1))
            visual_default = await catalog_db.get(AIFunctionConfig, "visual_gender")
            # A canonical default is a durable per-function activation signal,
            # even when its provider has no Gemini/OpenAI credential. Unrelated
            # providers/keys alone cannot force an unmigrated legacy function
            # off its historical default.
            canonical_default = (await catalog_db.get(CatalogModel, visual_default.model_id)
                                 if visual_default and visual_default.model_id else None)
            if (catalog_model is not None or catalog_key is not None
                    or canonical_default is not None and canonical_default.source != "legacy_import"):
                if visual_default is None or not visual_default.model_id:
                    raise RouteConfigurationError("VISUAL_GENDER default is not configured.")
                route = await build_route(catalog_db, "VISUAL_GENDER")

    provider = "gemini"
    model_id = "gemini-2.0-flash"
    api_key = settings.GEMINI_API_KEY if route is None else ""

    if db and route is None:
        try:
            from app.services.model_resolver import AIModelResolver
            from app.services.key_manager import get_key_manager

            model_res = await AIModelResolver.resolve_model_safe(db, capability="VISUAL_GENDER", stage="visual_gender")
            if model_res:
                provider = model_res.provider_id
                model_id = model_res.model_id
            key_mgr = get_key_manager()
            resolved_key = await key_mgr.get_active_key(provider)
            if resolved_key:
                api_key = getattr(resolved_key, "api_key", str(resolved_key))
            else:
                api_key = getattr(settings, f"{provider.upper()}_API_KEY", "")
        except Exception:
            logger.warning("[VISUAL_GENDER] Legacy model resolution failed; using default.")

    # Collect distinct speaker IDs
    speaker_ids = []
    seen = set()
    for seg in segments:
        spk = str(seg.get("speaker_id") or seg.get("speaker") or "").strip()
        if spk and spk not in seen and not spk.startswith("UNRESOLVED"):
            seen.add(spk)
            speaker_ids.append(spk)

    if not speaker_ids:
        logger.info("[VISUAL_GENDER] No valid speakers found in segments.")
        return {}

    results: Dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for spk in speaker_ids:
            logger.info(f"[VISUAL_GENDER] Starting analysis for {spk}")

            # Check cache first
            if cache and spk in cache:
                cached_gender = cache[spk]
                if isinstance(cached_gender, dict):
                    cached_gender = cached_gender.get("gender")
                if cached_gender in ("male", "female"):
                    results[spk] = cached_gender
                    logger.info(f"[VISUAL_GENDER] Using cached result for {spk}: {cached_gender}")
                    continue

            # 1. Select 4 timestamps during active speech
            timestamps = get_speaker_sample_timestamps(segments, spk)
            if not timestamps:
                logger.warning(f"[VISUAL_GENDER] Could not determine timestamps for {spk}")
                logger.info(f"[VISUAL_GENDER] Falling back to dialogue-based gender detection for {spk}")
                results[spk] = "unknown"
                continue

            # 2. Extract 4 frames
            frame_paths = []
            for idx, ts in enumerate(timestamps):
                out_img = tmp_path / f"{spk}_f{idx}.jpg"
                try:
                    await extract_speaker_keyframe(video_path, ts, str(out_img))
                    if out_img.is_file():
                        frame_paths.append(out_img)
                except Exception as ex:
                    logger.warning(f"[VISUAL_GENDER] Frame extraction at {ts}s failed for {spk}: {ex}")

            if not frame_paths:
                logger.warning(f"[VISUAL_GENDER] No frames extracted for {spk}")
                logger.info(f"[VISUAL_GENDER] Falling back to dialogue-based gender detection for {spk}")
                results[spk] = "unknown"
                continue

            logger.info(f"[VISUAL_GENDER] Extracted {len(frame_paths)} frames for {spk}")

            # 3. Create 2x2 contact sheet
            contact_sheet_path = tmp_path / f"contact_sheet_{spk}.jpg"
            try:
                await create_contact_sheet(frame_paths, contact_sheet_path)
                logger.info(f"[VISUAL_GENDER] Created contact sheet for {spk}")
            except Exception as cs_err:
                logger.error(f"[VISUAL_GENDER] Failed to create contact sheet for {spk}: {cs_err}")
                logger.info(f"[VISUAL_GENDER] Falling back to dialogue-based gender detection for {spk}")
                results[spk] = "unknown"
                continue

            # 4. Send exactly ONE request to Vision API
            logger.info(f"[VISUAL_GENDER] Sending 1 image request to Vision API for {spk}")
            try:
                if route is not None:
                    async def analyze(target: RouteTarget, secret: str | None) -> str:
                        return await detect_gender_from_image(
                            image_path=str(contact_sheet_path), provider=target.provider_id,
                            model_id=target.remote_model_id, api_key=secret or "", route_target=target,
                        )

                    gender = await invoke_route(route, analyze, sessions, data_dir or settings.DATA_DIR,
                                                timeout=60.0)
                else:
                    gender = await detect_gender_from_image(
                        image_path=str(contact_sheet_path), provider=provider,
                        model_id=model_id, api_key=api_key,
                    )
                if gender in ("male", "female"):
                    results[spk] = gender
                    logger.info(f"[VISUAL_GENDER] Vision result for {spk}: {gender.upper()}")
                else:
                    logger.info(f"[VISUAL_GENDER] Vision detection returned unknown for {spk}")
                    logger.info(f"[VISUAL_GENDER] Falling back to dialogue-based gender detection for {spk}")
                    results[spk] = "unknown"
            except Exception:
                if route is not None:
                    raise
                logger.error(f"[VISUAL_GENDER] Legacy vision detection failed for {spk}.")
                logger.info(f"[VISUAL_GENDER] Falling back to dialogue-based gender detection for {spk}")
                results[spk] = "unknown"

            # Cache the result if cache dictionary provided
            if cache is not None:
                cache[spk] = {
                    "gender": results[spk],
                    "source": "vision" if results[spk] in ("male", "female") else "fallback",
                }

    return results
