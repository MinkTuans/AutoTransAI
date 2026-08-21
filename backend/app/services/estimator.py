"""
Resource estimator — calculates expected resource usage before generation.

All estimates are clearly marked as estimates, never presented as actual values.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core import get_logger
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Rough estimation constants (conservative)
# Average speaking rate: ~150 words per minute, ~13 chars per second
CHARS_PER_SECOND_ESTIMATE = 13.0
# Gemini token estimation: ~4 chars per token
CHARS_PER_TOKEN_ESTIMATE = 4.0


@dataclass
class SegmentEstimate:
    """Estimated resources for a single segment."""
    segment_number: int
    char_count: int
    estimated_audio_seconds: float
    estimated_video_seconds: float


@dataclass
class ProjectEstimate:
    """Aggregated resource estimate for a full project."""
    total_segments: int
    total_characters: int
    estimated_audio_duration_seconds: float
    estimated_video_clips: int
    estimated_video_seconds: float
    estimated_input_tokens: int  # For LLM if used
    estimated_audio_characters: int  # For TTS providers
    segment_estimates: list[SegmentEstimate]


def estimate_audio_duration(char_count: int) -> float:
    """
    Estimate audio duration in seconds from character count.

    This is a rough estimate. Actual duration MUST be measured with FFprobe
    after generation. This estimate is used only for pre-generation planning.

    Args:
        char_count: Number of characters in the text.

    Returns:
        Estimated duration in seconds.
    """
    return char_count / CHARS_PER_SECOND_ESTIMATE


def estimate_project(
    segments: list[dict],
    workflow_mode: str = "audio_video",
    video_target_duration: int | None = None,
) -> ProjectEstimate:
    """
    Calculate full project resource estimate.

    Args:
        segments: List of dicts with 'number' and 'char_count' keys.
        workflow_mode: "audio_only" or "audio_video".
        video_target_duration: Target video clip duration in seconds.

    Returns:
        ProjectEstimate with all resource calculations.
    """
    video_duration = video_target_duration or settings.VIDEO_TARGET_DURATION
    total_chars = sum(s["char_count"] for s in segments)
    segment_estimates = []

    for seg in segments:
        est_audio = estimate_audio_duration(seg["char_count"])
        est_video = float(video_duration) if workflow_mode == "audio_video" else 0.0
        segment_estimates.append(SegmentEstimate(
            segment_number=seg["number"],
            char_count=seg["char_count"],
            estimated_audio_seconds=round(est_audio, 2),
            estimated_video_seconds=est_video,
        ))

    total_audio = sum(s.estimated_audio_seconds for s in segment_estimates)
    total_video_clips = len(segments) if workflow_mode == "audio_video" else 0
    total_video_seconds = total_video_clips * video_duration

    estimate = ProjectEstimate(
        total_segments=len(segments),
        total_characters=total_chars,
        estimated_audio_duration_seconds=round(total_audio, 2),
        estimated_video_clips=total_video_clips,
        estimated_video_seconds=float(total_video_seconds),
        estimated_input_tokens=total_chars // int(CHARS_PER_TOKEN_ESTIMATE),
        estimated_audio_characters=total_chars,
        segment_estimates=segment_estimates,
    )

    logger.info(
        "Project estimated",
        total_segments=estimate.total_segments,
        total_characters=estimate.total_characters,
        estimated_audio_seconds=estimate.estimated_audio_duration_seconds,
        estimated_video_clips=estimate.estimated_video_clips,
    )

    return estimate
