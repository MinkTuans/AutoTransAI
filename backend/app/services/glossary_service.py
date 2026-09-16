"""Canonical project glossary operations and conflict enforcement."""

from __future__ import annotations

import hashlib
import unicodedata
import uuid
from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_engine import ProjectGlossary


def clean_glossary_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = "".join(
        char for char in text
        if unicodedata.category(char) not in {"Cf", "Cc"} or char.isspace()
    )
    return " ".join(text.split())


def normalize_glossary_text(value: str) -> str:
    return clean_glossary_text(value).casefold()


def glossary_key(value: str) -> str:
    return hashlib.sha256(normalize_glossary_text(value).encode("utf-8")).hexdigest()


@dataclass
class GlossaryConflictError(Exception):
    code: str
    existing: ProjectGlossary
    source_term: str
    translated_term: str

    def __str__(self) -> str:
        return self.code

    def to_detail(self) -> dict:
        return {
            "code": self.code,
            "message": (
                "Source đã có canonical translation khác"
                if self.code == "GLOSSARY_SOURCE_CONFLICT"
                else "Translation đã được sử dụng bởi source khác"
            ),
            "existing": serialize_glossary_entry(self.existing),
            "candidate": {
                "source_term": self.source_term,
                "translated_term": self.translated_term,
            },
        }


def serialize_glossary_entry(row: ProjectGlossary) -> dict:
    return {
        "id": row.id,
        "source_term": row.source_term,
        "translated_term": row.translated_term,
        "term_type": row.term_type,
        "approved": row.approved,
    }


def _validated_values(source_term: str, translated_term: str) -> tuple[str, str, str, str]:
    source = clean_glossary_text(source_term)
    translation = clean_glossary_text(translated_term)
    if not source or not translation:
        raise ValueError("Source và Translation không được để trống")
    if len(source) > 255 or len(translation) > 255:
        raise ValueError("Source và Translation không được vượt quá 255 ký tự")
    return source, translation, glossary_key(source), glossary_key(translation)


async def _find_collision(
    db: AsyncSession,
    project_id: str,
    source_key: str,
    translation_key: str,
    exclude_id: str | None = None,
) -> ProjectGlossary | None:
    stmt = select(ProjectGlossary).where(
        ProjectGlossary.project_id == project_id,
        or_(
            ProjectGlossary.source_key == source_key,
            ProjectGlossary.translation_key == translation_key,
        ),
    )
    if exclude_id:
        stmt = stmt.where(ProjectGlossary.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalars().first()


def _raise_or_return_existing(
    row: ProjectGlossary,
    source: str,
    translation: str,
    source_key: str,
    translation_key: str,
) -> ProjectGlossary:
    if row.source_key == source_key and row.translation_key == translation_key:
        return row
    code = (
        "GLOSSARY_SOURCE_CONFLICT"
        if row.source_key == source_key
        else "GLOSSARY_TRANSLATION_CONFLICT"
    )
    raise GlossaryConflictError(code, row, source, translation)


async def create_glossary_entry(
    db: AsyncSession,
    project_id: str,
    source_term: str,
    translated_term: str,
    term_type: str = "other",
    *,
    confidence: float = 1.0,
    source_context: str | None = None,
) -> tuple[ProjectGlossary, bool]:
    source, translation, source_key, translation_key = _validated_values(
        source_term, translated_term
    )
    existing = await _find_collision(db, project_id, source_key, translation_key)
    if existing:
        return _raise_or_return_existing(
            existing, source, translation, source_key, translation_key
        ), False

    row = ProjectGlossary(
        id=str(uuid.uuid4()),
        project_id=project_id,
        source_term=source,
        translated_term=translation,
        source_key=source_key,
        translation_key=translation_key,
        term_type=(term_type or "other")[:50],
        confidence=max(0.0, min(float(confidence), 1.0)),
        source_context=source_context,
        approved=True,
    )
    db.add(row)
    try:
        await db.commit()
        return row, True
    except IntegrityError:
        await db.rollback()
        winner = await _find_collision(db, project_id, source_key, translation_key)
        if winner:
            return _raise_or_return_existing(
                winner, source, translation, source_key, translation_key
            ), False
        raise


async def update_glossary_entry(
    db: AsyncSession,
    project_id: str,
    entry_id: str,
    source_term: str,
    translated_term: str,
    term_type: str,
) -> ProjectGlossary:
    source, translation, source_key, translation_key = _validated_values(
        source_term, translated_term
    )
    result = await db.execute(
        select(ProjectGlossary).where(
            ProjectGlossary.id == entry_id,
            ProjectGlossary.project_id == project_id,
        )
    )
    row = result.scalars().first()
    if row is None:
        raise LookupError("Glossary entry not found")
    collision = await _find_collision(
        db, project_id, source_key, translation_key, exclude_id=entry_id
    )
    if collision:
        _raise_or_return_existing(collision, source, translation, source_key, translation_key)
    row.source_term = source
    row.translated_term = translation
    row.source_key = source_key
    row.translation_key = translation_key
    row.term_type = (term_type or "other")[:50]
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        collision = await _find_collision(
            db, project_id, source_key, translation_key, exclude_id=entry_id
        )
        if collision:
            _raise_or_return_existing(collision, source, translation, source_key, translation_key)
        raise
    return row


async def load_project_glossary(db: AsyncSession, project_id: str) -> list[ProjectGlossary]:
    result = await db.execute(
        select(ProjectGlossary)
        .where(ProjectGlossary.project_id == project_id, ProjectGlossary.approved.is_(True))
        .order_by(ProjectGlossary.source_term)
    )
    return list(result.scalars().all())
