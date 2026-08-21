from __future__ import annotations

"""
FFprobe wrapper — measures actual media duration and properties.

CRITICAL: Always use FFprobe to measure audio duration.
Never estimate duration from text length for final calculations.
"""

import json
import shutil
from pathlib import Path

from app.core import get_logger
from app.core.exceptions import FFmpegNotFoundError
from app.core.security import safe_subprocess_run

logger = get_logger(__name__)


def is_ffmpeg_installed() -> bool:
    """Check if FFmpeg and FFprobe are available in PATH."""
    return (
        shutil.which("ffmpeg") is not None
        and shutil.which("ffprobe") is not None
    )


def get_ffmpeg_version() -> str | None:
    """Get FFmpeg version string."""
    try:
        result = safe_subprocess_run(
            ["ffmpeg", "-version"],
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            # First line contains version info
            return result.stdout.split("\n")[0].strip()
    except Exception:
        pass
    return None


def probe_duration(file_path: Path) -> float:
    """
    Get the actual duration of a media file in seconds using FFprobe.

    Args:
        file_path: Path to the audio or video file.

    Returns:
        Duration in seconds.

    Raises:
        FFmpegNotFoundError: If FFprobe is not installed.
        ValueError: If duration cannot be determined.
    """
    if not is_ffmpeg_installed():
        raise FFmpegNotFoundError()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    result = safe_subprocess_run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(file_path),
        ],
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        raise ValueError(
            f"FFprobe failed for {file_path}: {result.stderr}"
        )

    try:
        data = json.loads(result.stdout)
        duration_str = data.get("format", {}).get("duration")
        if duration_str is None:
            raise ValueError(f"No duration found in FFprobe output for {file_path}")
        return round(float(duration_str), 3)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise ValueError(f"Failed to parse FFprobe output: {e}") from e


def probe_media_info(file_path: Path) -> dict:
    """
    Get detailed media information using FFprobe.

    Returns:
        Dict with format and stream information.
    """
    if not is_ffmpeg_installed():
        raise FFmpegNotFoundError()

    result = safe_subprocess_run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ],
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        raise ValueError(f"FFprobe failed: {result.stderr}")

    return json.loads(result.stdout)
