"""Stage 5: Produce Stage — Subtitle generation (ASS/SRT/VTT), reframing, watermark/logo, BGM ducking, final FFmpeg render, and QC."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.workflow.workflow_context import WorkflowContext

logger = logging.getLogger(__name__)


class ProduceStage:
    """Stage 5: Final video assembly, post-processing effects, subtitle embedding, rendering, and technical QC."""

    STAGE_NAME = "PRODUCE"
    STEPS = [
        "generate_subtitles",
        "video_reframing",
        "add_watermark_logo",
        "add_intro_outro",
        "add_bgm",
        "final_render",
        "final_video_qc",
    ]

    async def execute_step(self, step_name: str, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        """Execute an individual step within Stage 5."""
        logger.info(f"[Stage PRODUCE] Executing step: {step_name}")

        if step_name == "generate_subtitles":
            return await self._generate_subtitles(ctx)
        elif step_name == "video_reframing":
            return await self._video_reframing(ctx)
        elif step_name == "add_watermark_logo":
            return await self._add_watermark_logo(ctx)
        elif step_name == "add_intro_outro":
            return await self._add_intro_outro(ctx)
        elif step_name == "add_bgm":
            return await self._add_bgm(ctx)
        elif step_name == "final_render":
            return await self._final_render(ctx)
        elif step_name == "final_video_qc":
            return await self._final_video_qc(ctx)
        else:
            raise ValueError(f"Unknown step in PRODUCE stage: {step_name}")

    async def run_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Validate Stage 5 output requirements."""
        issues = []
        if not ctx.final_video_path or not Path(ctx.final_video_path).is_file():
            issues.append("Final rendered video file is missing.")

        # Execute technical QC via qc_service
        if ctx.final_video_path and Path(ctx.final_video_path).is_file():
            from app.services.video_editor.qc_service import run_technical_qc
            tech_report = await run_technical_qc(ctx.final_video_path)
            if not tech_report.get("passed", True):
                issues.extend(tech_report.get("errors", []))

        passed = len(issues) == 0
        return {
            "stage": self.STAGE_NAME,
            "passed": passed,
            "issues": issues,
            "metrics": {
                "final_video_path": ctx.final_video_path,
                "subtitle_files": ctx.subtitle_files,
            },
        }

    async def _generate_subtitles(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_editor.subtitle_service import generate_subtitles_for_project
        out_dir = str(Path(ctx.video_path).parent) if ctx.video_path else "."
        
        subs = await generate_subtitles_for_project(
            segments=ctx.translated_segments if ctx.translated_segments else ctx.source_segments,
            output_dir=out_dir,
        )
        ctx.subtitle_files = subs
        return {"subtitles_generated": list(subs.keys())}

    async def _video_reframing(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"reframing_applied": False}

    async def _add_watermark_logo(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"watermark_logo_applied": False}

    async def _add_intro_outro(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"intro_outro_applied": False}

    async def _add_bgm(self, ctx: WorkflowContext) -> dict[str, Any]:
        return {"bgm_applied": False}

    async def _final_render(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_translator.translator_service import VideoTranslatorService
        svc = VideoTranslatorService()

        out_final = str(Path(ctx.video_path).parent / "final_dubbed_video.mp4") if ctx.video_path else "final_dubbed_video.mp4"
        
        # Multiplex dubbed audio track with original video using FFmpeg
        final_path = await svc.mux_video_and_audio(
            video_path=ctx.video_path,
            audio_path=ctx.dubbed_audio_path,
            output_path=out_final,
            subtitles_ass=ctx.subtitle_files.get("ass"),
        )
        ctx.final_video_path = final_path

        # Upload final output to R2 if configured
        if ctx.final_video_path:
            from app.services.storage_service import upload_file_to_r2
            r2_key = await upload_file_to_r2(ctx.final_video_path, f"projects/{ctx.project_id}/final_output.mp4")
            if r2_key:
                ctx.r2_key = r2_key

        return {"final_video_path": ctx.final_video_path}

    async def _final_video_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        qc_res = await self.run_qc(ctx)
        ctx.qc_reports["PRODUCE"] = qc_res
        return qc_res
