"""Encrypted provider credentials; raw secrets belong only in the credential service."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class APIKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        UniqueConstraint("provider_id", "fingerprint", name="uq_api_keys_provider_fingerprint"),
        UniqueConstraint("id", "provider_id", name="uq_api_keys_id_provider"),
        CheckConstraint("priority > 0", name="ck_api_keys_priority_positive"),
        CheckConstraint("request_count >= 0 AND success_count >= 0 AND failure_count >= 0", name="ck_api_keys_counters_nonnegative"),
        CheckConstraint("runtime_status IN ('ready', 'rate_limited', 'invalid', 'exhausted')", name="ck_api_keys_runtime_status"),
        CheckConstraint("last_error_code IS NULL OR last_error_code IN ('auth', 'quota', 'rate_limit', 'timeout', 'provider_unavailable', 'model_unavailable', 'capability_mismatch', 'invalid_output')", name="ck_api_keys_last_error_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.id", ondelete="RESTRICT"), index=True)
    ciphertext: Mapped[str] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(String(64))
    masked_key: Mapped[str] = mapped_column(String(16))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    runtime_status: Mapped[str] = mapped_column(String(20), default="ready", server_default="ready")
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    success_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    failure_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
