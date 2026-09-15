"""add tiktok_accounts for Login Kit OAuth

Revision ID: 20260915_tiktok_accounts
Revises: 20260908_workflow_progress
Create Date: 2026-09-15 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260915_tiktok_accounts"
down_revision = "20260908_workflow_progress"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tiktok_accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("open_id", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False, server_default="TikTok"),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("credentials_json", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tiktok_accounts_open_id", "tiktok_accounts", ["open_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tiktok_accounts_open_id", table_name="tiktok_accounts")
    op.drop_table("tiktok_accounts")
