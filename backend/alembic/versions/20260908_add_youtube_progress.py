"""add youtube publication progress

Revision ID: 20260908_youtube_progress
Revises: 20260822_sync_schema
Create Date: 2026-09-08 08:50:00.000000

"""
from pathlib import Path

from alembic.util import load_python_file

# revision identifiers, used by Alembic.
revision = '20260908_youtube_progress'
down_revision = '20260822_sync_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    _prerequisites().upgrade_group('youtube')


def downgrade() -> None:
    _prerequisites().refuse_downgrade()


def _prerequisites():
    return load_python_file(str(Path(__file__).resolve().parents[1]), 'progress_prerequisites.py')
