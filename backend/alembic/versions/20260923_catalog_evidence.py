"""Add bounded provider discovery evidence without modifying historical rows."""
from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa

revision = "20260923_catalog_evidence"
down_revision = "20260923_catalog_refresh"
branch_labels = None
depends_on = None


def upgrade():
    if load_python_file(str(Path(__file__).resolve().parents[1]),
                        'catalog_prerequisites.py').is_startup_final(op.get_bind()):
        return
    op.add_column("ai_catalog_models", sa.Column("discovery_metadata", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("ai_catalog_models", "discovery_metadata")
