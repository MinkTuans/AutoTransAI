"""
Thumbnail Service — AI Content Analysis, Visual Prompt Generator, Image Synthesis,
and Storage Management for Video Thumbnails.
"""

from __future__ import annotations

import json
import re
import uuid
import asyncio
from io import BytesIO
from math import gcd
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from PIL import Image
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.core import get_logger
from app.models.video_thumbnail import VideoThumbnail, ThumbnailStatus
from app.models.project import Project
from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
from app.models import APIKey, CatalogModel, CatalogRefreshRun
from app.models.settings import AIFunctionConfig
from app.providers.registry import get_registry
from app.providers.base import GenerationResult, ImageProvider
from app.providers.image.catalog_media import CatalogImageError, validate_image_bytes
from app.services.storage_service import storage_service
from app.services.ai_routing import (
    RouteConfigurationError, RouteExhausted, RoutePending, RouteTarget, UnsupportedModalityError,
    build_route, classify_failure, invoke_route,
)
from app.services.video_editor.catalog_llm import InvalidEditorOutput, generate_catalog_json

logger = get_logger(__name__)
settings = get_settings()
_IMAGE_FORMATS = {"PNG": (".png", "image/png"), "JPEG": (".jpg", "image/jpeg"),
                  "WEBP": (".webp", "image/webp")}


class _ThumbnailImageFailure(Exception):
    """Classified provider failure without raw upstream text."""

    def __init__(self, result: GenerationResult):
        code = result.error_code if isinstance(result.error_code, str) else ""
        status = code.removeprefix("HTTP_")
        self.status_code = int(status) if code.startswith("HTTP_") and status.isdigit() else None
        self.code = "invalid_output" if code == "INVALID_OUTPUT" else "provider_unavailable"
        super().__init__("Image generation failed")


class AIThumbnailAnalysis(BaseModel):
    """Structured Pydantic validation schema for LLM content analysis."""
    title: str = Field(default="Untitled Video")
    main_subject: str = Field(default="Main subject of the video")
    main_character: str = Field(default="Key character or object")
    main_event: str = Field(default="Key action or discovery")
    main_conflict: str = Field(default="Dramatic tension or intrigue")
    emotion: str = Field(default="Mysterious and dramatic")
    environment: str = Field(default="Cinematic visual setting")
    important_visual_elements: List[str] = Field(default_factory=list)
    thumbnail_hook: str = Field(default="Visual hook showing dramatic moment")


STYLE_PROMPT_PRESETS: Dict[str, str] = {
    "auto": "Cinematic dramatic lighting, high contrast visual storytelling, expressive focal subject, 16:9 composition.",
    "cinematic": "Dramatic cinematic lighting, 35mm film lens, anamorphic depth of field, vivid contrast, photorealistic cinematic scene.",
    "youtube_viral": "High contrast vibrant YouTube viral thumbnail style, intense facial emotional expression, bright bold primary lighting, clear single focal point, optimized for small display size.",
    "horror": "Dark eerie atmospheric horror scene, dramatic dark shadows, mysterious suspenseful lighting, creepy tension.",
    "anime": "High quality Japanese anime art style, vibrant vivid colors, expressive cel shading, dynamic anime key visual.",
    "realistic": "Photorealistic 8K photography, natural realistic lighting, sharp fine details, high dynamic range.",
    "cartoon": "3D animated cartoon character style, warm expressive lighting, stylized 3D digital art.",
    "documentary": "Dramatic photojournalism style, authentic documentary atmosphere, natural dramatic contrast.",
    "minimal": "Clean minimalist visual layout, bold striking subject focus, high contrast graphic aesthetic.",
    "movie_poster": "Epic Hollywood movie poster composition, dramatic rim light key art style, intense cinematic hook.",
}


