"""
Video Thumbnail ORM Model.

Stores AI-generated video thumbnails, prompts, style configurations,
AI content analysis, R2 keys, and access URLs.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ThumbnailStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING_PROMPT = "generating_prompt"
    GENERATING_IMAGE = "generating_image"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoThumbnail(Base):
    __tablename__ = "video_thumbnails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("video_translation_jobs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    asset_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("video_assets.id", ondelete="CASCADE"), nullable=True, index=True
    )

    source_title: Mapped[str] = mapped_column(String(255), default="Untitled")
    source_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    selected_style: Mapped[str] = mapped_column(String(50), default="auto")
    custom_instruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ai_analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    provider: Mapped[str] = mapped_column(String(50), default="pollinations")
    model: Mapped[str] = mapped_column(String(100), default="default")

    r2_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    width: Mapped[int] = mapped_column(Integer, default=1280)
    height: Mapped[int] = mapped_column(Integer, default=720)
    aspect_ratio: Mapped[str] = mapped_column(String(20), default="16:9")

    status: Mapped[str] = mapped_column(String(30), default=ThumbnailStatus.PENDING.value)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="thumbnails")  # type: ignore[name-defined]
    job: Mapped[Optional["VideoTranslationJob"]] = relationship("VideoTranslationJob", back_populates="thumbnails")  # type: ignore[name-defined]
    asset: Mapped[Optional["VideoAsset"]] = relationship("VideoAsset", back_populates="thumbnails")  # type: ignore[name-defined]
