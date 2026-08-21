"""Segment-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SegmentResponse(BaseModel):
    """Full segment details."""
    id: int
    segment_number: int
    text_content: str
    char_count: int
    audio_status: str
    video_status: str
    audio_duration: float | None = None
    video_duration: float | None = None
    target_duration: float | None = None
    sync_strategy_used: str | None = None
    audio_error_message: str | None = None
    video_error_message: str | None = None
    video_error_details: str | None = None

    model_config = {"from_attributes": True}
