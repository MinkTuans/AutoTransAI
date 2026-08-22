"""sync model schema across video translation jobs, assets, projects, and segments

Revision ID: 20260822_sync_schema
Revises: 202da08bcdd8
Create Date: 2026-08-22 04:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260822_sync_schema'
down_revision: Union[str, Sequence[str], None] = '202da08bcdd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include all ORM model columns."""
    # video_translation_jobs column additions
    with op.batch_alter_table('video_translation_jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('llm_provider_id', sa.String(length=50), nullable=True, server_default='openai'))
        batch_op.add_column(sa.Column('r2_key', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('output_url', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_cleaned', sa.Boolean(), server_default='0'))
        batch_op.add_column(sa.Column('stage', sa.String(length=50), server_default='QUEUED'))
        batch_op.add_column(sa.Column('stage_progress_pct', sa.Float(), server_default='0.0'))
        batch_op.add_column(sa.Column('overall_progress_pct', sa.Float(), server_default='0.0'))
        batch_op.add_column(sa.Column('pid', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_heartbeat', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ffmpeg_stats_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('completed_segments_count', sa.Integer(), server_default='0'))
        batch_op.add_column(sa.Column('total_segments_count', sa.Integer(), server_default='0'))

    # video_assets column additions
    with op.batch_alter_table('video_assets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('r2_key', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('url', sa.Text(), nullable=True))

    # projects column additions
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('r2_key', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('media_url', sa.Text(), nullable=True))

    # segments column additions
    with op.batch_alter_table('segments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('audio_error_message', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('video_error_message', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('video_error_details', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
