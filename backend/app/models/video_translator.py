"""
Video Translator ORM models.

Stores VideoAsset metadata, VideoTranslationJob pipeline states,
and per-segment timestamped transcript translations.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssetSourceType(str, enum.Enum):
    UPLOAD = "upload"
    URL = "url"


class TranslationJobStatus(str, enum.Enum):
    CREATED = "created"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    EXTRACTING_AUDIO = "extracting_audio"
    STT = "stt"
    LANGUAGE_DETECTED = "language_detected"
    TRANSLATED = "translated"
    SEGMENT_EDITING = "segment_editing"
    GENERATING_TTS = "generating_tts"
    SYNCING_AUDIO = "syncing_audio"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioMixMode(str, enum.Enum):
    MUTE = "mute"      # Mute original audio completely
    DUCK = "duck"      # Duck original audio (lower volume)
    KEEP = "keep"      # Keep original audio intact


class VideoAsset(Base):
    __tablename__ = "video_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(20), default=AssetSourceType.URL.value)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), default="Untitled Video")
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    audio_available: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="ready")
    r2_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    jobs: Mapped[list["VideoTranslationJob"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )


class VideoTranslationJob(Base):
    __tablename__ = "video_translation_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("video_assets.id", ondelete="CASCADE"), index=True
    )
    source_language: Mapped[str] = mapped_column(String(20), default="auto")
    detected_language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    target_language: Mapped[str] = mapped_column(String(20), default="vi")
    audio_provider_id: Mapped[Optional[str]] = mapped_column(String(50), default="edge_tts")
    llm_provider_id: Mapped[Optional[str]] = mapped_column(String(50), default="gemini")
    voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voice_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    original_audio_mode: Mapped[str] = mapped_column(String(20), default=AudioMixMode.MUTE.value)
    status: Mapped[str] = mapped_column(String(30), default=TranslationJobStatus.CREATED.value)
    stage: Mapped[str] = mapped_column(String(50), default="QUEUED")
    stage_progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    overall_progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[str] = mapped_column(String(100), default="Khởi tạo")
    pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    ffmpeg_stats_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_segments_count: Mapped[int] = mapped_column(Integer, default=0)
    total_segments_count: Mapped[int] = mapped_column(Integer, default=0)
    output_video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    r2_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_cleaned: Mapped[bool] = mapped_column(Boolean, default=False)
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
    asset: Mapped["VideoAsset"] = relationship(back_populates="jobs")
    segments: Mapped[list["VideoTranslationSegment"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="VideoTranslationSegment.segment_number"
    )


class VideoTranslationSegment(Base):
    __tablename__ = "video_translation_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("video_translation_jobs.id", ondelete="CASCADE"), index=True
    )
    segment_number: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[float] = mapped_column(Float, default=0.0)
    end_time: Mapped[float] = mapped_column(Float, default=0.0)
    original_text: Mapped[str] = mapped_column(Text, default="")
    translated_text: Mapped[str] = mapped_column(Text, default="")
    tts_audio_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tts_audio_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    synced_audio_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")

    # Relationships
    job: Mapped["VideoTranslationJob"] = relationship(back_populates="segments")
