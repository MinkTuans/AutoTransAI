"""
Video Translation Pipeline Service.

Manages audio extraction, Speech-to-Text (STT), Language Detection,
LLM Translation, TTS generation, Audio Synchronization (time-stretching),
and final FFmpeg audio mix / video rendering with real-time progress & logging.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
import shutil
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.core import get_logger
from app.core.job_logger import log_job_event
from app.media.ffprobe import probe_duration_async, get_video_metadata_async
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.providers.registry import get_registry
from app.providers.request_target import resolve_request_target
from app.services.ai_routing import RouteTarget, RouteConfigurationError, UnsupportedModalityError, build_route, invoke_route
from app.models import APIKey, CatalogModel, CatalogRefreshRun
from app.models.settings import AIFunctionConfig
from app.models.video_translator import (
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    TranslationJobStatus,
    AudioMixMode,
)

logger = get_logger(__name__)
settings = get_settings()

# Stage weights for overall progress calculation
STAGE_WEIGHTS = {
    "DOWNLOADING": 10.0,
    "EXTRACTING_AUDIO": 10.0,
    "STT": 20.0,
    "TRANSLATING": 20.0,
    "GENERATING_TTS": 20.0,
    "SYNCING_AUDIO": 5.0,
    "RENDERING": 15.0,
}

STAGE_BASE_OFFSET = {
    "QUEUED": 0.0,
    "DOWNLOADING": 0.0,
    "EXTRACTING_AUDIO": 10.0,
    "STT": 20.0,
    "TRANSLATING": 40.0,
    "SEGMENT_EDITING": 60.0,
    "GENERATING_TTS": 60.0,
    "SYNCING_AUDIO": 80.0,
    "RENDERING": 85.0,
    "COMPLETED": 100.0,
}


def calculate_overall_progress(stage: str, stage_progress_pct: float) -> float:
    """Calculate total overall progress percentage based on stage base offset and stage progress."""
    base = STAGE_BASE_OFFSET.get(stage, 0.0)
    weight = STAGE_WEIGHTS.get(stage, 0.0)
    if stage == "SEGMENT_EDITING":
        return 60.0
    if stage == "COMPLETED":
        return 100.0
    overall = base + (weight * (stage_progress_pct / 100.0))
    return round(min(99.9, max(0.0, overall)), 1)


async def extract_audio_from_video(
    video_path: Path,
    output_audio_path: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> float:
    """
    Extract audio track from video file into 16kHz MONO WAV using real-time FFmpeg process.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    log_job_event(job_id, "EXTRACTING_AUDIO", f"Probing metadata for {video_path.name}")
    meta = await get_video_metadata_async(video_path)
    if not meta.get("has_audio"):
        log_job_event(job_id, "EXTRACTING_AUDIO", "ERROR: Video has no audio stream.")
        raise ValueError("Video không chứa track audio. Không thể thực hiện dịch giọng nói.")

    total_duration = meta.get("duration", 0.0)
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path),
    ]

    log_job_event(job_id, "EXTRACTING_AUDIO", f"Starting FFmpeg audio extraction (Duration: {total_duration:.1f}s)")
    calc_timeout = max(600.0, float(total_duration) * 3.0)
    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=total_duration,
        on_progress=on_progress,
        on_pid=on_pid,
        timeout=calc_timeout,
    )

    if not output_audio_path.exists() or output_audio_path.stat().st_size == 0:
        raise RuntimeError("Không thể trích xuất audio từ video.")

    actual_dur = await probe_duration_async(output_audio_path)
    log_job_event(job_id, "EXTRACTING_AUDIO", f"Audio extraction completed successfully. Duration: {actual_dur:.1f}s")
    return actual_dur


def validate_no_placeholders(segments: List[Dict[str, Any]]) -> None:
    """Ensure no segment text contains mock/placeholder text."""
    placeholder_patterns = [
        r"Phần phát biểu",
        r"Video speech",
        r"Speech segment",
        r"Placeholder",
        r"Mock transcript",
        r"Dummy transcript",
    ]
    pattern = re.compile("|".join(placeholder_patterns), re.IGNORECASE)
    for seg in segments:
        txt = seg.get("text", "")
        if pattern.search(txt):
            raise ValueError(f"STT Error: Transcript contains placeholder text: '{txt}'")


def validate_and_clean_timeline_segments(
    raw_segments: List[Dict[str, Any]],
    total_duration: float,
    job_id: str = "VT-JOB",
) -> List[Dict[str, Any]]:
    """
    Validate, deduplicate, sort, and enforce timeline invariants on STT segments.
    Guarantees no segment end_time exceeds total_duration.
    Logs automated TIMELINE AUDIT REPORT.
    """
    if not raw_segments:
        raise ValueError("STT Error: Không có phân đoạn hội thoại nào được nhận diện.")

    # Sort segments strictly by start_time ASC
    sorted_segs = sorted(raw_segments, key=lambda s: float(s.get("start_time", 0.0)))
    cleaned_segments: List[Dict[str, Any]] = []

    for seg in sorted_segs:
        st = float(seg.get("start_time", 0.0))
        et = float(seg.get("end_time", st + 1.0))
        txt = str(seg.get("text", "")).strip()

        if not txt:
            continue

        # Invariant 1: start_time >= 0
        if st < 0.0:
            st = 0.0

        # Invariant 2: start_time < end_time
        if et <= st:
            et = round(st + 1.0, 2)

        # Invariant 3: end_time <= total_duration
        if et > total_duration:
            diff = et - total_duration
            log_job_event(
                job_id,
                "STT_WARNING",
                f"⚠️ TIMELINE OUT OF BOUNDS: Segment #{seg.get('number')} ('{txt[:30]}...') "
                f"end_time ({et:.2f}s) exceeded video duration ({total_duration:.2f}s) by {diff:.2f}s. "
                f"Correcting end_time to total_duration."
            )
            et = round(total_duration, 2)
            if st >= et:
                st = max(0.0, round(et - 1.0, 2))

        # Deduplicate overlap segments (e.g., from chunk boundary overlap)
        if cleaned_segments:
            prev = cleaned_segments[-1]
            prev_st = prev["start_time"]
            prev_et = prev["end_time"]
            prev_txt = prev["text"]

            # If segment has identical text and starts close to previous segment
            if txt == prev_txt and abs(st - prev_st) < 5.0:
                logger.info(f"[{job_id}] Skipping duplicate segment from chunk overlap: '{txt[:30]}'")
                continue

            # If segment is completely contained within previous segment
            if st >= prev_st and et <= prev_et and (txt in prev_txt or prev_txt in txt):
                logger.info(f"[{job_id}] Skipping contained sub-segment: '{txt[:30]}'")
                continue

        cleaned_segments.append({
            "number": len(cleaned_segments) + 1,
            "start_time": round(st, 2),
            "end_time": round(et, 2),
            "text": txt,
            "speaker_id": str(seg.get("speaker_id") or seg.get("speaker") or f"UNRESOLVED_{len(cleaned_segments) + 1:04d}"),
        })

    if not cleaned_segments:
        raise ValueError("STT Error: Không còn segment hợp lệ sau khi validate timeline.")

    # Final timeline invariants verification
    first_seg = cleaned_segments[0]
    last_seg = cleaned_segments[-1]
    max_segment_end = max(s["end_time"] for s in cleaned_segments)

    if max_segment_end > total_duration + 0.05:
        raise ValueError(
            f"TIMELINE_INVALID: Max segment end ({max_segment_end:.2f}s) exceeds total video duration ({total_duration:.2f}s)."
        )

    # Gap Audit (Detect silent gaps >= 15 seconds)
    gaps = []
    prev_end = 0.0
    for s in cleaned_segments:
        gap_dur = s["start_time"] - prev_end
        if gap_dur >= 15.0:
            gaps.append((round(prev_end, 2), round(s["start_time"], 2), round(gap_dur, 2)))
        prev_end = max(prev_end, s["end_time"])

    audit_report = [
        "========================================",
        "TIMELINE AUDIT REPORT",
        "========================================",
        f"JOB ID: {job_id}",
        f"VIDEO DURATION: {total_duration:.2f}s ({int(total_duration//60)}m {total_duration%60:.1f}s)",
        f"TOTAL SEGMENTS: {len(cleaned_segments)}",
        f"FIRST SEGMENT: #{first_seg['number']} ({first_seg['start_time']:.2f}s -> {first_seg['end_time']:.2f}s)",
        f"LAST SEGMENT: #{last_seg['number']} ({last_seg['start_time']:.2f}s -> {last_seg['end_time']:.2f}s)",
        f"MAX SEGMENT END: {max_segment_end:.2f}s",
        f"TIMELINE VALID: YES",
        f"DETECTED SILENT GAPS (>=15s): {len(gaps)}",
    ]
    for g_start, g_end, g_dur in gaps:
        audit_report.append(f"  - GAP: {g_start:.2f}s -> {g_end:.2f}s (Duration: {g_dur:.2f}s)")
    audit_report.append("========================================")

    log_job_event(job_id, "STT", "\n".join(audit_report))
    return cleaned_segments


