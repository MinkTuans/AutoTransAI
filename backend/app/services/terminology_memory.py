"""Extract and persist AI Auto Terminology Memory terms from transcripts."""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from typing import Any, Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.models.workflow_engine import ProjectTerminologyMemory

logger = get_logger(__name__)

_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")
_LATIN_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")

_CJK_STOP = {
    "一个", "我们", "他们", "什么", "不是", "可以", "因为", "所以", "这个", "那个",
    "没有", "已经", "现在", "自己", "知道", "出来", "起来", "时候", "这样", "那样",
}


def normalize_extracted_terms(raw: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in raw or []:
        source = str(item.get("source_term") or "").strip()
        if len(source) < 2:
            continue
        key = source.lower()
        if key in seen:
            continue
        seen.add(key)
        suggested = str(item.get("suggested_term") or source).strip() or source
        term_type = str(item.get("term_type") or "other").strip().lower() or "other"
        try:
            confidence = float(item.get("confidence") or 0.8)
        except (TypeError, ValueError):
            confidence = 0.8
        out.append(
            {
                "source_term": source,
                "suggested_term": suggested,
                "term_type": term_type[:50],
                "confidence": min(max(confidence, 0.0), 1.0),
                "source_context": (item.get("source_context") or None),
            }
        )
    return out


def heuristic_extract_terms(text: str, target_lang: str = "vi") -> list[dict[str, Any]]:
    """Fallback extractor: repeated CJK spans and Latin proper names."""
    blob = text or ""
    grams: list[str] = []
    for run in _CJK_RUN_RE.findall(blob):
        max_n = min(4, len(run))
        for n in range(2, max_n + 1):
            for i in range(0, len(run) - n + 1):
                grams.append(run[i : i + n])
    counts = Counter(grams)
    raw: list[dict[str, Any]] = []
    for term, n in counts.items():
        if term in _CJK_STOP:
            continue
        if len(term) < 3 and n < 2:
            continue
        if n < 1:
            continue
        raw.append(
            {
                "source_term": term,
                "suggested_term": term,
                "term_type": "other",
                "confidence": min(0.55 + 0.05 * n, 0.85),
                "source_context": f"appeared {n} times",
            }
        )
    latin_counts = Counter(_LATIN_NAME_RE.findall(blob))
    for term, n in latin_counts.items():
        if n < 2 or len(term) < 3:
            continue
        raw.append(
            {
                "source_term": term,
                "suggested_term": term,
                "term_type": "character",
                "confidence": min(0.5 + 0.05 * n, 0.8),
                "source_context": f"appeared {n} times",
            }
        )
    return normalize_extracted_terms(raw)


def _parse_llm_terms(payload: str) -> list[dict[str, Any]]:
    if not payload:
        return []
    text = payload.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            return []
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
    if isinstance(data, dict):
        data = data.get("terms") or data.get("entities") or []
    if not isinstance(data, list):
        return []
    return normalize_extracted_terms([x for x in data if isinstance(x, dict)])


async def llm_extract_terms(text: str, target_lang: str = "vi") -> list[dict[str, Any]]:
    blob = (text or "").strip()
    if len(blob) < 8:
        return []
    try:
        from app.providers.registry import get_registry

        registry = get_registry()
        llm = registry.get_llm("gemini") or next(iter(registry._llm.values()), None)
        if not llm:
            return []
        prompt = (
            "Extract named entities (characters, locations, organizations, skills, titles) "
            f"from this transcript for a {target_lang} translation glossary.\n"
            "Return ONLY a JSON array of objects with keys: "
            "source_term, suggested_term, term_type, confidence.\n"
            "suggested_term must be the translation in the target language.\n"
            "term_type one of: character, location, organization, skill, title, other.\n\n"
            f"Transcript:\n{blob[:6000]}"
        )
        raw = await llm.generate_text(prompt)
        return _parse_llm_terms(raw if isinstance(raw, str) else str(raw))
    except Exception as exc:
        logger.warning("LLM terminology extraction failed", error=str(exc))
        return []


async def persist_terminology_memory(
    db: Optional[AsyncSession],
    project_id: str,
    terms: list[dict[str, Any]],
) -> int:
    if db is None or not project_id or project_id == "default_project" or not terms:
        return 0
    saved = 0
    for item in normalize_extracted_terms(terms):
        stmt = select(ProjectTerminologyMemory).where(
            ProjectTerminologyMemory.project_id == project_id,
            ProjectTerminologyMemory.source_term == item["source_term"],
        )
        res = await db.execute(stmt)
        row = res.scalars().first()
        if not row:
            row = ProjectTerminologyMemory(
                id=str(uuid.uuid4()),
                project_id=project_id,
                source_term=item["source_term"],
                suggested_term=item["suggested_term"],
                term_type=item["term_type"],
                confidence=item["confidence"],
                needs_review=item["suggested_term"] == item["source_term"],
                source_context=item.get("source_context"),
            )
            db.add(row)
            saved += 1
        else:
            if item["suggested_term"] and item["suggested_term"] != item["source_term"]:
                row.suggested_term = item["suggested_term"]
            row.term_type = item["term_type"] or row.term_type
            row.confidence = max(row.confidence or 0, item["confidence"])
            saved += 1
    await db.commit()
    return saved


def segments_transcript_blob(segments: Optional[Iterable[dict[str, Any]]]) -> str:
    parts: list[str] = []
    for seg in segments or []:
        txt = (
            seg.get("text")
            or seg.get("original_text")
            or seg.get("translated_text")
            or ""
        )
        if txt:
            parts.append(str(txt))
    return "\n".join(parts)


async def extract_and_persist_from_segments(
    db: Optional[AsyncSession],
    project_id: str,
    segments: Optional[Iterable[dict[str, Any]]],
    target_lang: str = "vi",
) -> int:
    """Used by the Studio Auto job pipeline (startJob), which never hits TranslateStage."""
    blob = segments_transcript_blob(segments)
    if len(blob.strip()) < 4:
        return 0
    heuristic = heuristic_extract_terms(blob, target_lang)
    llm_terms = await llm_extract_terms(blob, target_lang)
    llm_keys = {t["source_term"].lower() for t in llm_terms}
    merged = llm_terms + [t for t in heuristic if t["source_term"].lower() not in llm_keys]
    return await persist_terminology_memory(db, project_id, merged)


def transcript_blob(ctx: Any) -> str:
    parts: list[str] = []
    if getattr(ctx, "raw_transcript", None):
        parts.append(str(ctx.raw_transcript))
    for seg in getattr(ctx, "source_segments", None) or []:
        txt = seg.get("text") or seg.get("original_text") or seg.get("translated_text") or ""
        if txt:
            parts.append(str(txt))
    return "\n".join(parts)
