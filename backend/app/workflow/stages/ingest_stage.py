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
            return await self._import_video(ctx)
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

    async def _import_video(self, ctx: WorkflowContext) -> dict[str, Any]:
        # Reuse video_source service if video_url is present, or verify existing file
        if ctx.video_url and not ctx.video_path:
            from app.services.video_source import download_video_from_url
            download_res = await download_video_from_url(ctx.video_url, ctx.project_id)
            ctx.video_path = download_res.get("file_path")

        if not ctx.video_path or not Path(ctx.video_path).is_file():
            raise FileNotFoundError(f"Video file not found for project {ctx.project_id}: {ctx.video_path}")

        return {"video_path": ctx.video_path, "status": "imported"}

    async def _validate_video(self, ctx: WorkflowContext) -> dict[str, Any]:
        path = Path(ctx.video_path)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Video file is empty or non-existent: {ctx.video_path}")
        return {"validated": True, "size_bytes": path.stat().st_size}

    async def _probe_video(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_source import probe_media_file
        info = await probe_media_file(ctx.video_path)
        ctx.duration = info.get("duration", 0.0)
        ctx.resolution = info.get("resolution", "1920x1080")
        ctx.fps = info.get("fps", 30.0)
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
        from app.services.video_source import extract_audio_track
        output_wav = str(Path(ctx.video_path).parent / "extracted_audio.wav")
        extracted_path = await extract_audio_track(ctx.video_path, output_wav)
        ctx.audio_path = extracted_path
        return {"audio_path": extracted_path}
