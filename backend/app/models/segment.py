"""Segment model — one parsed segment of a script."""

from __future__ import annotations

import enum

from typing import Optional

from sqlalchemy import Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SegmentStatus(str, enum.Enum):
    """Per-segment processing status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    segment_number: Mapped[int] = mapped_column(Integer)
    text_content: Mapped[str] = mapped_column(Text, default="")
    char_count: Mapped[int] = mapped_column(Integer, default=0)

    # Audio status
    audio_status: Mapped[str] = mapped_column(
        String(20), default=SegmentStatus.PENDING.value
    )
    audio_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Video status
    video_status: Mapped[str] = mapped_column(
        String(20), default=SegmentStatus.PENDING.value
    )
    video_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    video_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Sync
    target_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sync_strategy_used: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    merged_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="segments")  # type: ignore[name-defined]
    assets: Mapped[list["Asset"]] = relationship(  # type: ignore[name-defined]
        back_populates="segment", cascade="all, delete-orphan",
    )
    jobs: Mapped[list["Job"]] = relationship(  # type: ignore[name-defined]
        back_populates="segment", cascade="all, delete-orphan",
    )
