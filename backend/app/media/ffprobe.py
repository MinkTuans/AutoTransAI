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


import sys
import os

def _ensure_ffmpeg_in_path() -> None:
    """Ensure virtualenv Scripts/bin directory is in PATH."""
    scripts_dir = str(Path(sys.prefix) / "Scripts")
    bin_dir = str(Path(sys.prefix) / "bin")
    current_path = os.environ.get("PATH", "")
    for d in (scripts_dir, bin_dir):
        if Path(d).exists() and d not in current_path:
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")

def get_ffmpeg_executable() -> str:
    """Get path to FFmpeg binary using system PATH or imageio_ffmpeg fallback."""
    _ensure_ffmpeg_in_path()
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

import re

def is_ffmpeg_installed() -> bool:
    """Check if FFmpeg is available."""
    try:
        exe = get_ffmpeg_executable()
        return bool(exe) and (shutil.which(exe) is not None or Path(exe).exists())
    except Exception:
        return False


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


import asyncio


async def probe_duration_async(file_path: Path) -> float:
    """Async non-blocking version of probe_duration."""
    return await asyncio.to_thread(probe_duration, file_path)


def probe_duration(file_path: Path) -> float:
    """
    Get the actual duration of a media file in seconds using FFprobe or FFmpeg.

    Args:
        file_path: Path to the audio or video file.

    Returns:
        Duration in seconds.

    Raises:
        FFmpegNotFoundError: If FFmpeg is not installed.
        ValueError: If duration cannot be determined.
    """
    if not is_ffmpeg_installed():
        raise FFmpegNotFoundError()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Try ffprobe if available
    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        result = safe_subprocess_run(
            [
                ffprobe_bin,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(file_path),
            ],
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                duration_str = data.get("format", {}).get("duration")
                if duration_str is not None:
                    return round(float(duration_str), 3)
            except Exception:
                pass

    # 2. Universal FFmpeg duration probe fallback
    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
    result = safe_subprocess_run(
        [ffmpeg_bin, "-i", str(file_path)],
        timeout=30,
        check=False,
    )
    output = (result.stderr or "") + (result.stdout or "")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if match:
        h, m, s = float(match.group(1)), float(match.group(2)), float(match.group(3))
        return round(h * 3600 + m * 60 + s, 3)

    raise ValueError(f"Could not determine duration for media file {file_path}")


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


async def probe_media_info_async(file_path: Path) -> dict:
    """Async non-blocking version of probe_media_info."""
    return await asyncio.to_thread(probe_media_info, file_path)


def get_video_metadata(file_path: Path) -> dict:
    """
    Extract video metadata (duration, width, height, format, has_audio) from media file.
    """
    info = probe_media_info(file_path)
    streams = info.get("streams", [])
    fmt = info.get("format", {})

    duration = float(fmt.get("duration", 0.0))
    format_name = fmt.get("format_name", "mp4").split(",")[0]
    file_size = int(fmt.get("size", file_path.stat().st_size if file_path.exists() else 0))

    width = 0
    height = 0
    has_audio = False

    for s in streams:
        c_type = s.get("codec_type")
        if c_type == "video" and not width:
            width = int(s.get("width", 0))
            height = int(s.get("height", 0))
        elif c_type == "audio":
            has_audio = True

    return {
        "duration": round(duration, 2),
        "width": width,
        "height": height,
        "format": format_name,
        "file_size": file_size,
        "has_audio": has_audio,
    }


async def get_video_metadata_async(file_path: Path) -> dict:
    return await asyncio.to_thread(get_video_metadata, file_path)

