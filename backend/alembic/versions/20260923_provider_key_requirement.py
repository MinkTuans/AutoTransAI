"""Persist provider credential requirement; unknown providers remain keyed."""
from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa

revision = "20260923_provider_key_requirement"
down_revision = "20260923_catalog_evidence"
branch_labels = None
depends_on = None


def upgrade():
    if load_python_file(str(Path(__file__).resolve().parents[1]),
                        'catalog_prerequisites.py').is_startup_final(op.get_bind()):
        return
    op.add_column("providers", sa.Column("requires_api_key", sa.Boolean(), nullable=False,
                                         server_default=sa.true()))


def downgrade():
    op.drop_column("providers", "requires_api_key")
