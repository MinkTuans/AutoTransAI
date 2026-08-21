"""
Sync strategies — handles audio/video duration mismatch.

Each segment may have different audio/video durations.
This module decides how to adjust them to match.
"""

import enum
from dataclasses import dataclass
from pathlib import Path

from app.core import get_logger
from app.media.ffmpeg import trim_video, loop_video, pad_video_with_black

logger = get_logger(__name__)


class SyncStrategy(str, enum.Enum):
    """Available audio/video sync strategies."""
    TRIM_VIDEO = "trim_video"       # Trim video to match audio duration
    LOOP_VIDEO = "loop_video"       # Loop video to match audio duration
    PAD_VIDEO = "pad_video"         # Pad video with freeze frame / black
    SPEED_VIDEO = "speed_video"     # Speed up/slow down video (not recommended)
    NONE = "none"                   # No adjustment (audio-only mode)


@dataclass
class SyncPlan:
    """Planned sync operation for a segment."""
    segment_number: int
    audio_duration: float
    video_duration: float
    strategy: SyncStrategy
    target_duration: float
    adjustment_seconds: float  # positive = extend video, negative = trim


def plan_sync(
    segment_number: int,
    audio_duration: float,
    video_duration: float,
    default_strategy: str = "trim_video",
    tolerance: float = 0.5,
) -> SyncPlan:
    """
    Determine the sync strategy for a segment based on duration difference.

    Args:
        segment_number: The segment number.
        audio_duration: Actual audio duration in seconds.
        video_duration: Actual video duration in seconds.
        default_strategy: Default strategy when video is longer.
        tolerance: Duration difference below which no adjustment is needed.

    Returns:
        SyncPlan with the determined strategy.
    """
    diff = video_duration - audio_duration  # positive = video is longer

    if abs(diff) <= tolerance:
        # Close enough — no adjustment needed
        return SyncPlan(
            segment_number=segment_number,
            audio_duration=audio_duration,
            video_duration=video_duration,
            strategy=SyncStrategy.NONE,
            target_duration=audio_duration,
            adjustment_seconds=0.0,
        )

    if diff > 0:
        # Video is longer than audio → trim video
        strategy = SyncStrategy(default_strategy)
        target = audio_duration
    else:
        # Audio is longer than video → extend video
        strategy = SyncStrategy.LOOP_VIDEO
        target = audio_duration

    plan = SyncPlan(
        segment_number=segment_number,
        audio_duration=audio_duration,
        video_duration=video_duration,
        strategy=strategy,
        target_duration=target,
        adjustment_seconds=round(-diff, 3),
    )

    logger.info(
        "Sync plan created",
        segment=segment_number,
        audio_dur=audio_duration,
        video_dur=video_duration,
        strategy=strategy.value,
        target=target,
    )

    return plan


from app.media.ffmpeg import (
    trim_video,
    loop_video,
    pad_video_with_black,
    trim_video_async,
    loop_video_async,
    pad_video_with_black_async,
)


async def execute_sync_async(
    plan: SyncPlan,
    video_input_path: Path,
    video_output_path: Path,
) -> Path:
    """Execute a sync plan asynchronously (non-blocking)."""
    if plan.strategy == SyncStrategy.NONE:
        logger.debug("No sync needed", segment=plan.segment_number)
        return video_input_path

    if plan.strategy == SyncStrategy.TRIM_VIDEO:
        return await trim_video_async(video_input_path, video_output_path, plan.target_duration)

    if plan.strategy == SyncStrategy.LOOP_VIDEO:
        return await loop_video_async(video_input_path, video_output_path, plan.target_duration)

    if plan.strategy == SyncStrategy.PAD_VIDEO:
        pad_duration = plan.target_duration - plan.video_duration
        return await pad_video_with_black_async(video_input_path, video_output_path, pad_duration)

    logger.warning("Unknown sync strategy", strategy=plan.strategy.value)
    return video_input_path


def execute_sync(
    plan: SyncPlan,
    video_input_path: Path,
    video_output_path: Path,
) -> Path:
    """
    Execute a sync plan — adjust video duration to match audio.

    Args:
        plan: The SyncPlan to execute.
        video_input_path: Original video file.
        video_output_path: Where to save the adjusted video.

    Returns:
        Path to the adjusted video (may be same as input if no adjustment needed).
    """
    if plan.strategy == SyncStrategy.NONE:
        logger.debug("No sync needed", segment=plan.segment_number)
        return video_input_path

    if plan.strategy == SyncStrategy.TRIM_VIDEO:
        return trim_video(video_input_path, video_output_path, plan.target_duration)

    if plan.strategy == SyncStrategy.LOOP_VIDEO:
        return loop_video(video_input_path, video_output_path, plan.target_duration)

    if plan.strategy == SyncStrategy.PAD_VIDEO:
        pad_duration = plan.target_duration - plan.video_duration
        return pad_video_with_black(video_input_path, video_output_path, pad_duration)

    logger.warning("Unknown sync strategy", strategy=plan.strategy.value)
    return video_input_path

