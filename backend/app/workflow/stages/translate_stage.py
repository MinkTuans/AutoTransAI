"""Stage 3: Translate Stage — Project glossary system, cross-batch context translation, segment ID validation, recovery, and QC."""

from __future__ import annotations

import logging
from typing import Any

from app.database import async_session_factory
from app.workflow.workflow_context import WorkflowContext
from app.services.glossary_service import load_project_glossary

logger = logging.getLogger(__name__)


class TranslateStage:
    """Stage 3: Translate source segments into Vietnamese with glossary enforcement and context continuity."""

    STAGE_NAME = "TRANSLATE"
    STEPS = [
        "extract_entities",
        "create_load_glossary",
        "translate_transcript",
        "validate_segment_ids",
        "check_consistency",
        "translation_qc",
    ]

    async def execute_step(self, step_name: str, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        """Execute an individual step within Stage 3."""
        logger.info(f"[Stage TRANSLATE] Executing step: {step_name}")

        if step_name == "create_load_glossary":
            return await self._create_load_glossary(ctx, db)
        elif step_name == "extract_entities":
            return await self._extract_entities(ctx, db)
        elif step_name == "translate_transcript":
            return await self._translate_transcript(ctx, db)
        elif step_name == "validate_segment_ids":
            return await self._validate_segment_ids(ctx)
        elif step_name == "check_consistency":
            return await self._check_consistency(ctx)
        elif step_name == "translation_qc":
            return await self._translation_qc(ctx)
        else:
            raise ValueError(f"Unknown step in TRANSLATE stage: {step_name}")

    async def run_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        """Validate Stage 3 output requirements."""
        issues = []
        if not ctx.translated_segments:
            issues.append("No translated segments available.")

        source_ids = {seg.get("id") or seg.get("index") for seg in ctx.source_segments}
        translated_ids = {seg.get("id") or seg.get("index") for seg in ctx.translated_segments}

        missing = source_ids - translated_ids
        if missing:
            issues.append(f"Missing translated segment IDs: {sorted(list(missing))[:10]}")

        for seg in ctx.translated_segments:
            txt = (seg.get("translated_text") or seg.get("text") or "").strip()
            if not txt:
                issues.append(f"Empty translation for segment ID {seg.get('id') or seg.get('index')}")
                
            if "start" in seg and "end" in seg and float(seg["end"]) <= float(seg["start"]):
                issues.append(f"Invalid timeline (end <= start) for segment ID {seg.get('id') or seg.get('index')}")

        passed = len(issues) == 0
        return {
            "stage": self.STAGE_NAME,
            "passed": passed,
            "issues": issues,
            "metrics": {
                "source_count": len(ctx.source_segments),
                "translated_count": len(ctx.translated_segments),
                "glossary_terms": len(ctx.glossary),
            },
        }

    async def _create_load_glossary(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        glossary_list = []
        if db:
            terms = await load_project_glossary(db, ctx.project_id)
            glossary_list = [
                {
                    "source_term": t.source_term,
                    "translated_term": t.translated_term,
                    "term_type": t.term_type,
                    "approved": t.approved,
                    "priority": 1,
                }
                for t in terms
            ]

        ctx.glossary = glossary_list
        return {"glossary_count": len(ctx.glossary)}

    async def _extract_entities(self, ctx: WorkflowContext, db: Any) -> dict[str, Any]:
        from app.services.terminology_extractor import extract_and_persist_from_segments

        segments = list(ctx.source_segments or [])
        if not segments and ctx.raw_transcript:
            segments = [{"text": ctx.raw_transcript}]
        saved = await extract_and_persist_from_segments(
            db, ctx.project_id, segments, ctx.target_language
        )
        return {"entities_extracted": True, "saved": saved}

    async def _translate_transcript(self, ctx: WorkflowContext, db: Any = None) -> dict[str, Any]:
        from app.services.video_translator.translator_service import translate_transcript_segments

        # Format glossary dictionary for translator prompt
        glossary_dict = {
            item["source_term"]: item["translated_term"]
            for item in ctx.glossary
        }

        # Perform translation preserving cross-batch context
        translated = await translate_transcript_segments(
            segments=ctx.source_segments,
            source_language=ctx.source_language,
            target_language=ctx.target_language,
            job_id=ctx.job_id or ctx.workflow_id or "WORKFLOW",
            glossary=glossary_dict,
            db=db,
            project_id=ctx.project_id,
            sessions=async_session_factory,
        )

        ctx.translated_segments = translated

        if ctx.progress_callback:
            await ctx.progress_callback(
                self.STAGE_NAME,
                50, # 50% through translate stage
                len(ctx.translated_segments),
                len(ctx.source_segments),
                "Translation completed, validating..."
            )
            
        return {"translated_count": len(ctx.translated_segments)}

    async def _validate_segment_ids(self, ctx: WorkflowContext) -> dict[str, Any]:
        if len(ctx.translated_segments) != len(ctx.source_segments):
            raise RuntimeError(
                f"TRANSLATION_SEGMENT_MISMATCH: {len(ctx.translated_segments)}/{len(ctx.source_segments)}"
            )
        return {"validated_count": len(ctx.translated_segments)}

    async def _check_consistency(self, ctx: WorkflowContext) -> dict[str, Any]:
        from app.services.video_translator.translator_service import find_glossary_violations

        glossary_dict = {item["source_term"]: item["translated_term"] for item in ctx.glossary}
        violations = find_glossary_violations(
            ctx.translated_segments, glossary_dict,
            source_language=ctx.source_language,
            target_language=ctx.target_language,
        )
        if violations:
            raise RuntimeError(f"GLOSSARY_ENFORCEMENT_FAILED: {violations}")
        return {"consistency_checked": True}

    async def _translation_qc(self, ctx: WorkflowContext) -> dict[str, Any]:
        qc_res = await self.run_qc(ctx)
        ctx.qc_reports["TRANSLATE"] = qc_res
        return qc_res
