"""
Thumbnail Service — AI Content Analysis, Visual Prompt Generator, Image Synthesis,
and Storage Management for Video Thumbnails.
"""

from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core import get_logger
from app.models.video_thumbnail import VideoThumbnail, ThumbnailStatus
from app.models.project import Project
from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
from app.providers.registry import get_registry
from app.providers.base import ImageProvider
from app.services.key_manager import get_key_manager
from app.services.storage_service import storage_service

logger = get_logger(__name__)
settings = get_settings()


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
    ) -> Dict[str, Any]:
        """Use LLM (Gemini or OpenAI via KeyManager) to generate structured content analysis."""
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

        registry = get_registry()
        llm_provider = registry.get_llm("gemini") or registry.get_llm("openai")

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
            logger.warning("LLM content analysis parsing failed, using fallback", error=str(ex))
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
    ) -> VideoThumbnail:
        """
        Full End-to-End AI Auto Thumbnail Generation Workflow.
        """
        title = "Untitled Video"
        description = ""
        transcript_text = ""
        source_lang = "auto"
        target_lang = "vi"

        # Check existing generating status to prevent duplicate jobs
        existing_stmt = select(VideoThumbnail).where(
            VideoThumbnail.status.in_([ThumbnailStatus.ANALYZING.value, ThumbnailStatus.GENERATING_IMAGE.value]),
        )
        if project_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.project_id == project_id)
        elif job_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.job_id == job_id)
        elif asset_id:
            existing_stmt = existing_stmt.where(VideoThumbnail.asset_id == asset_id)

        existing_res = await db.execute(existing_stmt)
        if existing_res.scalar_one_or_none():
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
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        try:
            # 2. Intelligent transcript chunking & AI Content Analysis
            cleaned = cls.clean_transcript(transcript_text)
            chunks = cls.chunk_transcript(cleaned)
            summary_context = "\n".join(chunks[:3]) if chunks else title

            logger.info("[THUMBNAIL] Starting AI Content Analysis", thumbnail_id=thumbnail_id, title=title)
            analysis = await cls.analyze_content_with_llm(
                title=title,
                description=description,
                transcript_summary=summary_context,
                source_lang=source_lang,
                target_lang=target_lang,
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

            registry = get_registry()
            target_provider_id = provider_id or "pollinations"
            img_provider: Optional[ImageProvider] = registry.get_image(target_provider_id)

            if not img_provider:
                img_provider = registry.get_image("pollinations") or registry.get_image("local_image")

            if not img_provider:
                raise RuntimeError("No suitable AI Image Provider found.")

            # Retry loop (max 2 retries)
            max_retries = 2
            gen_res = None
            for attempt in range(max_retries + 1):
                gen_res = await img_provider.generate_image(
                    prompt=prompt,
                    width=1280,
                    height=720,
                    aspect_ratio="16:9",
                    model=model_id or "default",
                )
                if gen_res.success:
                    break
                logger.warning(
                    f"[THUMBNAIL] Generation attempt {attempt + 1} failed",
                    provider=img_provider.provider_id,
                    error=gen_res.error_message,
                )
                await asyncio.sleep(1.5)

            if not gen_res or not gen_res.success or not gen_res.metadata.get("image_bytes"):
                # Fallback to local image provider if primary provider failed
                fallback_provider = registry.get_image("local_image")
                if fallback_provider:
                    logger.info("[THUMBNAIL] Retrying with local image fallback provider")
                    gen_res = await fallback_provider.generate_image(prompt=prompt, width=1280, height=720)

            if not gen_res or not gen_res.success or not gen_res.metadata.get("image_bytes"):
                err_text = gen_res.error_message if gen_res else "Image generation timeout or failure"
                record.status = ThumbnailStatus.FAILED.value
                record.error_message = err_text
                await db.commit()
                return record

            image_bytes = gen_res.metadata["image_bytes"]

            # 5. Upload image to Storage (Cloudflare R2 / Supabase Storage)
            record.status = ThumbnailStatus.UPLOADING.value
            await db.commit()

            tmp_dir = settings.DATA_DIR / "temp_thumbnails"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            tmp_file = tmp_dir / f"thumb_{thumbnail_id}.webp"
            tmp_file.write_bytes(image_bytes)

            timestamp = int(datetime.now(timezone.utc).timestamp())
            if project_id:
                object_key = f"projects/{project_id}/thumbnails/thumbnail_{timestamp}.webp"
            elif job_id:
                object_key = f"translator/jobs/{job_id}/thumbnails/thumbnail_{timestamp}.webp"
            else:
                object_key = f"translator/assets/{asset_id}/thumbnails/thumbnail_{timestamp}.webp"

            r2_key, public_url = await storage_service.upload_file(
                local_path=tmp_file,
                object_key=object_key,
                content_type="image/webp",
                is_public=True,
            )

            # Cleanup temp local file
            if tmp_file.exists():
                tmp_file.unlink()

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
            record.provider = img_provider.provider_id

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
            logger.info("[THUMBNAIL] Successfully completed thumbnail generation", thumbnail_id=thumbnail_id, url=public_url)
            return record

        except Exception as ex:
            logger.error("[THUMBNAIL] Critical failure during generation", error=str(ex))
            record.status = ThumbnailStatus.FAILED.value
            record.error_message = str(ex)
            await db.commit()
            return record

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
