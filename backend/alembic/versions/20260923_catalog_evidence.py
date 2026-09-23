"""Add bounded provider discovery evidence without modifying historical rows."""
from alembic import op
import sqlalchemy as sa

revision = "20260923_catalog_evidence"
down_revision = "20260923_catalog_refresh"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("ai_catalog_models", sa.Column("discovery_metadata", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("ai_catalog_models", "discovery_metadata")
