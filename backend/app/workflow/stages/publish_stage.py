"""Stage 6: Publish Stage — SEO generation, thumbnail selection, user approval, YouTube publishing with OAuth credential enforcement."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.workflow.workflow_context import WorkflowContext
from app.config import get_settings

logger = logging.getLogger(__name__)


class PublishStage:
    """Stage 6: Generate metadata, prepare YouTube upload, check OAuth credentials, and record publication status."""

    STAGE_NAME = "PUBLISH"
    STEPS = [
        "generate_seo",
        "select_thumbnail",
        "user_approval",
        "schedule_publish",
        "publish_youtube",
        "save_publication_record",
    ]

    async def execute_step(self, step_name: str, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        """Execute an individual step within Stage 6."""
        logger.info(f"[Stage PUBLISH] Executing step: {step_name}")

        if step_name == "generate_seo":
            return await self._generate_seo(ctx)
        elif step_name == "select_thumbnail":
            return await self._select_thumbnail(ctx)
        elif step_name == "user_approval":
            return await self._user_approval(ctx)
        elif step_name == "schedule_publish":
            return await self._schedule_publish(ctx)
        elif step_name == "publish_youtube":
            return await self._publish_youtube(ctx, db)
        elif step_name == "save_publication_record":
            return await self._save_publication_record(ctx, db)
        else:
            raise ValueError(f"Unknown step in PUBLISH stage: {step_name}")

    async def run_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Validate Stage 6 output requirements."""
        issues = []
        if ctx.publication_status == "PUBLISHING_BLOCKED":
            issues.append(ctx.publication_record.get("reason", "YouTube OAuth credentials are not configured."))

        passed = len(issues) == 0
        return {
            "stage": self.STAGE_NAME,
            "passed": passed,
            "issues": issues,
            "metrics": {
                "publication_status": ctx.publication_status,
                "seo_title": ctx.seo_metadata.get("title"),
            },
        }

    async def _generate_seo(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_editor.youtube_service import YouTubePublishingService
        seo = await YouTubePublishingService.generate_youtube_seo_metadata(
            transcript_text=ctx.raw_transcript or "",
            target_language=ctx.target_language,
        )
        ctx.seo_metadata = seo
        return seo

    async def _select_thumbnail(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Select or generate AI thumbnail for publication."""
        from app.services.thumbnail_service import ThumbnailService
        from app.database import async_session_factory
        
        thumbnail_url = getattr(ctx, "thumbnail_url", None)
        if not thumbnail_url and ctx.project_id:
            try:
                async with async_session_factory() as session:
                    record = await ThumbnailService.create_thumbnail(
                        db=session,
                        project_id=ctx.project_id,
                        selected_style="auto",
                    )
                    if record and record.thumbnail_url:
                        thumbnail_url = record.thumbnail_url
                        ctx.thumbnail_url = thumbnail_url
            except Exception as e:
                logger.warning(f"[PublishStage] Thumbnail auto-generation bypassed: {str(e)}")

        return {
            "thumbnail_selected": thumbnail_url or "default",
            "thumbnail_url": thumbnail_url,
        }


    async def _user_approval(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"user_approved": True}

    async def _schedule_publish(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"scheduled": False}

    async def _publish_youtube(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        settings = get_settings()
        
        # Check OAuth credentials explicitly
        if not getattr(settings, "YOUTUBE_CLIENT_ID", None) or not getattr(settings, "YOUTUBE_CLIENT_SECRET", None):
            ctx.publication_status = "PUBLISHING_BLOCKED"
            ctx.publication_record = {
                "status": "PUBLISHING_BLOCKED",
                "reason": "YouTube OAuth credentials are not configured.",
                "simulation": False,
            }
            logger.warning("[PublishStage] YouTube publishing blocked: OAuth credentials not configured.")
            return ctx.publication_record

        # Delegate to real YouTube API publish service if configured
        from app.services.video_editor.youtube_service import YouTubePublishingService
        from app.models.video_editor import YouTubeChannel
        import sqlalchemy as sa
        
        active_channel = None
        if db is not None:
            stmt = sa.select(YouTubeChannel).where(YouTubeChannel.is_active == True)
            result = await db.execute(stmt)
            active_channel = result.scalars().first()
        
        if not active_channel:
            ctx.publication_status = "PUBLISHING_BLOCKED"
            ctx.publication_record = {
                "status": "PUBLISHING_BLOCKED",
                "reason": "YouTube OAuth credentials are not configured or no active YouTube channel linked.",
                "simulation": False,
            }
            logger.warning("[PublishStage] YouTube publishing blocked: No active channel connected.")
            return ctx.publication_record

        # Create a DB upload record and start async
        from app.models.video_editor import YouTubePublication, PublishStatusEnum
        import uuid
        import json
            
        pub = YouTubePublication(
            id=str(uuid.uuid4()),
            job_id=getattr(ctx, "job_id", None),
            project_id=ctx.project_id,
            channel_id=active_channel.id,
            title=ctx.seo_metadata.get("title", "Dubbed Video"),
            description=ctx.seo_metadata.get("description", ""),
            tags_json=json.dumps(ctx.seo_metadata.get("tags", [])),
            category_id=ctx.seo_metadata.get("category_id", "22"),
            privacy_status="private",
            status=PublishStatusEnum.PENDING.value,
            progress=0
        )
        db.add(pub)
        import asyncio
        asyncio.create_task(
            YouTubePublishingService.execute_async_upload(
                publication_id=pub.id,
                video_path=str(ctx.final_video_path)
            )
        )
        
        res = {
            "success": True,
            "status": "UPLOADING_ASYNC",
            "publication_id": pub.id
        }
        ctx.publication_status = res.get("status", "SUCCESS")
        ctx.publication_record = res
        return res

    async def _save_publication_record(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        qc_res = await self.run_qc(ctx)
        ctx.qc_reports["PUBLISH"] = qc_res
        return ctx.publication_record
