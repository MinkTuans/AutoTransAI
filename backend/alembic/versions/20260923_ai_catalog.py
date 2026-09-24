"""Add canonical model inventory and encrypted credentials without rewriting legacy data.

Revision ID: 20260923_ai_catalog
Revises: 20260918_add_fk
"""
from pathlib import Path

from alembic import op
from alembic.util import load_python_file
import sqlalchemy as sa

revision = "20260923_ai_catalog"
down_revision = "20260918_add_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    load_python_file(str(Path(__file__).resolve().parents[1]), 'catalog_prerequisites.py').ensure(
        op.get_bind())
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(50), sa.ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ciphertext", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("masked_key", sa.String(16), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("provider_id", "fingerprint", name="uq_api_keys_provider_fingerprint"),
        sa.UniqueConstraint("id", "provider_id", name="uq_api_keys_id_provider"),
    )
    op.create_index("ix_api_keys_provider_id", "api_keys", ["provider_id"])
    op.create_table(
        "ai_catalog_models",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(50), sa.ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("remote_model_id", sa.String(255).with_variant(sa.String(255, collation="utf8mb4_bin"), "mysql"), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("capability_status", sa.String(30), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("retired_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("provider_id", "remote_model_id", name="uq_catalog_provider_remote"),
        sa.UniqueConstraint("id", "provider_id", name="uq_catalog_id_provider"),
    )
    op.create_index("ix_ai_catalog_models_provider_id", "ai_catalog_models", ["provider_id"])
    op.create_table(
        "ai_key_model_access",
        sa.Column("key_id", sa.String(36), primary_key=True),
        sa.Column("model_id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(50), nullable=False),
        sa.Column("discovered_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["key_id", "provider_id"], ["api_keys.id", "api_keys.provider_id"],
            name="fk_access_key_provider", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["model_id", "provider_id"], ["ai_catalog_models.id", "ai_catalog_models.provider_id"],
            name="fk_access_model_provider", ondelete="CASCADE",
        ),
    )
    op.create_index("ix_ai_key_model_access_model_id", "ai_key_model_access", ["model_id"])


def downgrade() -> None:
    # Administrative rollback removes only this revision's tables; never legacy tables.
    op.drop_table("ai_key_model_access")
    op.drop_table("ai_catalog_models")
    op.drop_table("api_keys")