async def transcribe_audio_with_whisper(
    audio_path: Path,
    job_id: str = "VT-JOB",
    *,
    route_target: RouteTarget | None = None,
    api_key: str | None = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Transcribe audio file using OpenAI Whisper API (whisper-1).
    Handles large audio files by chunking via FFmpeg with exact chunk duration bounds and overlap.
    """
    remote_model, request_key = resolve_request_target(
        route_target, api_key, provider_id="openai", capabilities=("STT",),
        legacy_model="whisper-1", legacy_key=settings.OPENAI_API_KEY,
    )
    if not request_key:
        raise ValueError("OPENAI_API_KEY chưa được cấu hình trong .env")

    import httpx
    from app.core.pipeline_errors import classify_http_error
    total_duration = await probe_duration_async(audio_path)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)

    max_chunk_sec = 120.0
    overlap_sec = 5.0
    chunks: List[Tuple[Path, float, float]] = []  # (chunk_path, time_offset, actual_chunk_duration)
    temp_dir: Optional[Path] = None

    try:
        if file_size_mb > 15.0 or total_duration > max_chunk_sec:
            log_job_event(job_id, "STT", f"[Whisper] Large audio file ({file_size_mb:.1f}MB, {total_duration:.1f}s). Slicing audio into {max_chunk_sec}s chunks (Overlap: {overlap_sec}s)...")
            temp_dir = audio_path.parent / f"whisper_chunks_{job_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            chunk_idx = 0
            curr_start = 0.0
            while curr_start < total_duration:
                chunk_len = min(max_chunk_sec, total_duration - curr_start)
                if chunk_len <= 0:
                    break

                chunk_path = temp_dir / f"chunk_{chunk_idx:03d}.wav"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-ss", f"{curr_start:.2f}",
                    "-t", f"{chunk_len:.2f}",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(chunk_path)
                ]
                await run_ffmpeg_with_progress_async(cmd, timeout=120.0)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Whisper STT: Audio chunk file lost or failed to generate: {chunk_path.name}")

                actual_dur = await probe_duration_async(chunk_path)
                chunks.append((chunk_path, curr_start, actual_dur))

                if curr_start + chunk_len >= total_duration:
                    break
                curr_start += (chunk_len - overlap_sec)
                chunk_idx += 1
        else:
            chunks.append((audio_path, 0.0, total_duration))

        all_segments = []
        detected_lang = "English"
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {request_key}"}

        async with httpx.AsyncClient(timeout=180.0) as client:
            for chunk_path, time_offset, actual_chunk_dur in chunks:
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Whisper STT: Audio chunk file missing before API call: {chunk_path.name}")

                log_job_event(job_id, "STT", f"[Whisper] Transcribing chunk {chunk_path.name} (Offset: {time_offset:.1f}s, Dur: {actual_chunk_dur:.1f}s)...")
                with open(chunk_path, "rb") as f:
                    files = {"file": (chunk_path.name, f, "audio/wav")}
                    data = {"model": remote_model, "response_format": "verbose_json"}
                    res = await client.post(url, headers=headers, files=files, data=data)

                if res.status_code != 200:
                    raise classify_http_error(
                        status_code=res.status_code,
                        response_text="",
                        provider="openai",
                        model=remote_model,
                        stage="STT",
                    )

                res_json = res.json()
                detected_lang = res_json.get("language", detected_lang)
                whisper_segs = res_json.get("segments", [])

                if not whisper_segs and res_json.get("text"):
                    whisper_segs = [{
                        "start": 0.0,
                        "end": actual_chunk_dur,
                        "text": res_json["text"]
                    }]

                for w_seg in whisper_segs:
                    local_st = float(w_seg.get("start", 0.0))
                    local_et = float(w_seg.get("end", local_st + 4.0))
                    txt = str(w_seg.get("text", "")).strip()

                    if not txt:
                        continue

                    if local_st >= time_offset and time_offset > 0:
                        local_st -= time_offset
                        local_et -= time_offset

                    if local_st < 0.0:
                        local_st = 0.0
                    if local_et > actual_chunk_dur + 0.5:
                        local_et = min(local_et, actual_chunk_dur)

                    if local_st >= actual_chunk_dur:
                        continue

                    st = round(time_offset + local_st, 2)
                    et = round(time_offset + max(local_st + 0.5, local_et), 2)

                    all_segments.append({
                        "number": len(all_segments) + 1,
                        "start_time": st,
                        "end_time": et,
                        "text": txt,
                    })

        if not all_segments:
            raise RuntimeError("OpenAI Whisper API không nhận diện được giọng nói trong audio.")

        validate_no_placeholders(all_segments)
        validated_segments = validate_and_clean_timeline_segments(all_segments, total_duration, job_id=job_id)
        log_job_event(job_id, "STT", f"Whisper STT completed successfully. Detected: {detected_lang}, Validated Segments: {len(validated_segments)}")
        return validated_segments, detected_lang
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


async def transcribe_audio_with_gemini(
    audio_path: Path,
    job_id: str = "VT-JOB",
    model_name: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    *,
    route_target: RouteTarget | None = None,
    api_key: str | None = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Transcribe audio file using Google Gemini API.
    Handles large audio files (>5MB or >90s) by chunking via FFmpeg with exact chunk duration bounds and overlap.
    """
    remote_model, request_key = resolve_request_target(
        route_target, api_key, provider_id="gemini", capabilities=("STT",),
        legacy_model=model_name, legacy_key=settings.GEMINI_API_KEY,
    )
    if not request_key:
        raise ValueError("GEMINI_API_KEY chưa được cấu hình trong .env")

    import httpx
    from app.providers.ai_router import AIRouter
    from app.providers.llm.gemini_provider import strip_gemini_model_prefix
    from app.core.pipeline_errors import PipelineError, classify_http_error
    from app.services.video_translator.stt_parser import parse_gemini_stt_response

    # Resolve active STT provider & model via AIModelResolver (Settings Database)
    if route_target is None:
        resolved_info = await AIRouter.resolve_stt_model(db, requested_model=remote_model)
        configured_model = resolved_info["model_id"]
        model_source = resolved_info["source"]
    else:
        configured_model = remote_model
        model_source = "CATALOG ROUTE"
        resolved_info = {"provider_id": route_target.provider_id}
    # Use model directly — NO normalization, NO rewriting
    primary_model = strip_gemini_model_prefix(configured_model)

    logger.info(
        f"[STT ROUTING] Capability: STT | "
        f"Selected Provider: {resolved_info['provider_id']} | "
        f"Selected Model: {primary_model} | "
        f"Model Source: {model_source} | "
        f"Fallback Enabled: false"
    )
    log_job_event(job_id, "STT", f"[STT ROUTING] Active STT Model: {primary_model} (Source: {model_source})")

    total_duration = await probe_duration_async(audio_path)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)

    max_chunk_sec = 90.0
    overlap_sec = 5.0
    chunks: List[Tuple[Path, float, float]] = []  # (chunk_path, time_offset, actual_chunk_duration)
    temp_dir: Optional[Path] = None

    try:
        if file_size_mb > 5.0 or total_duration > max_chunk_sec:
            log_job_event(job_id, "STT", f"[Gemini] Large audio file ({file_size_mb:.1f}MB, {total_duration:.1f}s). Slicing audio into {max_chunk_sec}s chunks (Overlap: {overlap_sec}s)...")
            temp_dir = audio_path.parent / f"gemini_chunks_{job_id}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            chunk_idx = 0
            curr_start = 0.0
            while curr_start < total_duration:
                chunk_len = min(max_chunk_sec, total_duration - curr_start)
                if chunk_len <= 0:
                    break

                chunk_path = temp_dir / f"g_chunk_{chunk_idx:03d}.wav"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-ss", f"{curr_start:.2f}",
                    "-t", f"{chunk_len:.2f}",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    str(chunk_path)
                ]
                await run_ffmpeg_with_progress_async(cmd, timeout=120.0)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Gemini STT: Audio chunk file lost or failed to generate: {chunk_path.name}")

                actual_dur = 0.0
                for attempt in range(3):
                    try:
                        actual_dur = await probe_duration_async(chunk_path)
                        if actual_dur > 0:
                            break
                    except Exception as probe_err:
                        if attempt == 2:
                            raise RuntimeError(f"Gemini STT: Failed to probe duration for chunk {chunk_path.name}: {str(probe_err)}")
                        await asyncio.sleep(0.5)

                chunks.append((chunk_path, curr_start, actual_dur))

                if curr_start + chunk_len >= total_duration:
                    break
                curr_start += (chunk_len - overlap_sec)
                chunk_idx += 1
        else:
            chunks.append((audio_path, 0.0, total_duration))

        all_segments = []
        detected_lang = "English"

        async with httpx.AsyncClient(timeout=120.0) as client:
            for chunk_path, time_offset, actual_chunk_dur in chunks:
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"Gemini STT: Audio chunk file missing before API call: {chunk_path.name}")

                log_job_event(job_id, "STT", f"[Gemini] Transcribing chunk {chunk_path.name} (Offset: {time_offset:.1f}s, Dur: {actual_chunk_dur:.1f}s)...")
                with open(chunk_path, "rb") as f:
                    audio_bytes = f.read()

                prompt = (
                    f"Phân tích file audio này (độ dài thực tế file audio: {actual_chunk_dur:.2f} giây) và thực hiện 3 việc:\n"
                    "1. Nhận diện ngôn ngữ được nói trong audio (ví dụ: English, Vietnamese, Japanese, Chinese, French, German).\n"
                    "2. Phân loại người nói (Speaker Diarization). Gán cho mỗi người nói một ID (ví dụ: Speaker 1, Speaker 2).\n"
                    "3. Trích xuất toàn bộ bản chép lời (transcript) theo từng câu có mốc thời gian start_time và end_time tính bằng giây, KÈM THEO ID của người nói (speaker_id).\n"
                    "LƯU Ý BẮT BUỘC VỀ TIMESTAMP:\n"
                    f"- mốc thời gian (start_time, end_time) BẮT BUỘC là thời gian RELATIVE tính từ 0.0 giây đến tối đa {actual_chunk_dur:.2f} giây trong file audio chunk này.\n"
                    f"- KHÔNG ĐƯỢC tạo timestamp vượt quá {actual_chunk_dur:.2f} giây.\n"
                    "- KHÔNG ĐƯỢC dùng mốc thời gian tuyệt đối của toàn bộ video.\n"
                    "Trả về định dạng JSON thuần túy (không markdown) với cấu trúc:\n"
                    "{\n"
                    '  "language": "English",\n'
                    '  "segments": [\n'
                    '    {"start_time": 0.0, "end_time": 4.5, "speaker_id": "Speaker 1", "text": "Sentence text"}\n'
                    '  ]\n'
                    "}"
                )

                base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "audio/wav",
                                        "data": base64_audio,
                                    }
                                },
                            ]
                        }
                    ],
                    "generationConfig": {
                        "response_mime_type": "application/json",
                        "temperature": 0.1,
                    },
                }

                # Use resolved model directly — NO fallback candidate queue
                actual_api_model = f"models/{primary_model}"
                logger.info(f"[STT API REQUEST] Actual model: {actual_api_model} | Chunk: {chunk_path.name}")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{primary_model}:generateContent"
                try:
                    res = await client.post(url, json=payload, headers={"x-goog-api-key": request_key})
                    if res.status_code == 200:
                        data = res.json()
                        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_response = parts[0].get("text", "").strip()
                            try:
                                parsed_json = parse_gemini_stt_response(
                                    raw_response,
                                    actual_chunk_dur=actual_chunk_dur,
                                    default_lang=detected_lang,
                                )
                            except Exception as parse_err:
                                logger.error(f"[Gemini STT Parse Error] Chunk: {chunk_path.name} | Error: {parse_err}")
                                log_job_event(
                                    job_id,
                                    "STT",
                                    f"[Gemini STT Parse Error] Invalid response for {chunk_path.name}"
                                )
                                raise PipelineError(
                                    code="AI_PROVIDER_API_ERROR",
                                    stage="STT",
                                    message=f"Gemini STT trả về JSON không hợp lệ cho chunk {chunk_path.name}.",
                                    provider="gemini",
                                    model=primary_model,
                                    technical_error=str(parse_err),
                                ) from parse_err

                            detected_lang = parsed_json.get("language", detected_lang)
                            raw_segments = parsed_json.get("segments", [])

                            if raw_segments:
                                for s in raw_segments:
                                    local_st = float(s.get("start_time", 0.0))
                                    local_et = float(s.get("end_time", local_st + 4.0))
                                    txt = str(s.get("text", "")).strip()

                                    if not txt:
                                        continue

                                    # Handle case where model returns absolute video timestamps
                                    if local_st >= time_offset and time_offset > 0:
                                        logger.info(f"[{job_id}] Model returned absolute timestamp {local_st:.2f}s for chunk starting at {time_offset:.2f}s. Adjusting relative timestamp.")
                                        local_st -= time_offset
                                        local_et -= time_offset

                                    # Enforce chunk bounds
                                    if local_st < 0.0:
                                        local_st = 0.0
                                    if local_et > actual_chunk_dur + 0.5:
                                        logger.warning(f"[{job_id}] Segment end {local_et:.2f}s exceeded chunk duration {actual_chunk_dur:.2f}s for {chunk_path.name}. Capping to chunk duration.")
                                        local_et = min(local_et, actual_chunk_dur)

                                    if local_st >= actual_chunk_dur:
                                        continue

                                    st = round(time_offset + local_st, 2)
                                    et = round(time_offset + max(local_st + 0.5, local_et), 2)

                                    all_segments.append({
                                        "number": len(all_segments) + 1,
                                        "start_time": st,
                                        "end_time": et,
                                        "text": txt,
                                        "speaker_id": str(s.get("speaker_id") or s.get("speaker") or f"UNRESOLVED_{len(all_segments) + 1:04d}"),
                                    })
                    else:
                        # Non-200 response — raise structured PipelineError
                        raise classify_http_error(
                            status_code=res.status_code,
                            response_text="",
                            provider="gemini",
                            model=primary_model,
                            stage="STT",
                        )
                except PipelineError:
                    raise
                except (httpx.TimeoutException, httpx.RequestError):
                    raise PipelineError(code="NETWORK_ERROR", stage="STT", provider="gemini", model=primary_model,
                                        message="Gemini request failed.") from None

        if not all_segments:
            raise RuntimeError("Gemini STT không nhận diện được giọng nói trong audio.")

        validate_no_placeholders(all_segments)
        validated_segments = validate_and_clean_timeline_segments(all_segments, total_duration, job_id=job_id)
        log_job_event(job_id, "STT", f"Gemini STT completed successfully using {primary_model}. Detected: {detected_lang}, Validated Segments: {len(validated_segments)}")
        return validated_segments, detected_lang
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


