"""Stage 2: Analyze Stage — Speech-to-Text, speaker detection, timeline validation & cleanup, transcript QC."""

from __future__ import annotations

import logging
from typing import Any

from app.workflow.workflow_context import WorkflowContext

logger = logging.getLogger(__name__)


class AnalyzeStage:
    """Stage 2: Transcribe source audio using Gemini STT / Whisper fallback and validate timeline."""

    STAGE_NAME = "ANALYZE"
    STEPS = [
        "speech_to_text",
        "detect_language",
        "detect_speakers",
        "validate_timeline",
        "clean_timeline",
        "transcript_qc",
    ]

    async def execute_step(self, step_name: str, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        """Execute an individual step within Stage 2."""
        logger.info(f"[Stage ANALYZE] Executing step: {step_name}")

        if step_name == "speech_to_text":
            return await self._speech_to_text(ctx, db)
        elif step_name == "detect_language":
            return await self._detect_language(ctx)
        elif step_name == "detect_speakers":
            return await self._detect_speakers(ctx)
        elif step_name == "validate_timeline":
            return await self._validate_timeline(ctx)
        elif step_name == "clean_timeline":
            return await self._clean_timeline(ctx)
        elif step_name == "transcript_qc":
            return await self._transcript_qc(ctx)
        else:
            raise ValueError(f"Unknown step in ANALYZE stage: {step_name}")

    async def run_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Validate Stage 2 output requirements."""
        issues = []
        if not ctx.source_segments:
            issues.append("No source segments transcribed.")

        for i, seg in enumerate(ctx.source_segments):
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            if start < 0 or end <= start:
                issues.append(f"Invalid timestamp range at segment index {i}: start={start}, end={end}")
            if ctx.duration > 0 and end > ctx.duration + 5.0:
                issues.append(f"Segment index {i} end timestamp ({end}s) exceeds video duration ({ctx.duration}s).")

        passed = len(issues) == 0
        return {
            "stage": self.STAGE_NAME,
            "passed": passed,
            "issues": issues,
            "metrics": {
                "segment_count": len(ctx.source_segments),
                "source_language": ctx.source_language,
                "speakers_detected": len(ctx.speakers),
            },
        }

    async def _speech_to_text(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        # Use module-level STT function with db session for model resolution
        from app.services.video_translator.translator_service import speech_to_text_and_detect_language

        result_segments, detected_lang = await speech_to_text_and_detect_language(
            audio_path=ctx.audio_path,
            job_id=getattr(ctx, 'job_id', 'WF-JOB'),
            target_language=ctx.target_language,
            source_language=ctx.source_language,
            db=db,
        )
        
        ctx.raw_transcript = " ".join(seg.get("text", "") for seg in result_segments)
        ctx.source_segments = result_segments
        if detected_lang:
            ctx.source_language = detected_lang

        return {"segment_count": len(ctx.source_segments), "detected_language": ctx.source_language}

    async def _detect_language(self, ctx: WorkflowContext) -> dict[str, Any]:
        # Language is detected during STT phase
        return {"source_language": ctx.source_language}

    async def _detect_speakers(self, ctx: WorkflowContext) -> dict[str, Any]:
        # Extract unique speakers if populated by STT
        speaker_ids = set()
        for seg in ctx.source_segments:
            spk = seg.get("speaker", "SPEAKER_00")
            speaker_ids.add(spk)

        ctx.speakers = [{"speaker_id": spk, "speaker_name": f"Speaker {spk}"} for spk in sorted(speaker_ids)]
        return {"speakers": ctx.speakers}

    async def _validate_timeline(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_translator.translator_service import validate_and_clean_timeline_segments
        validated_segments = validate_and_clean_timeline_segments(ctx.source_segments, ctx.duration)
        ctx.source_segments = validated_segments
        return {"validated_count": len(ctx.source_segments)}

    async def _clean_timeline(self, ctx: WorkflowContext) -> dict[str, Any]:
        # Timeline already validated and cleaned in _validate_timeline
        return {"cleaned_count": len(ctx.source_segments)}

    async def _transcript_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        qc_res = await self.run_qc(ctx)
        ctx.qc_reports["ANALYZE"] = qc_res
        return qc_res
