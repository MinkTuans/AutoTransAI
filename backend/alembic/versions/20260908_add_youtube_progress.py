"""add youtube publication progress

Revision ID: 20260908_youtube_progress
Revises: 20260822_sync_schema
Create Date: 2026-09-08 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260908_youtube_progress'
down_revision = '20260822_sync_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add progress column to youtube_publications
    with op.batch_alter_table('youtube_publications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress', sa.Integer(), server_default='0', nullable=False))

def downgrade() -> None:
    with op.batch_alter_table('youtube_publications', schema=None) as batch_op:
        batch_op.drop_column('progress')
