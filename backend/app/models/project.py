"""Project model — top-level entity representing a script-to-video project."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from typing import Optional

from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkflowMode(str, enum.Enum):
    """What the project generates."""
    AUDIO_ONLY = "audio_only"
    AUDIO_VIDEO = "audio_video"


class WorkflowStatus(str, enum.Enum):
    """Project-level state machine states."""
    CREATED = "created"
    PARSED = "parsed"
    ESTIMATED = "estimated"
    PRECHECKED = "prechecked"
    GENERATING_AUDIO = "generating_audio"
    AUDIO_COMPLETED = "audio_completed"
    GENERATING_VIDEO = "generating_video"
    VIDEO_COMPLETED = "video_completed"
    SYNCING = "syncing"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="Untitled")
    script_raw: Mapped[str] = mapped_column(Text, default="")
    workflow_mode: Mapped[str] = mapped_column(
        String(20), default=WorkflowMode.AUDIO_VIDEO.value
    )
    workflow_status: Mapped[str] = mapped_column(
        String(30), default=WorkflowStatus.CREATED.value
    )
    audio_provider_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    video_provider_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voice_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sync_strategy: Mapped[str] = mapped_column(String(30), default="trim_video")
    r2_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_r2_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    # Relationships
    segments: Mapped[list["Segment"]] = relationship(  # type: ignore[name-defined]
        back_populates="project", cascade="all, delete-orphan",
        order_by="Segment.segment_number",
    )
    jobs: Mapped[list["Job"]] = relationship(  # type: ignore[name-defined]
        back_populates="project", cascade="all, delete-orphan",
    )
    thumbnails: Mapped[list["VideoThumbnail"]] = relationship(  # type: ignore[name-defined]
        "VideoThumbnail", back_populates="project", cascade="all, delete-orphan"
    )

