"""Persist provider credential requirement; unknown providers remain keyed."""
from alembic import op
import sqlalchemy as sa

revision = "20260923_provider_key_requirement"
down_revision = "20260923_catalog_evidence"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("providers", sa.Column("requires_api_key", sa.Boolean(), nullable=False,
                                         server_default=sa.true()))


def downgrade():
    op.drop_column("providers", "requires_api_key")
