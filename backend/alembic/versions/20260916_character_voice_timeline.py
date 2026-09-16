"""add character voice profiles and scheduled audio timeline"""

from alembic import op
import sqlalchemy as sa

revision = "20260916_character_voice_timeline"
down_revision = "20260915_tiktok_accounts"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("speaker_voice_mappings") as batch:
        batch.add_column(sa.Column("character_id", sa.String(36), nullable=True))
        batch.add_column(sa.Column("confidence", sa.Float(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.create_index("ix_speaker_voice_mappings_character_id", ["character_id"])

    with op.batch_alter_table("video_translation_segments") as batch:
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
            batch.add_column(column)
        batch.create_index("ix_video_translation_segments_speaker_id", ["speaker_id"])
        batch.create_index("ix_video_translation_segments_character_id", ["character_id"])
    op.execute("UPDATE video_translation_segments SET original_start = start_time WHERE original_start IS NULL")
    op.execute("UPDATE video_translation_segments SET original_end = end_time WHERE original_end IS NULL")

    op.create_table(
        "character_voice_profiles",
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
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("project_id", "character_id", name="uq_character_profile_project_character"),
    )
    op.create_index("ix_character_voice_profiles_project_id", "character_voice_profiles", ["project_id"])
    op.create_index("ix_character_voice_profiles_character_id", "character_voice_profiles", ["character_id"])

    op.create_table(
        "voice_pool_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("language", sa.String(30), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("voice_id", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("provider_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("provider", "voice_id", name="uq_voice_pool_provider_voice"),
    )
    op.create_index("ix_voice_pool_entries_provider", "voice_pool_entries", ["provider"])
    op.create_index("ix_voice_pool_entries_language", "voice_pool_entries", ["language"])


def downgrade():
    op.drop_table("voice_pool_entries")
    op.drop_table("character_voice_profiles")
    with op.batch_alter_table("video_translation_segments") as batch:
        batch.drop_index("ix_video_translation_segments_character_id")
        batch.drop_index("ix_video_translation_segments_speaker_id")
        for name in ("mapping_confidence", "schedule_action", "overlap_with", "tts_duration", "scheduled_end", "scheduled_start", "original_end", "original_start", "voice_id", "voice_provider", "character_id", "speaker_id"):
            batch.drop_column(name)
    with op.batch_alter_table("speaker_voice_mappings") as batch:
        batch.drop_index("ix_speaker_voice_mappings_character_id")
        batch.drop_column("needs_review")
        batch.drop_column("confidence")
        batch.drop_column("character_id")
