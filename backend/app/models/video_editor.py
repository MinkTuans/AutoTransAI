"""
Video Editing, Quality Control, and YouTube Publishing ORM models.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AspectRatioEnum(str, enum.Enum):
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    SQUARE_1_1 = "1:1"


class WatermarkPositionEnum(str, enum.Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class QCStatusEnum(str, enum.Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class PublishPrivacyEnum(str, enum.Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class PublishStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class VideoEditConfig(Base):
    __tablename__ = "video_edit_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    target_aspect_ratio: Mapped[str] = mapped_column(String(20), default=AspectRatioEnum.LANDSCAPE_16_9.value)
    
    # Logo / Watermark
    watermark_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    watermark_type: Mapped[str] = mapped_column(String(20), default="image")
    logo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    watermark_text: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    logo_position: Mapped[str] = mapped_column(String(30), default=WatermarkPositionEnum.BOTTOM_RIGHT.value)
    logo_scale: Mapped[float] = mapped_column(Float, default=0.20)
    logo_opacity: Mapped[float] = mapped_column(Float, default=0.80)
    watermark_margin: Mapped[int] = mapped_column(Integer, default=20)
    watermark_font_size: Mapped[int] = mapped_column(Integer, default=32)

    
    # Background Music (BGM)
    bgm_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bgm_volume_db: Mapped[float] = mapped_column(Float, default=-18.0)
    enable_bgm_ducking: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Subtitles
    enable_burned_subtitles: Mapped[bool] = mapped_column(Boolean, default=True)
    subtitle_style_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Intro / Outro bumpers
    intro_video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    outro_video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class QCReport(Base):
    __tablename__ = "qc_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    audio_lufs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sync_drift_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_black_frames: Mapped[bool] = mapped_column(Boolean, default=False)
    has_silence_anomalies: Mapped[bool] = mapped_column(Boolean, default=False)
    
    content_safety_score: Mapped[float] = mapped_column(Float, default=100.0)
    translation_quality_score: Mapped[float] = mapped_column(Float, default=100.0)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    
    qc_status: Mapped[str] = mapped_column(String(20), default=QCStatusEnum.PASSED.value)
    issues_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel_name: Mapped[str] = mapped_column(String(200))
    channel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    credentials_json: Mapped[str] = mapped_column(Text)  # Encrypted OAuth2 tokens
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class YouTubePublication(Base):
    __tablename__ = "youtube_publications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    channel_id: Mapped[str] = mapped_column(String(36), ForeignKey("youtube_channels.id", ondelete="CASCADE"))
    
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    tags_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[str] = mapped_column(String(20), default="22")  # People & Blogs
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    privacy_status: Mapped[str] = mapped_column(String(20), default=PublishPrivacyEnum.PRIVATE.value)
    scheduled_publish_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    youtube_video_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=PublishStatusEnum.PENDING.value)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
