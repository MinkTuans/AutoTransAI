"""Guarded character voice timeline, frozen from published Git 8ae030a.

Accept complete pre-timeline or complete published/startup post-timeline
profiles. Python-only startup defaults are not SQL defaults. Ownership cannot
be inferred from presence, so downgrade requires restoration from backup.
"""

from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa

revision = "20260916_character_voice_timeline"
down_revision = "20260915_tiktok_accounts"
branch_labels = None
depends_on = None


def _helper():
    return load_python_file(str(Path(__file__).resolve().parents[1]), 'voice_prerequisites.py')


def _tables(helper, startup=False):
    parents, children = helper._tables()
    mappings, segments = children
    for column in (
        sa.Column("character_id", sa.String(36), nullable=True, index=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
    ):
        mappings.append_column(column)
    for column in (
        sa.Column("speaker_id", sa.String(100), nullable=True),
        sa.Column("character_id", sa.String(36), nullable=True),
        sa.Column("voice_provider", sa.String(50), nullable=True),
        sa.Column("voice_id", sa.String(100), nullable=True),
        sa.Column("original_start", sa.Float(), nullable=True),
        sa.Column("original_end", sa.Float(), nullable=True),
        sa.Column("scheduled_start", sa.Float(), nullable=True),
        sa.Column("scheduled_end", sa.Float(), nullable=True),
        sa.Column("tts_duration", sa.Float(), nullable=True),
        sa.Column("overlap_with", sa.JSON(), nullable=True),
        sa.Column("schedule_action", sa.String(100), nullable=True),
        sa.Column("mapping_confidence", sa.Float(), nullable=True),
    ):
        segments.append_column(column)
    sa.Index("ix_video_translation_segments_speaker_id", segments.c.speaker_id)
    sa.Index("ix_video_translation_segments_character_id", segments.c.character_id)

    profiles = sa.Table(
        "character_voice_profiles", mappings.metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("character_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("role", sa.String(20), nullable=False, server_default="supporting"),
        sa.Column("voice_provider", sa.String(50), nullable=True),
        sa.Column("voice_id", sa.String(100), nullable=True),
        sa.Column("mapping_confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confirmed_by_user", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=not startup),
        sa.Column("updated_at", sa.DateTime(), nullable=not startup),
        sa.UniqueConstraint("project_id", "character_id", name="uq_character_profile_project_character"),
    )
    sa.Index("ix_character_voice_profiles_project_id", profiles.c.project_id)
    sa.Index("ix_character_voice_profiles_character_id", profiles.c.character_id)

    pool = sa.Table(
        "voice_pool_entries", mappings.metadata,
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("language", sa.String(30), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("voice_id", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("provider_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=not startup),
        sa.Column("updated_at", sa.DateTime(), nullable=not startup),
        sa.UniqueConstraint("provider", "voice_id", name="uq_voice_pool_provider_voice"),
    )
    sa.Index("ix_voice_pool_entries_provider", pool.c.provider)
    sa.Index("ix_voice_pool_entries_language", pool.c.language)
    tables = (*children, profiles, pool)
    if startup:
        for table in tables:
            for column in table.columns:
                column.server_default = None
    return parents, tables


def upgrade():
    bind, helper = op.get_bind(), _helper()
    parents, tables = _tables(helper)
    inspector, present = helper.preflight_namespace(bind, parents, tables)
    if bind.dialect.name == 'sqlite':
        for table in tables:
            if bind.execute(sa.text(
                "SELECT 1 FROM sqlite_master WHERE type = 'trigger' AND tbl_name = :table COLLATE NOCASE "
                "UNION ALL SELECT 1 FROM sqlite_temp_master WHERE type = 'trigger' AND tbl_name = :table COLLATE NOCASE"),
                {'table': table.name}).first():
                helper._mismatch()
    child_names = {table.name for table in tables[:2]}
    if present in (set(), child_names):
        _, before = helper._tables()
        for table in before:
            if table.name in present:
                helper._validate_table(bind, inspector, table)
        # The entire namespace and existing group passed before any writes.
        helper.ensure(bind)
        for old, new in zip(before, tables[:2]):
            for column in new.columns:
                if column.name not in old.c:
                    # Direct ADD avoids SQLite batch table rebuilding for the
                    # published expression boolean defaults.
                    op.add_column(new.name, sa.Column(
                        column.name, column.type, nullable=column.nullable,
                        server_default=column.server_default))
            old_indexes = {index.name for index in old.indexes}
            for index in sorted(new.indexes, key=lambda item: item.name):
                if index.name not in old_indexes:
                    index.create(bind)
        for table in tables[2:]:
            table.create(bind)
    elif present == {table.name for table in tables}:
        # Require one coherent profile, not a per-column mixture of defaults.
        for startup in (False, True):
            try:
                for table in _tables(helper, startup)[1]:
                    helper._validate_table(bind, inspector, table)
                break
            except RuntimeError:
                if startup:
                    raise
    else:
        helper._mismatch()
    # Preserve historical originals; avoid even a redundant UPDATE on replay.
    segments = tables[1]
    for original, source in (('original_start', 'start_time'), ('original_end', 'end_time')):
        missing = segments.c[original].is_(None)
        if bind.execute(sa.select(segments.c.id).where(missing).limit(1)).first():
            bind.execute(segments.update().where(missing).values({original: segments.c[source]}))


def downgrade():
    raise RuntimeError('Cannot safely downgrade historical voice timeline; restore a verified backup instead.')