class ThumbnailService:
    """Service servicing AI Auto Thumbnail Generation pipeline."""

    @staticmethod
    def clean_transcript(raw_text: str) -> str:
        """Clean transcript text by removing line numbers, redundant spaces, and tags."""
        if not raw_text:
            return ""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return " ".join(lines)

    @staticmethod
    def chunk_transcript(cleaned_text: str, chunk_size: int = 2500) -> List[str]:
        """Split long transcript into manageable chunks for AI analysis."""
        if len(cleaned_text) <= chunk_size:
            return [cleaned_text]
        chunks = []
        for i in range(0, len(cleaned_text), chunk_size):
            chunks.append(cleaned_text[i: i + chunk_size])
        return chunks

    @classmethod
    async def analyze_content_with_llm(
        cls,
        title: str,
        description: str,
        transcript_summary: str,
        source_lang: str = "auto",
        target_lang: str = "vi",
        *,
        sessions: async_sessionmaker[AsyncSession] | None = None,
        data_dir: Path | None = None,
    ) -> Dict[str, Any]:
        """Analyze with the catalog LLM route, retaining the unmigrated legacy path."""
        system_prompt = (
            "You are an expert YouTube Thumbnail Director and Content Analyst. "
            "Analyze the video title, description, and transcript summary to extract core visual storytelling elements. "
            "Respond ONLY with valid JSON matching this schema:\n"
            "{\n"
            '  "title": "string",\n'
            '  "main_subject": "string",\n'
            '  "main_character": "string",\n'
            '  "main_event": "string",\n'
            '  "main_conflict": "string",\n'
            '  "emotion": "string",\n'
            '  "environment": "string",\n'
            '  "important_visual_elements": ["string"],\n'
            '  "thumbnail_hook": "string"\n'
            "}"
        )

        user_prompt = (
            f"Video Title: {title}\n"
            f"Description: {description or 'N/A'}\n"
            f"Source Language: {source_lang}, Target Language: {target_lang}\n"
            f"Transcript Content:\n{transcript_summary[:3000]}\n"
        )

        fallback_analysis = {
            "title": title,
            "main_subject": title,
            "main_character": "Main subject",
            "main_event": title,
            "main_conflict": "Dynamic visual story",
            "emotion": "Dramatic and suspenseful",
            "environment": "Cinematic visual environment",
            "important_visual_elements": [title],
            "thumbnail_hook": f"Visual scene representing {title}",
        }

        def validate(parsed: dict) -> dict:
            for name in ("title", "main_subject", "main_event", "thumbnail_hook"):
                value = parsed.get(name)
                if not isinstance(value, str) or not value.strip() or len(value) > 500:
                    raise InvalidEditorOutput() from None
            elements = parsed.get("important_visual_elements", [])
            if (not isinstance(elements, list) or len(elements) > 30
                    or any(not isinstance(item, str) or len(item) > 200 for item in elements)):
                raise InvalidEditorOutput() from None
            return AIThumbnailAnalysis(**parsed).model_dump()

        catalog_analysis = await generate_catalog_json(
            sessions=sessions, data_dir=data_dir,
            prompt_prefix=system_prompt + "\n", transcript=user_prompt,
            prompt_suffix="", validate=validate,
        )
        if catalog_analysis is not None:
            return catalog_analysis

        registry = get_registry()
        llm_provider = registry.get_llm("gemini") or registry.get_llm("openai")
        if not llm_provider:
            return fallback_analysis

        try:
            raw_response = await llm_provider.generate_text(user_prompt, system_prompt=system_prompt)
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.replace("```json", "").replace("```", "").strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json.replace("```", "").strip()

            parsed = json.loads(clean_json)
            validated = AIThumbnailAnalysis(**parsed)
            return validated.model_dump()
        except Exception as ex:
            logger.warning("LLM content analysis parsing failed, using fallback", code=classify_failure(ex))
            return fallback_analysis

    @classmethod
    def generate_image_prompt(
        cls,
        analysis: Dict[str, Any],
        selected_style: str = "auto",
        custom_instruction: Optional[str] = None,
    ) -> str:
        """Craft an optimized visual storytelling image prompt for AI image generation."""
        style_preset = STYLE_PROMPT_PRESETS.get(selected_style.lower(), STYLE_PROMPT_PRESETS["auto"])

        subject = analysis.get("main_subject") or analysis.get("title") or "Dynamic focal character"
        character = analysis.get("main_character") or "Expressive character"
        event = analysis.get("main_event") or "Dramatic scene"
        emotion = analysis.get("emotion") or "Intense emotion"
        environment = analysis.get("environment") or "Detailed environment"
        hook = analysis.get("thumbnail_hook") or "Visual storyline hook"

        base_prompt = (
            f"Create a high quality 16:9 video thumbnail showing {subject}. "
            f"The scene features {character} during {event}. "
            f"Visual atmosphere: {environment}. Emotional feeling: {emotion}. "
            f"Core visual hook: {hook}. "
            f"Style direction: {style_preset}"
        )

        if custom_instruction and custom_instruction.strip():
            # Validate and truncate user instruction (max 500 chars)
            safe_instruction = custom_instruction.strip()[:500]
            base_prompt += f" User instructions: {safe_instruction}."

        base_prompt += " Clear single focal point, strong visual storytelling, expressive emotion, 16:9 aspect ratio. No text, no watermark, no logo."
        return base_prompt

    @staticmethod
    async def _catalog_image_route(sessions: async_sessionmaker[AsyncSession] | None):
        if sessions is None:
            return None
        async with sessions() as catalog_db:
            config = await catalog_db.get(AIFunctionConfig, "image_generation")
            await catalog_db.scalar(select(CatalogRefreshRun.id).limit(1))
            # Seeded legacy Pollinations config remains untouched until Task 9
            # imports a system catalog row and migrates the default to its ID.
            if (config and config.primary_provider_id == "pollinations"
                    and config.model_id in ("pollinations-default", "default")):
                return None
            selected = (await catalog_db.get(CatalogModel, config.model_id)
                        if config and config.model_id else None)
            model = await catalog_db.scalar(select(CatalogModel.id).where(
                CatalogModel.source != "system",
                CatalogModel.provider_id.in_(("openai", "fal")),
            ).limit(1))
            key = await catalog_db.scalar(select(APIKey.id).where(
                APIKey.provider_id.in_(("openai", "fal")),
            ).limit(1))
            if selected is None and model is None and key is None:
                return None
            if config is None or not config.model_id:
                raise RouteConfigurationError("Image generation default is not configured.")
            return await build_route(catalog_db, "IMAGE_GENERATION")

    @staticmethod
    async def _catalog_image_result(route, prompt: str, sessions, data_dir: Path,
                                    attempted: list[RouteTarget]):
        registry = get_registry()

        async def transport(target: RouteTarget, secret: str | None):
            attempted[:] = [target]
            provider = registry.get_image(target.provider_id)
            if provider is None:
                raise UnsupportedModalityError("Image adapter is unavailable.")
            kwargs = {"prompt": prompt, "width": 1280, "height": 720, "aspect_ratio": "16:9"}
            if target.access_scope == "keyless":
                if target.provider_id not in ("pollinations", "local_image"):
                    raise UnsupportedModalityError("Unsupported keyless image adapter.")
                # System Pollinations catalog identity is a service sentinel,
                # not a paid remote model identifier.
                model = ("default" if target.provider_id == "pollinations"
                         and target.remote_model_id == "pollinations-default"
                         else target.remote_model_id)
                result = await provider.generate_image(**kwargs, model=model)
            elif target.provider_id in ("openai", "fal"):
                result = await provider.generate_image(**kwargs, route_target=target, api_key=secret)
            else:
                raise UnsupportedModalityError("Unsupported image adapter.")
            if not result.success:
                raise _ThumbnailImageFailure(result)
            content = result.metadata.get("image_bytes")
            if not isinstance(content, bytes):
                raise CatalogImageError("invalid_output")
            validate_image_bytes(content)
            return result, target

        return await invoke_route(route, transport, sessions, data_dir,
                                  max_attempts=1, timeout=150.0)

    @classmethod
    async def create_thumbnail(
        cls,
        db: AsyncSession,
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        selected_style: str = "auto",
        custom_instruction: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        *,
        sessions: async_sessionmaker[AsyncSession] | None = None,
        data_dir: Path | None = None,
        historical_selection_hint: bool = False,
    ) -> VideoThumbnail:
        """
        Full End-to-End AI Auto Thumbnail Generation Workflow.
        """
        title = "Untitled Video"
        description = ""
        transcript_text = ""
        source_lang = "auto"
        target_lang = "vi"

        # These identifiers become storage path components; imported rows may not be UUIDs.
        if not any((project_id, job_id, asset_id)) or any(
            value is not None and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value) is None
            for value in (project_id, job_id, asset_id)
        ):
            raise ValueError("Invalid thumbnail target identifier.")

        # Check existing generating status to prevent duplicate jobs
        existing_stmt = select(VideoThumbnail).where(
            VideoThumbnail.status.in_([ThumbnailStatus.ANALYZING.value,
                                       ThumbnailStatus.GENERATING_PROMPT.value,
                                       ThumbnailStatus.GENERATING_IMAGE.value,
                                       ThumbnailStatus.UPLOADING.value,
                                       ThumbnailStatus.PROVIDER_PENDING.value]),
        )
        if project_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.project_id == project_id)
        elif job_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.job_id == job_id)
        elif asset_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.asset_id == asset_id)

        existing_res = await db.execute(existing_stmt.limit(1))
        if existing_res.scalars().first():
            raise ValueError("Thumbnail generation is already in progress for this video.")

        # 1. Fetch metadata & transcript content
        if project_id:
            p_stmt = select(Project).where(Project.id == project_id)
            p_res = await db.execute(p_stmt)
            proj = p_res.scalar_one_or_none()
            if not proj:
                raise ValueError(f"Project '{project_id}' not found.")
            title = proj.title or title
            transcript_text = proj.script_raw or ""

        elif job_id:
            j_stmt = select(VideoTranslationJob).where(VideoTranslationJob.id == job_id)
            j_res = await db.execute(j_stmt)
            job = j_res.scalar_one_or_none()
            if not job:
                raise ValueError(f"Job '{job_id}' not found.")

            source_lang = job.source_language or source_lang
            target_lang = job.target_language or target_lang

            if job.asset:
                title = job.asset.title or title
                asset_id = job.asset_id

            # Fetch segments
            s_stmt = (
                select(VideoTranslationSegment)
                .where(VideoTranslationSegment.job_id == job_id)
                .order_by(VideoTranslationSegment.segment_number)
            )
            s_res = await db.execute(s_stmt)
            segments = s_res.scalars().all()
            if segments:
                transcript_text = " ".join(
                    [seg.translated_text or seg.original_text for seg in segments if (seg.translated_text or seg.original_text)]
                )

        elif asset_id:
            a_stmt = select(VideoAsset).where(VideoAsset.id == asset_id)
            a_res = await db.execute(a_stmt)
            asset = a_res.scalar_one_or_none()
            if not asset:
                raise ValueError(f"Video asset '{asset_id}' not found.")
            title = asset.title or title

        # Initial database record creation
        thumbnail_id = str(uuid.uuid4())
        record = VideoThumbnail(
            id=thumbnail_id,
            project_id=project_id,
            job_id=job_id,
            asset_id=asset_id,
            source_title=title,
            source_description=description,
            selected_style=selected_style,
            custom_instruction=custom_instruction,
            provider=provider_id or "pollinations",
            model=model_id or "default",
            status=ThumbnailStatus.ANALYZING.value,
            is_active=False,
        )
        db.add(record)
        await db.commit()

        attempted: list[RouteTarget] = []
        try:
            # 2. Intelligent transcript chunking & AI Content Analysis
            cleaned = cls.clean_transcript(transcript_text)
            chunks = cls.chunk_transcript(cleaned)
            summary_context = "\n".join(chunks[:3]) if chunks else title

            logger.info("[THUMBNAIL] Starting AI Content Analysis", thumbnail_id=thumbnail_id)
            analysis = await cls.analyze_content_with_llm(
                title=title,
                description=description,
                transcript_summary=summary_context,
                source_lang=source_lang,
                target_lang=target_lang,
                sessions=sessions,
                data_dir=data_dir,
            )

            # 3. Generate Visual Image Prompt
            record.status = ThumbnailStatus.GENERATING_PROMPT.value
            record.ai_analysis_json = json.dumps(analysis, ensure_ascii=False)
            prompt = cls.generate_image_prompt(
                analysis=analysis,
                selected_style=selected_style,
                custom_instruction=custom_instruction,
            )
            record.generated_prompt = prompt
            await db.commit()
            logger.info("[THUMBNAIL] Prompt generated", thumbnail_id=thumbnail_id, prompt_len=len(prompt))

            # 4. AI Image Generation
            record.status = ThumbnailStatus.GENERATING_IMAGE.value
            await db.commit()

            route = await cls._catalog_image_route(sessions)
            if route is not None:
                configured_target = route.targets[0]
                legacy_hint = (historical_selection_hint or
                               (provider_id == "pollinations"
                                and model_id in (None, "default", "pollinations-default")))
                if ((provider_id is not None and provider_id != configured_target.provider_id
                     and not legacy_hint)
                        or (model_id not in (None, "default", configured_target.model_id,
                                             configured_target.remote_model_id) and not legacy_hint)):
                    raise RouteConfigurationError("Explicit thumbnail model differs from the configured image default.")
                gen_res, selected_target = await cls._catalog_image_result(
                    route, prompt, sessions, data_dir or settings.DATA_DIR, attempted,
                )
                actual_provider = selected_target.provider_id
                actual_model = selected_target.remote_model_id
            else:
                registry = get_registry()
                target_provider_id = provider_id or "pollinations"
                img_provider: Optional[ImageProvider] = registry.get_image(target_provider_id)
                if not img_provider:
                    img_provider = registry.get_image("pollinations") or registry.get_image("local_image")
                if not img_provider:
                    raise RuntimeError("No suitable AI Image Provider found.")
                gen_res = None
                for attempt in range(3):
                    gen_res = await img_provider.generate_image(
                        prompt=prompt, width=1280, height=720,
                        aspect_ratio="16:9", model=model_id or "default",
                    )
                    if gen_res.success or img_provider.requires_api_key:
                        break
                    logger.warning("[THUMBNAIL] Legacy image attempt failed",
                                   provider=img_provider.provider_id, code=classify_failure(
                                       _ThumbnailImageFailure(gen_res)))
                    await asyncio.sleep(1.5)
                if not gen_res or not gen_res.success or not gen_res.metadata.get("image_bytes"):
                    fallback_provider = registry.get_image("local_image")
                    if fallback_provider:
                        logger.info("[THUMBNAIL] Retrying with local image fallback provider")
                        gen_res = await fallback_provider.generate_image(prompt=prompt, width=1280, height=720)
                        img_provider = fallback_provider
                if not gen_res or not gen_res.success or not gen_res.metadata.get("image_bytes"):
                    raise _ThumbnailImageFailure(gen_res or GenerationResult(False))
                actual_provider = img_provider.provider_id
                actual_model = gen_res.metadata.get("model") or model_id or "default"

            image_bytes = validate_image_bytes(gen_res.metadata["image_bytes"])
            with Image.open(BytesIO(image_bytes)) as decoded:
                width, height = decoded.size
                ext, mime = _IMAGE_FORMATS[decoded.format]

            # 5. Upload image to Storage (Cloudflare R2 / Supabase Storage)
            record.status = ThumbnailStatus.UPLOADING.value
            await db.commit()

            tmp_dir = settings.DATA_DIR / "temp_thumbnails"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            tmp_file = tmp_dir / f"thumb_{thumbnail_id}{ext}"
            timestamp = int(datetime.now(timezone.utc).timestamp())
            if project_id:
                object_key = f"projects/{project_id}/thumbnails/thumbnail_{timestamp}{ext}"
            elif job_id:
                object_key = f"translator/jobs/{job_id}/thumbnails/thumbnail_{timestamp}{ext}"
            else:
                object_key = f"translator/assets/{asset_id}/thumbnails/thumbnail_{timestamp}{ext}"

            try:
                tmp_file.write_bytes(image_bytes)
                r2_key, public_url = await storage_service.upload_file(
                    local_path=tmp_file, object_key=object_key,
                    content_type=mime, is_public=True,
                )
            finally:
                tmp_file.unlink(missing_ok=True)

            # 6. Deactivate old thumbnails & mark current active
            deact_stmt = update(VideoThumbnail).values(is_active=False)
            if project_id:
                deact_stmt = deact_stmt.where(VideoThumbnail.project_id == project_id)
            elif job_id:
                deact_stmt = deact_stmt.where(VideoThumbnail.job_id == job_id)
            elif asset_id:
                deact_stmt = deact_stmt.where(VideoThumbnail.asset_id == asset_id)

            await db.execute(deact_stmt)

            record.r2_key = r2_key
            record.thumbnail_url = public_url
            record.status = ThumbnailStatus.COMPLETED.value
            record.is_active = True
            record.provider = actual_provider
            record.model = actual_model
            record.width = width
            record.height = height
            divisor = gcd(width, height)
            record.aspect_ratio = f"{width // divisor}:{height // divisor}"

            # Update parent entity direct thumbnail references
            if project_id:
                await db.execute(
                    update(Project)
                    .where(Project.id == project_id)
                    .values(thumbnail_url=public_url, thumbnail_r2_key=r2_key)
                )
            if job_id:
                await db.execute(
                    update(VideoTranslationJob)
                    .where(VideoTranslationJob.id == job_id)
                    .values(thumbnail_url=public_url, thumbnail_r2_key=r2_key)
                )
            if asset_id:
                await db.execute(
                    update(VideoAsset)
                    .where(VideoAsset.id == asset_id)
                    .values(thumbnail_url=public_url, thumbnail_r2_key=r2_key)
                )

            await db.commit()
            await db.refresh(record)
            logger.info("[THUMBNAIL] Successfully completed thumbnail generation", thumbnail_id=thumbnail_id)
            return record

        except RoutePending:
            record.status = ThumbnailStatus.PROVIDER_PENDING.value
            record.error_message = "Image provider accepted the request; completion is not yet confirmed."
            if attempted:
                record.provider = attempted[0].provider_id
                record.model = attempted[0].remote_model_id
            await db.commit()
            return record
        except Exception as ex:
            code = classify_failure(ex)
            logger.error("[THUMBNAIL] Generation failed", code=code)
            record.status = ThumbnailStatus.FAILED.value
            record.error_message = (str(ex) if isinstance(ex, (RouteConfigurationError, RouteExhausted))
                                    else f"Thumbnail generation failed: {code}")
            await db.commit()
            return record

    @classmethod
    def snapshot_wants_thumbnail(cls, snapshot: Optional[Dict[str, Any]]) -> bool:
        """Studio checkbox `Tự Động Tạo Thumbnail AI` stored on the Auto job snapshot."""
        if not snapshot:
            return False
        raw = snapshot.get("thumbnail_enabled")
        if isinstance(raw, str):
            return raw.strip().lower() in ("true", "1", "yes", "on")
        return bool(raw)

    @classmethod
    async def maybe_generate_for_job(
        cls, db: Optional[AsyncSession], job: VideoTranslationJob, *,
        sessions: async_sessionmaker[AsyncSession] | None = None,
        data_dir: Path | None = None,
    ) -> Dict[str, Any]:
        """Used by Studio Auto after render. No-op when the checkbox was off."""
        snap: Dict[str, Any] = {}
        raw_json = getattr(job, "settings_snapshot_json", None)
        if raw_json:
            try:
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict):
                    snap = parsed
            except json.JSONDecodeError:
                snap = {}
        if not cls.snapshot_wants_thumbnail(snap):
            return {"generated": False, "reason": "disabled"}

        source = str(snap.get("thumbnail_source") or "ai").strip().lower()
        if source == "library":
            picked = Path(str(snap.get("thumbnail_library_path") or ""))
            if not picked.is_file():
                return {"generated": False, "error": "Chưa chọn ảnh có sẵn trong thư mục dự án."}
            root = settings.STORAGE_ROOT.resolve()
            try:
                rel = picked.resolve().relative_to(root)
                url = f"/api/storage/files/{rel.as_posix()}"
            except Exception:
                url = f"/api/storage/files/{picked.as_posix()}"
            return {"generated": True, "source": "library", "thumbnail_url": url}

        if db is None:
            return {"generated": False, "error": "no db session"}
        record = await cls.create_thumbnail(
            db=db,
            project_id=getattr(job, "project_id", None),
            job_id=getattr(job, "id", None),
            asset_id=getattr(job, "asset_id", None),
            selected_style=snap.get("thumbnail_style") or "auto",
            custom_instruction=snap.get("thumbnail_custom_instruction") or None,
            provider_id=snap.get("thumbnail_provider") or "pollinations",
            sessions=sessions,
            data_dir=data_dir,
        )
        url = getattr(record, "thumbnail_url", None)
        return {
            "generated": bool(url),
            "thumbnail_url": url,
            "status": getattr(record, "status", None),
            "error": getattr(record, "error_message", None),
        }

    @classmethod
    async def delete_thumbnail(cls, db: AsyncSession, thumbnail_id: str) -> bool:
        """Delete thumbnail record and purge storage object."""
        stmt = select(VideoThumbnail).where(VideoThumbnail.id == thumbnail_id)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            return False

        if record.r2_key:
            try:
                await storage_service.delete_file(record.r2_key, is_public=True)
            except Exception as ex:
                logger.warning("Failed deleting R2 object for thumbnail", error=str(ex), r2_key=record.r2_key)

        await db.delete(record)
        await db.commit()
        return True
