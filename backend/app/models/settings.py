"""
ORM Models for System Settings, AI Function Configs, AI Models Catalog, and Social Accounts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemSetting(Base):
    """General key-value store for application & infrastructure settings."""
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)  # JSON or plain string representation
    category: Mapped[str] = mapped_column(String(50), default="general")  # storage, processing, workflow, advanced
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class AIFunctionConfig(Base):
    """Configuration mapping for AI functions (STT, Translation, TTS, Video Gen, Image Gen)."""
    __tablename__ = "ai_function_configs"

    function_id: Mapped[str] = mapped_column(String(50), primary_key=True)  # stt, translation, tts, video_generation, image_generation
    function_name: Mapped[str] = mapped_column(String(100))
    capability: Mapped[str] = mapped_column(String(50))  # STT, LLM, TRANSLATION, TTS, VIDEO_GENERATION, IMAGE_GENERATION
    primary_provider_id: Mapped[str] = mapped_column(String(50))
    model_id: Mapped[str] = mapped_column(String(100), default="default")
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_provider_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class AIModel(Base):
    """Catalog of supported and custom AI Models per provider."""
    __tablename__ = "ai_models"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g., gemini-2.5-flash, whisper-1
    provider_id: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    capabilities: Mapped[str] = mapped_column(Text)  # JSON array string: ["STT", "LLM", "TRANSLATION"]
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class SocialAccount(Base):
    """Social Media Account Manager (YouTube, TikTok, Facebook, Instagram)."""
    __tablename__ = "social_accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    platform: Mapped[str] = mapped_column(String(50))  # youtube, tiktok, facebook, instagram
    account_name: Mapped[str] = mapped_column(String(100))
    channel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="connected")  # connected, token_expired, disconnected
    connected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    priority: Mapped[int] = mapped_column(Integer, default=1)
    credentials_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
