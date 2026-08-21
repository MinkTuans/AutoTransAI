"""Estimate-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ResourceEstimate(BaseModel):
    """Estimated resource usage for a single provider."""
    provider_id: str
    provider_name: str
    resource_type: str  # characters, credits, tokens, etc.
    estimated_usage: float
    unit: str
    available: float | None = None  # None = unknown
    sufficient: bool | None = None  # None = cannot determine


class EstimateResponse(BaseModel):
    """Full project resource estimate shown before generation."""
    project_id: str
    total_segments: int
    total_characters: int
    estimated_audio_duration_seconds: float
    estimated_video_clips: int | None = None  # None if audio-only
    estimated_video_seconds: float | None = None
    resources: list[ResourceEstimate] = []
    all_sufficient: bool | None = None  # None if any resource is unknown
    warnings: list[str] = []
