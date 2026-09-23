"""Provider-scoped model inventory independent of credential lifetime."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, ForeignKeyConstraint, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.api_key import utcnow


class CatalogModel(Base):
    __tablename__ = "ai_catalog_models"
    __table_args__ = (
        UniqueConstraint("provider_id", "remote_model_id", name="uq_catalog_provider_remote"),
        UniqueConstraint("id", "provider_id", name="uq_catalog_id_provider"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id", ondelete="RESTRICT"), index=True)
    # The provider's exact spelling is identity; do not trim, casefold, or remove prefixes.
    remote_model_id: Mapped[str] = mapped_column(String(255).with_variant(String(255, collation="utf8mb4_bin"), "mysql"))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Provider-allowlisted listing evidence; NULL means a pre-evidence historical row.
    discovery_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    source: Mapped[str] = mapped_column(String(30), default="discovered")
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    capability_status: Mapped[str] = mapped_column(String(30), default="FULL_UNKNOWN")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    retired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class KeyModelAccess(Base):
    """Credential-visible listing evidence, never verified generation entitlement."""
    __tablename__ = "ai_key_model_access"
    __table_args__ = (
        ForeignKeyConstraint(
            ["key_id", "provider_id"], ["api_keys.id", "api_keys.provider_id"],
            name="fk_access_key_provider", ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["model_id", "provider_id"], ["ai_catalog_models.id", "ai_catalog_models.provider_id"],
            name="fk_access_model_provider", ondelete="CASCADE",
        ),
    )

    key_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    provider_id: Mapped[str] = mapped_column(String(50))
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class CatalogRefreshRun(Base):
    __tablename__ = "ai_catalog_refresh_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mode: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="running")
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
