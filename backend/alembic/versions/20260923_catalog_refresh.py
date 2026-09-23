"""Persist refresh runs, concurrency revision, and visible invalid-default state."""
from alembic import op
import sqlalchemy as sa

revision = "20260923_catalog_refresh"
down_revision = "20260923_ai_catalog"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("providers", sa.Column("catalog_revision", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ai_function_configs", sa.Column("configuration_error", sa.String(50), nullable=True))
    op.create_table("ai_catalog_refresh_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("ai_catalog_refresh_runs")
    op.drop_column("ai_function_configs", "configuration_error")
    op.drop_column("providers", "catalog_revision")
