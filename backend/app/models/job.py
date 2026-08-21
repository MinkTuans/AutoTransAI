"""Job model — individual generation task (one audio or video per segment)."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobType(str, enum.Enum):
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    SYNC = "sync"
    MERGE = "merge"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    segment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("segments.id", ondelete="CASCADE"), nullable=True
    )
    provider_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING.value)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="jobs")  # type: ignore[name-defined]
    segment: Mapped["Segment | None"] = relationship(back_populates="jobs")  # type: ignore[name-defined]
    errors: Mapped[list["Error"]] = relationship(  # type: ignore[name-defined]
        back_populates="job", cascade="all, delete-orphan",
    )
