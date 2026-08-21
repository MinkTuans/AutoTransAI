from typing import Optional

from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    provider_type: Mapped[str] = mapped_column(String(20))  # audio, video, llm
    quota_type: Mapped[str] = mapped_column(String(50), default="unknown")
    # characters, credits, tokens, seconds, requests, unknown
    quota_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quota_used_local: Mapped[int] = mapped_column(Integer, default=0)
    # Tracks usage we've made locally for best-effort remaining estimate
    configured: Mapped[bool] = mapped_column(Boolean, default=False)
    api_key_set: Mapped[bool] = mapped_column(Boolean, default=False)
    # Never store the actual key here — only a boolean flag
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    capabilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON string of capabilities