async def speech_to_text_and_detect_language(
    audio_path: Path,
    job_id: str = "VT-JOB",
    target_language: str = "vi",
    source_language: str = "auto",
    llm_provider_id: str = "gemini",
    stt_model_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    on_status_update: Optional[Callable[[str], None]] = None,
    *,
    sessions: async_sessionmaker[AsyncSession] | None = None,
    data_dir: Path | None = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Transcribe audio through Studio's canonical STT route when initialized.
    Legacy callers without a session factory retain the original provider path.
    """
    total_duration = await probe_duration_async(audio_path)
    if total_duration <= 0:
        raise ValueError("File audio không hợp lệ hoặc không thể đọc.")

    log_job_event(job_id, "STT", f"Starting Speech-to-Text (Audio duration: {total_duration:.1f}s, Primary Provider: {llm_provider_id})")
    if on_status_update:
        on_status_update(f"Đang phân tích audio ({audio_path.stat().st_size / (1024*1024):.1f}MB) với STT...")

    if sessions is not None:
        # Legacy installations have the schema but no canonical model, key,
        # or refresh activity. Missing tables are migration errors: let the
        # database exception surface rather than silently selecting .env keys.
        async with sessions() as catalog_db:
            catalog_model = await catalog_db.scalar(
                select(CatalogModel.id).where(
                    CatalogModel.source != "system", CatalogModel.provider_id.in_(("gemini", "openai"))
                ).limit(1)
            )
            catalog_key = await catalog_db.scalar(
                select(APIKey.id).where(APIKey.provider_id.in_(("gemini", "openai"))).limit(1)
            )
            refresh_run = await catalog_db.scalar(select(CatalogRefreshRun.id).limit(1))
            initialized = any(value is not None for value in (catalog_model, catalog_key, refresh_run))
            if initialized:
                stt_default = await catalog_db.get(AIFunctionConfig, "stt")
                if stt_default is None or not stt_default.model_id:
                    raise RouteConfigurationError("STT default is not configured.")
                route = await build_route(catalog_db, "STT")
        if initialized:
            async def transcribe(target: RouteTarget, secret: str | None):
                if target.provider_id == "gemini":
                    return await transcribe_audio_with_gemini(
                        audio_path, job_id=job_id, route_target=target, api_key=secret,
                    )
                if target.provider_id == "openai":
                    return await transcribe_audio_with_whisper(
                        audio_path, job_id=job_id, route_target=target, api_key=secret,
                    )
                raise UnsupportedModalityError("No Studio STT adapter for this provider.")

            return await invoke_route(route, transcribe, sessions, data_dir or get_settings().DATA_DIR)

    settings = get_settings()
    stt_errors = []
    effective_provider = llm_provider_id or settings.DEFAULT_LLM_PROVIDER

    # Primary Attempt: Gemini STT (Default primary STT engine)
    if effective_provider == "gemini" or (not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY):
        if settings.GEMINI_API_KEY:
            try:
                return await transcribe_audio_with_gemini(audio_path, job_id=job_id, model_name=stt_model_id, db=db)
            except Exception as e:
                err_msg = f"Gemini STT failed: {str(e)}"
                logger.warning(err_msg)
                stt_errors.append(err_msg)

        # Secondary Attempt: OpenAI Whisper ONLY IF explicitly enabled via configuration
        if settings.ENABLE_OPENAI_FALLBACK and settings.OPENAI_API_KEY:
            try:
                log_job_event(job_id, "STT", "[Fallback] Attempting OpenAI Whisper STT fallback (ENABLE_OPENAI_FALLBACK=True)...")
                return await transcribe_audio_with_whisper(audio_path, job_id=job_id)
            except Exception as e:
                err_msg = f"Whisper STT fallback failed: {str(e)}"
                logger.warning(err_msg)
                stt_errors.append(err_msg)
        else:
            log_job_event(job_id, "STT", "[STT] Gemini STT error occurred and Fallback is DISABLED. Stopping without calling OpenAI/Whisper.")
            error_summary = " | ".join(stt_errors) if stt_errors else "Gemini STT Error: Chưa cấu hình GEMINI_API_KEY hợp lệ."
            raise RuntimeError(f"STT FAILED: {error_summary}")
    else:
        # User explicitly requested OpenAI STT
        if settings.OPENAI_API_KEY:
            try:
                return await transcribe_audio_with_whisper(audio_path, job_id=job_id)
            except Exception as e:
                err_msg = f"Whisper STT failed: {str(e)}"
                logger.warning(err_msg)
                stt_errors.append(err_msg)

        if settings.ENABLE_OPENAI_FALLBACK and settings.GEMINI_API_KEY:
            try:
                log_job_event(job_id, "STT", "[Fallback] Attempting Gemini STT fallback...")
                return await transcribe_audio_with_gemini(audio_path, job_id=job_id, model_name=stt_model_id, db=db)
            except Exception as e:
                err_msg = f"Gemini STT fallback failed: {str(e)}"
                logger.warning(err_msg)
                stt_errors.append(err_msg)

    # If all attempted STT providers fail
    error_summary = " | ".join(stt_errors) if stt_errors else "Chưa cấu hình API Key hợp lệ trong .env."
    raise RuntimeError(f"STT FAILED: {error_summary}")



def _safe_parse_json_translation(text: str) -> dict:
    """
    Parse JSON translation response robustly.
    Supports:
    1. Structured JSON list of dicts: [{"id": 0, "translation": "..."}, ...] -> returns {0: "...", ...}
    2. Structured JSON dict: {"translations": [{"id": 0, "translation": "..."}]} -> returns {0: "...", ...}
    3. Plain string array: ["trans 1", "trans 2"] -> returns {0: "trans 1", 1: "trans 2"}
    4. Fallback string regex extraction if JSON syntax is slightly damaged.
    """
    json_str = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    json_str = re.sub(r"^```\s*", "", json_str, flags=re.MULTILINE)
    json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
    
    match_arr = re.search(r"\[.*\]", json_str, re.DOTALL)
    match_obj = re.search(r"\{.*\}", json_str, re.DOTALL)
    
    raw_parsed = None
    if match_arr:
        try:
            raw_parsed = json.loads(match_arr.group(0), strict=False)
        except Exception:
            pass
    if raw_parsed is None and match_obj:
        try:
            raw_parsed = json.loads(match_obj.group(0), strict=False)
        except Exception:
            pass
    if raw_parsed is None:
        try:
            cleaned = re.sub(r'[\r\n\t]+', ' ', json_str)
            raw_parsed = json.loads(cleaned, strict=False)
        except Exception:
            pass

    res_dict: dict = {}

    if isinstance(raw_parsed, dict) and "translations" in raw_parsed and isinstance(raw_parsed["translations"], list):
        raw_parsed = raw_parsed["translations"]

    if isinstance(raw_parsed, list):
        for idx, item in enumerate(raw_parsed):
            if isinstance(item, dict):
                item_id = item.get("id")
                if item_id is None:
                    item_id = item.get("n")
                trans = item.get("translation")
                if trans is None:
                    trans = item.get("text", "")
                try:
                    seg_id = int(item_id) if item_id is not None else idx
                except (ValueError, TypeError):
                    seg_id = idx
                res_dict[seg_id] = str(trans).strip()
            elif isinstance(item, str):
                res_dict[idx] = item.strip()
        if res_dict:
            return res_dict

    if isinstance(raw_parsed, dict):
        for k, v in raw_parsed.items():
            try:
                seg_id = int(k)
            except ValueError:
                continue
            if isinstance(v, str):
                res_dict[seg_id] = v.strip()
            elif isinstance(v, dict):
                res_dict[seg_id] = str(v.get("translation", "")).strip()
        if res_dict:
            return res_dict

    # Regex extraction fallback for plain string array or json objects
    dict_matches = re.findall(
        r'\{\s*"(?:id|n)"\s*:\s*(\d+)\s*,\s*"(?:translation|text)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}',
        json_str,
    )
    if dict_matches:
        for seg_id_str, trans_str in dict_matches:
            res_dict[int(seg_id_str)] = trans_str.replace('\\"', '"').replace('\\n', '\n').strip()
        return res_dict

    items = re.findall(r'"((?:[^"\\]|\\.)*)"', json_str)
    if items:
        filtered_items = [it for it in items if it not in ("id", "translation", "translations", "text")]
        for idx, item in enumerate(filtered_items):
            res_dict[idx] = item.replace('\\"', '"').replace('\\n', '\n').strip()
        return res_dict

    raise ValueError(f"Could not parse valid JSON translation response: {text[:200]}")


def _safe_parse_json_list(text: str) -> list:
    """Parse JSON array robustly, maintaining backward compatibility."""
    parsed_map = _safe_parse_json_translation(text)
    if parsed_map:
        max_idx = max(parsed_map.keys())
        return [parsed_map.get(i, "") for i in range(max_idx + 1)]
    raise ValueError(f"Could not parse valid JSON list from response: {text[:200]}")


def dialogue_line_number(seg: Dict[str, Any], fallback_index: int) -> int:
    for key in ("number", "segment_number", "n"):
        raw = seg.get(key)
        if raw is None:
            continue
        try:
            n = int(raw)
        except (TypeError, ValueError):
            continue
        if n >= 1:
            return n
    return fallback_index + 1


def build_numbered_dialogue_payload(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = []
    for i, seg in enumerate(segments):
        lines.append(
            {
                "n": dialogue_line_number(seg, i),
                "text": str(seg.get("text") or seg.get("original_text") or ""),
            }
        )
    return {"lines": lines}


def _load_json_blob(text: str) -> Any:
    json_str = re.sub(r"^```json\s*", "", text or "", flags=re.MULTILINE)
    json_str = re.sub(r"^```\s*", "", json_str, flags=re.MULTILINE)
    json_str = re.sub(r"```$", "", json_str, flags=re.MULTILINE).strip()
    try:
        return json.loads(json_str, strict=False)
    except Exception:
        pass
    obj = re.search(r"\{.*\}", json_str, re.DOTALL)
    if obj:
        try:
            return json.loads(obj.group(0), strict=False)
        except Exception:
            pass
    arr = re.search(r"\[.*\]", json_str, re.DOTALL)
    if arr:
        try:
            return json.loads(arr.group(0), strict=False)
        except Exception:
            pass
    return None


def parse_translation_envelope(text: str, target_language: str = "") -> Tuple[Dict[int, str], List[Dict[str, Any]]]:
    """Parse {lines:[{n,text}], names:[...]} or legacy [{id, translation}]."""
    raw = _load_json_blob(text)
    names_raw: List[Any] = []
    lines_raw: Any = raw
    if isinstance(raw, dict):
        names_raw = raw.get("names") or raw.get("terms") or raw.get("glossary") or []
        if isinstance(raw.get("lines"), list):
            lines_raw = raw["lines"]
        elif isinstance(raw.get("translations"), list):
            lines_raw = raw["translations"]
        elif isinstance(raw.get("items"), list):
            lines_raw = raw["items"]
    lines_map: Dict[int, str] = {}
    if isinstance(lines_raw, list):
        fake = json.dumps(lines_raw, ensure_ascii=False)
        try:
            lines_map = _safe_parse_json_translation(fake)
        except ValueError:
            lines_map = {}
    if not lines_map:
        lines_map = _safe_parse_json_translation(text)
    names: List[Dict[str, Any]] = []
    if isinstance(names_raw, list):
        from app.services.terminology_extractor import normalize_extracted_terms

        names = normalize_extracted_terms([x for x in names_raw if isinstance(x, dict)], target_lang=target_language)
    return lines_map, names


def _ordered_translations(
    parsed_map: Dict[int, str],
    numbers: List[int],
    count: int,
) -> Optional[List[str]]:
    """Prefer STT `n` keys; fall back to legacy 0-based batch ids."""
    zero_based = count > 0 and all(i in parsed_map for i in range(count))
    n_based = bool(numbers) and all(n in parsed_map for n in numbers)
    sequential_n = numbers == list(range(1, count + 1))
    if zero_based and 0 in parsed_map and sequential_n:
        return [parsed_map[i] for i in range(count)]
    if n_based:
        return [parsed_map[n] for n in numbers]
    if zero_based:
        return [parsed_map[i] for i in range(count)]
    return None


def _translation_json_prompt(
    payload: Dict[str, Any],
    source_lang_name: str,
    target_lang_name: str,
    glossary: Optional[Dict[str, str]] = None,
) -> str:
    glossary_rules = ""
    if glossary:
        from app.services.terminology_extractor import is_valid_glossary_mapping

        # Filter out invalid or self-mapped CJK entries that would confuse the LLM
        valid_pairs = [
            (source, target)
            for source, target in sorted(
                glossary.items(), key=lambda item: len(item[0]), reverse=True
            )
            if is_valid_glossary_mapping(source, target, target_lang_name)
        ]
        if valid_pairs:
            pairs = "\n".join(f"- {source} → {target}" for source, target in valid_pairs)
            glossary_rules = (
                "GLOSSARY CANONICAL — BẮT BUỘC dùng đúng translation bên phải "
                "mỗi khi source bên trái xuất hiện:\n"
                f"{pairs}\n\n"
            )
    return (
        "Bạn là dịch giả phim chuyên nghiệp.\n"
        f"Dịch TOÀN BỘ các câu thoại từ {source_lang_name} sang {target_lang_name}.\n"
        "Input là một JSON. Output PHẢI là một JSON cùng hình dạng.\n"
        "Quy tắc:\n"
        "1. Giữ nguyên số thứ tự 'n' của từng câu. Không gộp, không bỏ, không đổi thứ tự.\n"
        f"2. Field 'text' ở output là bản dịch {target_lang_name} (tự nhiên, hợp lồng tiếng).\n"
        f"3. Trong 'names': Chỉ liệt kê TÊN RIÊNG (người/nhân vật, địa danh, tổ chức). "
        f"'source' là tên gốc trong {source_lang_name}, 'translation' phải là tên tương ứng đã được dịch/chuyển tự sang {target_lang_name} (ví dụ: 安妮 → Annie, 詹森 → Jensen, 路斯 → Ruth). "
        f"TUYỆT ĐỐI KHÔNG để 'translation' giữ nguyên chữ Hán khi dịch sang chữ Latin. "
        "Nếu không chắc chắn tên tương ứng ở ngôn ngữ đích, KHÔNG đưa vào 'names'. "
        "Không đưa động từ, đại từ, câu thoại thường vào 'names'.\n"
        f"{glossary_rules}"
        "Output đúng dạng:\n"
        '{"lines":[{"n":1,"text":"..."},{"n":2,"text":"..."}],'
        '"names":[{"source":"...","translation":"...","type":"character"}]}\n\n'
        f"JSON gốc:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def find_glossary_violations(
    segments: List[Dict[str, Any]],
    glossary: Optional[Dict[str, str]],
    source_language: str = "",
    target_language: str = "",
) -> List[Dict[str, Any]]:
    if not glossary:
        return []
    from app.services.glossary_service import normalize_glossary_text
    from app.services.terminology_extractor import is_valid_glossary_mapping

    violations: List[Dict[str, Any]] = []
    skipped_invalid: List[Dict[str, str]] = []
    for index, segment in enumerate(segments, start=1):
        source_text = normalize_glossary_text(
            str(segment.get("text") or segment.get("original_text") or "")
        )
        translated_text = normalize_glossary_text(
            str(segment.get("translated_text") or "")
        )
        occupied: list[tuple[int, int]] = []
        matches: list[tuple[str, str]] = []
        ordered_terms = sorted(
            glossary.items(),
            key=lambda item: len(normalize_glossary_text(item[0])),
            reverse=True,
        )
        for source_term, required in ordered_terms:
            normalized_source = normalize_glossary_text(source_term)
            start = source_text.find(normalized_source)
            while start >= 0:
                end = start + len(normalized_source)
                if not any(start < used_end and end > used_start for used_start, used_end in occupied):
                    occupied.append((start, end))
                    matches.append((source_term, required))
                start = source_text.find(normalized_source, start + 1)
        for source_term, required in matches:
            # Skip enforcement for invalid or malformed glossary mappings
            if not is_valid_glossary_mapping(source_term, required, target_language):
                skipped_invalid.append(
                    {"source_term": source_term, "required": required}
                )
                continue
            if normalize_glossary_text(required) not in translated_text:
                violations.append(
                    {"segment": index, "source_term": source_term, "required": required}
                )
    if skipped_invalid:
        unique_skipped = list({(s["source_term"], s["required"]) for s in skipped_invalid})
        logger.warning(
            "Glossary enforcement skipped invalid glossary entries",
            skipped_count=len(unique_skipped),
            entries=[
                {"source_term": s, "required": r, "source_language": source_language, "target_language": target_language,
                 "reason": "Malformed or invalid cross-script glossary mapping"}
                for s, r in unique_skipped
            ],
        )
    return violations


async def _persist_translation_names(
    db: Optional[Any], project_id: Optional[str], names: List[Dict[str, Any]],
    target_language: str = "",
) -> int:
    if not db or not project_id or project_id == "default_project" or not names:
        return 0
    from app.services.terminology_extractor import filter_terminology, persist_detected_terms

    return await persist_detected_terms(db, project_id, filter_terminology(names), target_lang=target_language)


async def _translate_sub_batch(
    llm: Any,
    sub_segments: List[Dict[str, Any]],
    source_lang_name: str,
    target_lang_name: str,
    job_id: str,
    batch_label: str,
    glossary: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Helper to translate a sub-batch of segments with structured IDs and targeted retries."""
    if not sub_segments:
        return []

    payload = build_numbered_dialogue_payload(sub_segments)
    numbers = [item["n"] for item in payload["lines"]]
    prompt = _translation_json_prompt(payload, source_lang_name, target_lang_name, glossary)

    parsed_map: Dict[int, str] = {}
    last_err = None
    for attempt in range(2):
        try:
            resp = await llm.generate_text(
                prompt if attempt == 0 else prompt + '\nLƯU Ý: Trả về đúng JSON {"lines":[{"n":1,"text":"..."}],"names":[]}',
                model=getattr(llm, '_resolved_model_id', None),
            )
            parsed_map, _names = parse_translation_envelope(resp)
            mapped = _ordered_translations(parsed_map, numbers, len(sub_segments))
            if mapped is not None:
                return mapped

            missing_ids = [n for n in numbers if n not in parsed_map]
            if 0 in parsed_map:
                missing_ids = [i for i in range(len(sub_segments)) if i not in parsed_map]
            if missing_ids and len(missing_ids) < max(1, len(sub_segments) // 2):
                missing_items = {
                    "lines": [item for item in payload["lines"] if item["n"] in missing_ids]
                }
                rec_prompt = (
                    f"CẢNH BÁO: Thiếu câu thoại n={missing_ids}.\n"
                    + _translation_json_prompt(
                        missing_items, source_lang_name, target_lang_name, glossary
                    )
                )
                try:
                    rec_resp = await llm.generate_text(rec_prompt, model=getattr(llm, '_resolved_model_id', None))
                    rec_map, _ = parse_translation_envelope(rec_resp)
                    for r_id, r_trans in rec_map.items():
                        if r_id in missing_ids:
                            parsed_map[r_id] = r_trans
                except Exception as ex:
                    logger.warning(f"Sub-batch {batch_label} recovery failed: {ex}")

            mapped = _ordered_translations(parsed_map, numbers, len(sub_segments))
            if mapped is not None:
                return mapped
            still_missing = [n for n in numbers if n not in parsed_map]
            last_err = f"Sub-batch length mismatch: expected {len(sub_segments)}, still missing IDs {still_missing}"
        except Exception as ex:
            last_err = str(ex)

    if len(sub_segments) > 5:
        logger.warning(f"Sub-batch {batch_label} failed ({last_err}). Splitting sub-batch of size {len(sub_segments)} into smaller halves...")
        half = len(sub_segments) // 2
        part1 = await _translate_sub_batch(llm, sub_segments[:half], source_lang_name, target_lang_name, job_id, f"{batch_label}a", glossary)
        part2 = await _translate_sub_batch(llm, sub_segments[half:], source_lang_name, target_lang_name, job_id, f"{batch_label}b", glossary)
        return part1 + part2

    raise ValueError(f"Sub-batch translation failed: {last_err}")


def is_verbatim_echo(orig_text: str, trans_text: str, source_lang: str, target_lang: str) -> bool:
    """
    Check if a translated segment is an untranslated verbatim echo of the source text.
    Handles exact string match as well as pure CJK output when translating from Chinese to non-Chinese.
    Ignores non-linguistic inputs (pure digits or punctuation).
    """
    orig_clean = (orig_text or "").strip()
    trans_clean = (trans_text or "").strip()
    if not orig_clean or not trans_clean:
        return False
    if str(source_lang).lower() == str(target_lang).lower():
        return False

    # Ignore numbers and pure punctuation (e.g. "123", "...", "?")
    has_letters_or_cjk = any(ch.isalpha() or "\u4e00" <= ch <= "\u9fff" for ch in orig_clean)
    if not has_letters_or_cjk:
        return False

    # 1. Exact string identity for linguistic text
    if orig_clean == trans_clean:
        return True

    # 2. Chinese -> Non-Chinese: output contains only CJK characters (verbatim echo)
    try:
        from app.services.terminology_extractor import is_chinese_language, is_pure_cjk
        if is_chinese_language(source_lang) and not is_chinese_language(target_lang):
            if is_pure_cjk(trans_clean):
                return True
    except Exception:
        pass

    return False


async def translate_transcript_segments(
    segments: List[Dict[str, Any]],
    source_language: str,
    target_language: str,
    job_id: str = "VT-JOB",
    llm_provider_id: str = "gemini",
    batch_size: int = 0,
    translation_model_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    project_id: Optional[str] = None,
    glossary: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Translate transcript text segments to target language using LLM Provider (Gemini / OpenAI).
    Implements per-batch retries, structured segment ID mapping, targeted missing segment recovery,
    dynamic sub-batch splitting, anti-verbatim validation safeguards, and structured audit logging.
    Raises RuntimeError on failure — NO dummy/placeholder fallbacks permitted.
    """
    if not segments:
        return segments

    if (
        glossary is None
        and db is not None
        and hasattr(db, "execute")
        and project_id
        and project_id != "default_project"
    ):
        from app.services.glossary_service import load_project_glossary

        glossary = {
            row.source_term: row.translated_term
            for row in await load_project_glossary(db, project_id)
        }
    glossary = glossary or {}

    registry = get_registry()
    settings = get_settings()
    effective_provider = llm_provider_id or settings.DEFAULT_LLM_PROVIDER
    
    primary_llm = registry.get_llm(effective_provider) or registry.get_llm("gemini")
    
    candidate_llms = []
    if primary_llm:
        candidate_llms.append(primary_llm)

    fallback_ids = []
    if effective_provider == "gemini":
        if settings.ENABLE_OPENAI_FALLBACK:
            fallback_ids.append("openai")
    elif effective_provider == "openai":
        fallback_ids.append("gemini")

    for fid in fallback_ids:
        fb_llm = registry.get_llm(fid)
        if fb_llm and fb_llm not in candidate_llms:
            candidate_llms.append(fb_llm)

    if not candidate_llms:
        raise RuntimeError("Không tìm thấy LLM Provider nào khả thi trong hệ thống.")

    # Resolve translation model ID via AIModelResolver if not explicitly provided
    if not translation_model_id:
        from app.services.model_resolver import AIModelResolver
        try:
            res_info = await AIModelResolver.resolve_model(db, capability="TRANSLATION", stage="TRANSLATE")
            translation_model_id = res_info.model_id
        except Exception as res_err:
            logger.warning(f"[{job_id}] Model resolution for TRANSLATION capability failed: {res_err}")

    # Attach resolved model ID to each LLM provider for generate_text() calls
    for llm in candidate_llms:
        llm._resolved_model_id = translation_model_id


    lang_names = {
        "vi": "Tiếng Việt",
        "vietnamese": "Tiếng Việt",
        "en": "English",
        "english": "English",
        "ja": "Tiếng Nhật",
        "japanese": "Tiếng Nhật",
        "ko": "Tiếng Hàn",
        "korean": "Tiếng Hàn",
        "zh": "Tiếng Trung",
        "chinese": "Tiếng Trung",
        "fr": "Tiếng Pháp",
        "french": "Tiếng Pháp",
        "de": "Tiếng Đức",
        "german": "Tiếng Đức",
        "es": "Tiếng Tây Ban Nha",
        "spanish": "Tiếng Tây Ban Nha",
        "auto": "Tự động",
    }
    source_lang_name = lang_names.get(str(source_language).lower(), source_language or "Tự động")
    target_lang_name = lang_names.get(str(target_language).lower(), target_language or "Tiếng Việt")

    provider_errors: List[str] = []

    for llm_idx, llm in enumerate(candidate_llms):
        is_primary = (llm_idx == 0)
        log_job_event(
            job_id,
            "TRANSLATING",
            f"[TRANSLATION_PROVIDER] job_id={job_id} | configured_provider={llm_provider_id} | "
            f"resolved_provider={llm.provider_id} | actual_provider={llm.provider_name} | "
            f"is_primary={is_primary} | source_language={source_lang_name} | "
            f"target_language={target_lang_name} | segments_count={len(segments)}"
        )

        try:
            translated_results: List[str] = []
            collected_names: List[Dict[str, Any]] = []
            chunk = len(segments) if not batch_size or batch_size < 1 else batch_size
            total_batches = (len(segments) + chunk - 1) // chunk

            for batch_idx in range(total_batches):
                start_i = batch_idx * chunk
                end_i = min(len(segments), start_i + chunk)
                batch_segments = segments[start_i:end_i]
                payload = build_numbered_dialogue_payload(batch_segments)
                numbers = [item["n"] for item in payload["lines"]]
                prompt = _translation_json_prompt(payload, source_lang_name, target_lang_name, glossary)

                translated_list = None
                batch_error = None
                parsed_map: Dict[int, str] = {}

                for attempt in range(2):
                    try:
                        curr_prompt = prompt if attempt == 0 else prompt + '\nLƯU Ý BẮT BUỘC: Trả về đúng JSON {"lines":[{"n":1,"text":"..."}],"names":[]}'
                        response_text = await llm.generate_text(curr_prompt, model=getattr(llm, '_resolved_model_id', None))
                        parsed_map, batch_names = parse_translation_envelope(response_text, target_language=target_language)
                        if batch_names:
                            collected_names.extend(batch_names)

                        mapped = _ordered_translations(parsed_map, numbers, len(batch_segments))

                        # Targeted recovery for missing segment IDs in parsed_map
                        if mapped is None:
                            missing_ids = [n for n in numbers if n not in parsed_map]
                            if 0 in parsed_map:
                                missing_ids = [i for i in range(len(batch_segments)) if i not in parsed_map]
                            if missing_ids and len(missing_ids) < max(1, len(batch_segments) // 2):
                                missing_items = {
                                    "lines": [item for item in payload["lines"] if item["n"] in missing_ids]
                                }
                                rec_prompt = (
                                    f"CẢNH BÁO: Thiếu câu thoại n={missing_ids}.\n"
                                    + _translation_json_prompt(
                                        missing_items, source_lang_name, target_lang_name, glossary
                                    )
                                )
                                try:
                                    rec_resp = await llm.generate_text(rec_prompt, model=getattr(llm, '_resolved_model_id', None))
                                    rec_map, rec_names = parse_translation_envelope(rec_resp, target_language=target_language)
                                    if rec_names:
                                        collected_names.extend(rec_names)
                                    for r_id, r_trans in rec_map.items():
                                        if r_id in missing_ids:
                                            parsed_map[r_id] = r_trans
                                    log_job_event(
                                        job_id,
                                        "TRANSLATING",
                                        f"[Gemini Recovery] Recovered missing segments. Total items now: {len(parsed_map)}/{len(batch_segments)}"
                                    )
                                except Exception as rec_err:
                                    logger.warning(f"Targeted recovery retry failed: {rec_err}")

                            mapped = _ordered_translations(parsed_map, numbers, len(batch_segments))

                        if mapped is None:
                            still_missing = [n for n in numbers if n not in parsed_map]
                            batch_error = f"Output length mismatch: expected {len(batch_segments)}, still missing IDs {still_missing}"
                            continue

                        # Audit verbatim echoes & missing text
                        echo_indices = [
                            idx for idx, (seg, trans) in enumerate(zip(batch_segments, mapped))
                            if is_verbatim_echo(seg.get("text") or seg.get("original_text") or "", trans, source_language, target_language)
                        ]
                        missing_indices = [
                            idx for idx, (seg, trans) in enumerate(zip(batch_segments, mapped))
                            if (seg.get("text") or seg.get("original_text") or "").strip() and not str(trans).strip()
                        ]
                        invalid_indices = sorted(list(set(echo_indices + missing_indices)))
                        invalid_ids = [numbers[i] for i in invalid_indices]
                        valid_count = len(batch_segments) - len(invalid_indices)

                        audit_msg = (
                            f"[Translation Audit]\n"
                            f"batch={batch_idx+1}/{total_batches}\n"
                            f"input={len(batch_segments)}\n"
                            f"output={len(mapped)}\n"
                            f"valid={valid_count}\n"
                            f"verbatim_echo={len(echo_indices)}\n"
                            f"missing={len(missing_indices)}\n"
                            f"retry_ids={invalid_ids}"
                        )
                        logger.info(audit_msg)
                        log_job_event(job_id, "TRANSLATING", audit_msg)

                        # Targeted retry: retry ONLY invalid segments (echoes + missing), preserving valid ones!
                        if invalid_indices:
                            max_echo_retries = 2
                            for echo_attempt in range(max_echo_retries):
                                if not invalid_indices:
                                    break
                                retry_payload = {
                                    "lines": [item for item in payload["lines"] if item["n"] in invalid_ids]
                                }
                                echo_in_retry = len([i for i in invalid_indices if i in echo_indices])
                                correction_prompt = (
                                    f"CẢNH BÁO DỊCH THUẬT: Có {echo_in_retry} câu thoại bị giữ nguyên tiếng gốc ({source_lang_name}) thay vì dịch sang {target_lang_name}!\n\n"
                                    f"QUY TẮC SỬA LỖI BẮT BUỘC:\n"
                                    f"1. Source language: {source_lang_name}\n"
                                    f"2. Target language: {target_lang_name}\n"
                                    f"3. BẮT BUỘC dịch toàn bộ nội dung sang {target_lang_name}. TUYỆT ĐỐI KHÔNG COPY NGUYÊN VĂN tiếng Trung/tiếng gốc.\n"
                                    f"4. Giữ nguyên ý nghĩa của câu gốc.\n"
                                    f"5. Giữ nguyên chính xác số thứ tự 'n' của từng câu ({invalid_ids}). Không thêm/bớt câu.\n"
                                    f"6. Tên riêng và thuật ngữ chỉ giữ nguyên nếu là proper term invariant hợp lệ, tuyệt đối không biến cả câu thành tiếng Trung.\n"
                                    f"7. Trả về đúng định dạng JSON envelope duy nhất:\n"
                                    f'{{"lines": [{{"n": 1, "text": "bản dịch tiếng Việt"}}], "names": []}}\n\n'
                                    f"DANH SÁCH CÁC CÂU CẦN DỊCH LẠI:\n"
                                    + _translation_json_prompt(
                                        retry_payload, source_lang_name, target_lang_name, glossary
                                    )
                                )
                                try:
                                    rec_resp = await llm.generate_text(correction_prompt, model=getattr(llm, '_resolved_model_id', None))
                                    rec_map, rec_names = parse_translation_envelope(rec_resp, target_language=target_language)
                                    if rec_names:
                                        collected_names.extend(rec_names)

                                    for pos, idx in enumerate(invalid_indices):
                                        n = numbers[idx]
                                        orig_text = batch_segments[idx].get("text") or batch_segments[idx].get("original_text") or ""
                                        cand = None
                                        if n in rec_map:
                                            cand = rec_map[n]
                                        elif pos in rec_map:
                                            cand = rec_map[pos]
                                        elif idx in rec_map:
                                            cand = rec_map[idx]

                                        if cand is not None:
                                            cand_str = str(cand).strip()
                                            if not is_verbatim_echo(orig_text, cand_str, source_language, target_language):
                                                if cand_str or not orig_text.strip():
                                                    mapped[idx] = cand_str

                                    # Re-evaluate
                                    echo_indices = [
                                        i for i, (seg, trans) in enumerate(zip(batch_segments, mapped))
                                        if is_verbatim_echo(seg.get("text") or seg.get("original_text") or "", trans, source_language, target_language)
                                    ]
                                    missing_indices = [
                                        i for i, (seg, trans) in enumerate(zip(batch_segments, mapped))
                                        if (seg.get("text") or seg.get("original_text") or "").strip() and not str(trans).strip()
                                    ]
                                    invalid_indices = sorted(list(set(echo_indices + missing_indices)))
                                    invalid_ids = [numbers[i] for i in invalid_indices]

                                    retry_log = (
                                        f"[Translation Retry]\n"
                                        f"retry_count={echo_attempt+1}\n"
                                        f"retry_input={len(retry_payload['lines'])}\n"
                                        f"retry_output={len(rec_map)}\n"
                                        f"remaining_invalid={len(invalid_indices)}"
                                    )
                                    logger.info(retry_log)
                                    log_job_event(job_id, "TRANSLATING", retry_log)
                                except Exception as rec_err:
                                    logger.warning(f"Targeted echo retry attempt {echo_attempt+1} failed: {rec_err}")

                        # If all segments are valid, finish batch successfully
                        if not invalid_indices:
                            translated_list = mapped
                            break

                        batch_error = f"Output length/echo mismatch: expected {len(batch_segments)}, still invalid IDs {invalid_ids}"
                    except Exception as ex:
                        batch_error = str(ex)
                        logger.warning(f"Batch {batch_idx+1}/{total_batches} attempt {attempt+1} failed on {llm.provider_id}: {batch_error}")

                if translated_list is None or len(translated_list) != len(batch_segments):
                    logger.warning(f"Batch {batch_idx+1}/{total_batches} full batch translation failed ({batch_error}). Triggering dynamic sub-batch splitting fallback...")
                    try:
                        if len(batch_segments) > 1:
                            half = len(batch_segments) // 2
                            part1 = await _translate_sub_batch(llm, batch_segments[:half], source_lang_name, target_lang_name, job_id, f"B{batch_idx+1}a", glossary)
                            part2 = await _translate_sub_batch(llm, batch_segments[half:], source_lang_name, target_lang_name, job_id, f"B{batch_idx+1}b", glossary)
                            translated_list = part1 + part2
                        else:
                            translated_list = await _translate_sub_batch(llm, batch_segments, source_lang_name, target_lang_name, job_id, f"B{batch_idx+1}", glossary)
                        log_job_event(job_id, "TRANSLATING", f"[Gemini Sub-batch Fallback] Successfully translated batch {batch_idx+1}/{total_batches} via sub-batch splitting.")
                    except Exception as sub_ex:
                        batch_error = f"Sub-batch splitting failed: {sub_ex}"

                if not isinstance(translated_list, list) or len(translated_list) != len(batch_segments):
                    raise ValueError(f"LLM translation failed for batch {batch_idx+1}/{total_batches} on {llm.provider_name}: {batch_error}")

                translated_results.extend([str(t).strip() for t in translated_list])
                log_job_event(job_id, "TRANSLATING", f"Translated batch {batch_idx+1}/{total_batches} via {llm.provider_name} ({len(translated_list)} items)")

            if len(translated_results) == len(segments):
                untranslated_count = 0
                for orig_s, trans_t in zip(segments, translated_results):
                    orig_txt = orig_s.get("text", "").strip()
                    trans_txt = trans_t.strip()
                    if is_verbatim_echo(orig_txt, trans_txt, source_language, target_language):
                        untranslated_count += 1

                if untranslated_count > 0:
                    err_msg = f"Translation validation failed on {llm.provider_name}: {untranslated_count}/{len(segments)} segments were verbatim echoes."
                    logger.warning(err_msg)
                    provider_errors.append(f"[{llm.provider_name}] {err_msg}")
                    continue

                for seg, trans in zip(segments, translated_results):
                    seg["translated_text"] = trans

                violations = find_glossary_violations(
                    segments, glossary,
                    source_language=source_language,
                    target_language=target_language,
                )
                if violations:
                    # Targeted retry with LLM for segments with valid glossary violations
                    log_job_event(
                        job_id,
                        "TRANSLATING",
                        f"[Glossary Enforcement] Detected {len(violations)} glossary violations on {llm.provider_name}. Attempting targeted recovery..."
                    )
                    violating_indices = sorted({v["segment"] for v in violations if 1 <= v["segment"] <= len(segments)})
                    violating_segments = [segments[idx - 1] for idx in violating_indices]
                    if violating_segments:
                        retry_payload = build_numbered_dialogue_payload(violating_segments)
                        rules_summary = "\n".join(
                            f"- '{v['source_term']}' BẮT BUỘC dịch là '{v['required']}' (câu {v['segment']})"
                            for v in violations[:10]
                        )
                        strict_retry_prompt = (
                            f"CẢNH BÁO: Bản dịch trước chưa dùng đúng thuật ngữ Glossary Canonical bắt buộc:\n"
                            f"{rules_summary}\n\n"
                            f"Dịch lại CÁC CÂU THOẠI SAU sang {target_lang_name} và BẮT BUỘC chứa chính xác các bản dịch thuật ngữ trên:\n\n"
                            + _translation_json_prompt(
                                retry_payload, source_lang_name, target_lang_name, glossary
                            )
                        )
                        try:
                            retry_resp = await llm.generate_text(strict_retry_prompt)
                            retry_map, retry_names = parse_translation_envelope(retry_resp, target_language=target_language)
                            if retry_names:
                                collected_names.extend(retry_names)
                            retry_numbers = [item["n"] for item in retry_payload["lines"]]
                            for n, seg_item in zip(retry_numbers, violating_segments):
                                if n in retry_map and retry_map[n].strip():
                                    seg_item["translated_text"] = retry_map[n].strip()
                            # Re-check violations after retry
                            violations = find_glossary_violations(
                                segments, glossary,
                                source_language=source_language,
                                target_language=target_language,
                            )
                        except Exception as retry_ex:
                            logger.warning(f"Targeted glossary retry failed: {retry_ex}")

                if violations:
                    raise RuntimeError(
                        "GLOSSARY_ENFORCEMENT_FAILED: "
                        + json.dumps(violations, ensure_ascii=False)
                    )

                saved = await _persist_translation_names(
                    db, project_id, collected_names,
                    target_language=target_language,
                )
                completed_log = (
                    f"[TRANSLATION COMPLETED]\n"
                    f"job_id={job_id}\n"
                    f"segments={len(segments)}\n"
                    f"translated={len(segments)}"
                )
                logger.info(completed_log)
                log_job_event(job_id, "TRANSLATING", completed_log)
                return segments

        except Exception as e:
            err_detail = f"[{llm.provider_name} ({llm.provider_id})] {str(e)}"
            logger.warning(err_detail)
            log_job_event(
                job_id,
                "TRANSLATING",
                f"LLM translation provider failed ({llm.provider_name}): {str(e)}. "
                f"{'Chuyển sang Provider dự phòng...' if llm_idx + 1 < len(candidate_llms) else 'Không còn Provider dự phòng nào.'}"
            )
            provider_errors.append(err_detail)

    # If all LLM providers in failover chain failed
    error_summary = " | ".join(provider_errors) if provider_errors else "Tất cả LLM Provider đều thất bại."
    raise RuntimeError(f"TRANSLATION FAILED: {error_summary}")


from app.services.video_translator.sync_service import VideoAudioSyncService

async def sync_and_stretch_audio(
    tts_audio_path: Path,
    target_duration: float,
    output_synced_path: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> float:
    """
    Adjust audio speed (time-stretch) using FFmpeg multi-stage atempo filter to match target duration.
    """
    res = await VideoAudioSyncService.stretch_and_normalize_audio(
        input_audio_path=tts_audio_path,
        target_duration=target_duration,
        output_audio_path=output_synced_path,
        job_id=job_id,
        on_progress=on_progress,
        on_pid=on_pid,
    )
    
    log_job_event(
        job_id,
        "SYNCING_AUDIO",
        f"[VIDEO-SYNC] Audio stretched/normalized: target={target_duration:.2f}s, "
        f"actual={res['actual_duration']:.2f}s, final={res['final_duration']:.2f}s, "
        f"tempo={res['tempo_applied']:.2f}x, action={res['action']}"
    )
    return res["final_duration"]


async def render_dubbed_video(
    video_path: Path,
    segments: List[VideoTranslationSegment],
    original_audio_mode: str,
    output_video_path: Path,
    work_dir: Path,
    job_id: str = "VT-JOB",
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
) -> Path:
    """
    Render final dubbed video by building a sample-accurate timeline audio track and muxing with video.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    log_job_event(job_id, "RENDERING", "[VIDEO-SYNC] Probing total video duration for timeline render...")
    total_video_duration = await probe_duration_async(video_path)

    valid_segments = [s for s in segments if s.synced_audio_path or s.tts_audio_path]
    if not valid_segments:
        raise ValueError("❌ Không có phân đoạn âm thanh lồng tiếng nào được tạo.")

    log_job_event(
        job_id,
        "RENDERING",
        f"[VIDEO-SYNC] Building PCM audio timeline for {len(valid_segments)} segments (Master duration: {total_video_duration:.2f}s)..."
    )

    segment_dicts = []
    for s in valid_segments:
        if s.end_time > total_video_duration + 0.05:
            raise ValueError(
                f"TIMELINE_INVALID: Segment #{s.segment_number} end_time ({s.end_time:.2f}s) "
                f"exceeds total video duration ({total_video_duration:.2f}s). Render aborted."
            )
        segment_dicts.append({
            "number": s.segment_number,
            "start_time": s.scheduled_start if s.scheduled_start is not None else s.start_time,
            "end_time": s.scheduled_end if s.scheduled_end is not None else s.end_time,
            "voice_id": s.voice_id,
            "schedule_action": s.schedule_action,
            "audio_path": s.synced_audio_path or s.tts_audio_path,
        })

    combined_audio_path = work_dir / "combined_dubbed_audio.wav"

    # Step 1: Assemble timeline PCM audio track with exact zero-volume-loss and silence gaps
    timeline_res = VideoAudioSyncService.build_dubbed_audio_timeline(
        segments=segment_dicts,
        total_video_duration=total_video_duration,
        output_wav_path=combined_audio_path,
        job_id=job_id,
    )

    if timeline_res.get("overlap_warnings"):
        for warn in timeline_res["overlap_warnings"]:
            logger.warning(f"[VIDEO-SYNC] Job {job_id}: {warn}")

    # Step 2: Mux combined dubbed audio timeline with original video
    rendered_path = await VideoAudioSyncService.render_and_mux_video(
        video_path=video_path,
        dubbed_audio_path=combined_audio_path,
        original_audio_mode=original_audio_mode,
        output_video_path=output_video_path,
        total_video_duration=total_video_duration,
        job_id=job_id,
        on_progress=on_progress,
        on_pid=on_pid,
    )

    # Step 3: Validate final output duration and audio track
    val_res = await VideoAudioSyncService.validate_output(
        output_video_path=rendered_path,
        source_video_duration=total_video_duration,
    )

    log_job_event(
        job_id,
        "VALIDATION",
        f"[VIDEO-SYNC] Validation passed: Duration={val_res['output_duration']:.2f}s (Diff={val_res['duration_diff']}s), "
        f"Resolution={val_res['width']}x{val_res['height']}, HasAudio={val_res['has_audio']}"
    )

    return rendered_path
