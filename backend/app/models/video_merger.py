"""
Video Merger ORM models.

Stores VideoMergeJob and VideoMergeAsset states for video concatenation workflow.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MergeJobStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoMergeJob(Base):
    __tablename__ = "video_merge_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), default="Untitled Merge")
    status: Mapped[str] = mapped_column(String(30), default=MergeJobStatus.PENDING.value)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    input_files_json: Mapped[str] = mapped_column(Text)  # JSON array of ordered input files info
    output_video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_relative_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_duration: Mapped[float] = mapped_column(Float, default=0.0)
    processed_duration: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class VideoMergeAsset(Base):
    __tablename__ = "video_merge_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    fps: Mapped[float] = mapped_column(Float, default=0.0)
    has_audio: Mapped[bool] = mapped_column(Boolean, default=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
