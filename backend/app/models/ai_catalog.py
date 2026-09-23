"""Provider-scoped model inventory independent of credential lifetime."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.api_key import utcnow


class CatalogModel(Base):
    __tablename__ = "ai_catalog_models"
    __table_args__ = (UniqueConstraint("provider_id", "remote_model_id", name="uq_catalog_provider_remote"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id", ondelete="RESTRICT"), index=True)
    # The provider's exact spelling is identity; do not trim, casefold, or remove prefixes.
    remote_model_id: Mapped[str] = mapped_column(String(255).with_variant(String(255, collation="utf8mb4_bin"), "mysql"))
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="discovered")
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    capability_status: Mapped[str] = mapped_column(String(30), default="FULL_UNKNOWN")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    retired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class KeyModelAccess(Base):
    __tablename__ = "ai_key_model_access"

    key_id: Mapped[str] = mapped_column(ForeignKey("api_keys.id", ondelete="CASCADE"), primary_key=True)
    model_id: Mapped[str] = mapped_column(ForeignKey("ai_catalog_models.id", ondelete="CASCADE"), primary_key=True, index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
