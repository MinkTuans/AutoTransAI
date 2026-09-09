"""Stage 1: Ingest Stage — Import, validate, probe video metadata, store asset, extract audio."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.workflow.workflow_context import WorkflowContext

logger = logging.getLogger(__name__)


class IngestStage:
    """Stage 1: Ingest source media and extract raw audio."""

    STAGE_NAME = "INGEST"
    STEPS = [
        "import_video",
        "validate_video",
        "probe_video",
        "store_asset",
        "extract_audio",
    ]

    async def execute_step(self, step_name: str, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        """Execute an individual step within Stage 1."""
        logger.info(f"[Stage INGEST] Executing step: {step_name}")

        if step_name == "import_video":
            return await self._import_video(ctx, db)
        elif step_name == "validate_video":
            return await self._validate_video(ctx)
        elif step_name == "probe_video":
            return await self._probe_video(ctx)
        elif step_name == "store_asset":
            return await self._store_asset(ctx, db)
        elif step_name == "extract_audio":
            return await self._extract_audio(ctx)
        else:
            raise ValueError(f"Unknown step in INGEST stage: {step_name}")

    async def run_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Validate Stage 1 output requirements."""
        issues = []
        if not ctx.video_path or not Path(ctx.video_path).is_file():
            issues.append("Source video file is missing or invalid.")
        if not ctx.audio_path or not Path(ctx.audio_path).is_file():
            issues.append("Extracted audio file is missing or invalid.")
        if ctx.duration <= 0:
            issues.append("Video duration could not be determined.")

        passed = len(issues) == 0
        return {
            "stage": self.STAGE_NAME,
            "passed": passed,
            "issues": issues,
            "metrics": {
                "duration": ctx.duration,
                "resolution": ctx.resolution,
                "fps": ctx.fps,
                "video_path": ctx.video_path,
                "audio_path": ctx.audio_path,
            },
        }

    async def _import_video(self, ctx: WorkflowContext, db: Any = None) -> dict[str, Any]:
        # 1. Auto-resolve video_path or video_url from DB if missing or non-existent
        if not ctx.video_path or not Path(ctx.video_path).is_file():
            await self._resolve_video_from_db(ctx, db)

        # 2. Reuse video_source service if video_url is present, or verify existing file
        if ctx.video_url and (not ctx.video_path or not Path(ctx.video_path).is_file()):
            from app.services.video_source import get_video_source_service
            service = get_video_source_service()
            storage_dir = Path("storage") / "projects" / ctx.project_id
            storage_dir.mkdir(parents=True, exist_ok=True)
            download_res = await service.download_video(ctx.video_url, storage_dir)
            ctx.video_path = download_res.get("file_path") or download_res.get("local_path")

        if not ctx.video_path or not Path(ctx.video_path).is_file():
            raise FileNotFoundError(f"Video file not found for project {ctx.project_id}: {ctx.video_path}")

        return {"video_path": ctx.video_path, "status": "imported"}

    async def _resolve_video_from_db(self, ctx: WorkflowContext, db: Any = None):
        """Auto-resolve video_path or video_url from VideoTranslationJob, VideoAsset, or Project table."""
        if not db:
            return

        try:
            from sqlalchemy import select
            from app.models.video_translator import VideoTranslationJob, VideoAsset
            from app.models.project import Project

            # Check VideoTranslationJob -> VideoAsset first
            stmt_job = (
                select(VideoTranslationJob)
                .where((VideoTranslationJob.project_id == ctx.project_id) | (VideoTranslationJob.id == ctx.project_id))
                .order_by(VideoTranslationJob.created_at.desc())
            )
            res_job = await db.execute(stmt_job)
            job = res_job.scalars().first()
            if job and job.asset_id:
                stmt_asset = select(VideoAsset).where(VideoAsset.id == job.asset_id)
                res_asset = await db.execute(stmt_asset)
                asset = res_asset.scalars().first()
                if asset:
                    if asset.file_path and Path(asset.file_path).is_file():
                        ctx.video_path = asset.file_path
                        logger.info(f"[IngestStage] Resolved video_path from VideoAsset {asset.id}: {asset.file_path}")
                        return
                    elif asset.source_url:
                        ctx.video_url = asset.source_url
                        logger.info(f"[IngestStage] Resolved video_url from VideoAsset {asset.id}: {asset.source_url}")
                        return

            # Check Project table
            stmt_proj = select(Project).where(Project.id == ctx.project_id)
            res_proj = await db.execute(stmt_proj)
            proj = res_proj.scalars().first()
            if proj:
                if proj.media_url:
                    if Path(proj.media_url).is_file():
                        ctx.video_path = proj.media_url
                        return
                    elif proj.media_url.startswith("http"):
                        ctx.video_url = proj.media_url
                        return
                proj_settings = proj.settings_json or {}
                if proj_settings.get("video_path") and Path(proj_settings["video_path"]).is_file():
                    ctx.video_path = proj_settings["video_path"]
                    return
                elif proj_settings.get("video_url"):
                    ctx.video_url = proj_settings["video_url"]
                    return
        except Exception as e:
            logger.warning(f"[IngestStage] Failed to auto-resolve video source for project {ctx.project_id}: {e}")

    async def _validate_video(self, ctx: WorkflowContext) -> dict[str, Any]:
        path = Path(ctx.video_path)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Video file is empty or non-existent: {ctx.video_path}")
        return {"validated": True, "size_bytes": path.stat().st_size}

    async def _probe_video(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.media.ffprobe import get_video_metadata_async
        info = await get_video_metadata_async(Path(ctx.video_path))
        ctx.duration = float(info.get("duration", 0.0))
        width = info.get("width", 1920)
        height = info.get("height", 1080)
        ctx.resolution = f"{width}x{height}"
        ctx.fps = float(info.get("fps", 30.0))
        ctx.video_metadata = info
        return info

    async def _store_asset(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        # Optionally upload to R2 cloud storage using existing storage service
        from app.services.storage_service import upload_file_to_r2
        r2_key = await upload_file_to_r2(ctx.video_path, f"projects/{ctx.project_id}/source.mp4")
        if r2_key:
            ctx.r2_key = r2_key
        return {"r2_key": ctx.r2_key or "local"}

    async def _extract_audio(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_translator.translator_service import extract_audio_from_video
        output_wav = Path(ctx.video_path).parent / "extracted_audio.wav"
        extracted_path = await extract_audio_from_video(Path(ctx.video_path), output_wav)
        ctx.audio_path = str(extracted_path)
        return {"audio_path": str(extracted_path)}
