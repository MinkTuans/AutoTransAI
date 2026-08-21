"""Project-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Request body for creating a new project."""
    title: str = Field(default="Untitled", max_length=200)
    script: str = Field(..., min_length=1, description="Raw script text with segments")
    workflow_mode: str = Field(default="audio_video", pattern="^(audio_only|audio_video)$")


class SegmentSummary(BaseModel):
    """Lightweight segment info for project responses."""
    number: int
    char_count: int
    text_preview: str
    audio_status: str
    video_status: str
    audio_duration: float | None = None
    video_duration: float | None = None


class ProjectResponse(BaseModel):
    """Full project details."""
    id: str
    title: str
    workflow_mode: str
    workflow_status: str
    audio_provider_id: str | None = None
    video_provider_id: str | None = None
    voice_id: str | None = None
    voice_name: str | None = None
    sync_strategy: str
    segment_count: int = 0
    total_characters: int = 0
    segments: list[SegmentSummary] = []
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Lightweight project info for listing."""
    id: str
    title: str
    workflow_mode: str
    workflow_status: str
    segment_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectStatusResponse(BaseModel):
    """Real-time project status for progress tracking."""
    project_id: str
    workflow_status: str
    total_segments: int = 0
    audio_completed: int = 0
    video_completed: int = 0
    audio_progress_pct: float = 0.0
    video_progress_pct: float = 0.0
    current_segment: int | None = None
    current_task: str | None = None
    error_message: str | None = None
