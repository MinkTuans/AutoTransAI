"""make project glossary the single terminology source of truth

Revision ID: 20260916_glossary_single_source
Revises: 20260916_character_voice_timeline
"""

from __future__ import annotations

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.services.glossary_migration import audit_legacy_glossary_rows
from app.services.glossary_service import clean_glossary_text, glossary_key


revision: str = "20260916_glossary_single_source"
down_revision: Union[str, Sequence[str], None] = "20260916_character_voice_timeline"
branch_labels = None
depends_on = None


def _table_exists(bind, name: str) -> bool:
    return name in sa.inspect(bind).get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "project_glossaries"):
        return
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("project_glossaries")}
    existing_constraints = {
        constraint.get("name")
        for constraint in inspector.get_unique_constraints("project_glossaries")
    }
    memory_exists = _table_exists(bind, "project_terminology_memory")
    if (
        not memory_exists
        and {"source_key", "translation_key"}.issubset(existing_columns)
        and {
            "uq_project_glossary_source_key",
            "uq_project_glossary_translation_key",
        }.issubset(existing_constraints)
    ):
        return

    glossary_rows = [
        {
            "table": "project_glossaries",
            "id": row.id,
            "project_id": row.project_id,
            "source_term": row.source_term,
            "translated_term": row.translated_term,
        }
        for row in bind.execute(
            sa.text(
                "SELECT id, project_id, source_term, translated_term "
                "FROM project_glossaries"
            )
        )
    ]
    memory_rows = []
    if memory_exists:
        memory_rows = [
            {
                "table": "project_terminology_memory",
                "id": row.id,
                "project_id": row.project_id,
                "source_term": row.source_term,
                "translated_term": row.suggested_term,
            }
            for row in bind.execute(
                sa.text(
                    "SELECT id, project_id, source_term, suggested_term "
                    "FROM project_terminology_memory"
                )
            )
        ]

    all_rows = glossary_rows + memory_rows
    audit = audit_legacy_glossary_rows(all_rows)
    if audit.conflicts:
        raise RuntimeError(
            "GLOSSARY_MIGRATION_CONFLICT: resolve legacy data before migration: "
            + json.dumps(audit.conflicts, ensure_ascii=False)
        )

    if "source_key" not in existing_columns or "translation_key" not in existing_columns:
        with op.batch_alter_table("project_glossaries") as batch_op:
            if "source_key" not in existing_columns:
                batch_op.add_column(sa.Column("source_key", sa.String(length=64), nullable=True))
            if "translation_key" not in existing_columns:
                batch_op.add_column(sa.Column("translation_key", sa.String(length=64), nullable=True))

    glossary_ids = {str(row["id"]) for row in glossary_rows}
    rows_by_id = {str(row["id"]): row for row in all_rows}
    for canonical_id in audit.canonical_ids:
        row = rows_by_id[canonical_id]
        source = clean_glossary_text(row["source_term"])
        target = clean_glossary_text(row["translated_term"])
        if canonical_id in glossary_ids:
            bind.execute(
                sa.text(
                    "UPDATE project_glossaries SET source_term=:source, translated_term=:target, "
                    "source_key=:source_key, translation_key=:translation_key WHERE id=:id"
                ),
                {
                    "id": canonical_id,
                    "source": source,
                    "target": target,
                    "source_key": glossary_key(source),
                    "translation_key": glossary_key(target),
                },
            )
        else:
            legacy = bind.execute(
                sa.text(
                    "SELECT term_type, confidence, source_context, created_at, updated_at "
                    "FROM project_terminology_memory WHERE id=:id"
                ),
                {"id": canonical_id},
            ).first()
            bind.execute(
                sa.text(
                    "INSERT INTO project_glossaries "
                    "(id, project_id, source_term, translated_term, source_key, translation_key, "
                    "term_type, confidence, source_context, approved, created_at, updated_at) "
                    "VALUES (:id, :project_id, :source, :target, :source_key, :translation_key, "
                    ":term_type, :confidence, :source_context, :approved, :created_at, :updated_at)"
                ),
                {
                    "id": canonical_id,
                    "project_id": row["project_id"],
                    "source": source,
                    "target": target,
                    "source_key": glossary_key(source),
                    "translation_key": glossary_key(target),
                    "term_type": legacy.term_type,
                    "confidence": legacy.confidence,
                    "source_context": legacy.source_context,
                    "approved": True,
                    "created_at": legacy.created_at,
                    "updated_at": legacy.updated_at,
                },
            )

    duplicate_glossary_ids = audit.duplicate_ids & glossary_ids
    for duplicate_id in duplicate_glossary_ids:
        bind.execute(
            sa.text("DELETE FROM project_glossaries WHERE id=:id"), {"id": duplicate_id}
        )

    with op.batch_alter_table("project_glossaries") as batch_op:
        batch_op.alter_column("source_key", existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column("translation_key", existing_type=sa.String(length=64), nullable=False)
        if "uq_project_glossary_source_key" not in existing_constraints:
            batch_op.create_unique_constraint(
                "uq_project_glossary_source_key", ["project_id", "source_key"]
            )
        if "uq_project_glossary_translation_key" not in existing_constraints:
            batch_op.create_unique_constraint(
                "uq_project_glossary_translation_key", ["project_id", "translation_key"]
            )

    if _table_exists(bind, "project_terminology_memory"):
        op.drop_table("project_terminology_memory")


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "project_glossaries"):
        with op.batch_alter_table("project_glossaries") as batch_op:
            batch_op.drop_constraint("uq_project_glossary_translation_key", type_="unique")
            batch_op.drop_constraint("uq_project_glossary_source_key", type_="unique")
            batch_op.drop_column("translation_key")
            batch_op.drop_column("source_key")
