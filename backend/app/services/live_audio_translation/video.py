"""MP4 input/output adapter for the independent Gemini Live translation path."""

from __future__ import annotations

import asyncio
import json
import math
import wave
from pathlib import Path

from .audio import AudioInputError, _run


VIDEO_SUFFIXES = frozenset({".mp4"})


async def _ffmpeg(*args: str, timeout: float) -> None:
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y", *args,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        try:
            await asyncio.wait_for(process.wait(), timeout)
        except (TimeoutError, asyncio.CancelledError):
            process.kill()
            await process.wait()
            raise
        if process.returncode != 0:
            raise AudioInputError("video_processing_failed")
    except FileNotFoundError as error:
        raise AudioInputError("converter_unavailable") from error
    except TimeoutError as error:
        raise AudioInputError("conversion_timeout") from error


async def _probe_video(source: Path) -> float:
    try:
        raw = await _run("ffprobe", "-v", "error", "-show_entries",
                         "format=duration:stream=codec_type", "-of", "json", str(source), timeout=15)
        info = json.loads(raw)
        duration = float(info["format"]["duration"])
        kinds = [item["codec_type"] for item in info["streams"]]
    except (AudioInputError, ValueError, TypeError, KeyError) as error:
        if isinstance(error, AudioInputError) and error.code in {"converter_unavailable", "conversion_timeout"}:
            raise
        raise AudioInputError("unsupported_video_format") from error
    if not math.isfinite(duration) or duration <= 0 or "video" not in kinds:
        raise AudioInputError("unsupported_video_format")
    if "audio" not in kinds:
        raise AudioInputError("video_has_no_audio")
    return duration


async def extract_video_pcm(source: Path, output: Path, *, max_seconds: float) -> float:
    """Validate a short MP4 and extract only its audio as Live-ready 16 kHz PCM."""
    if source.suffix.lower() not in VIDEO_SUFFIXES or not source.is_file():
        raise AudioInputError("unsupported_video_format")
    duration = await _probe_video(source)
    if duration > max_seconds:
        raise AudioInputError("session_limit")
    await _ffmpeg("-i", str(source), "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                  "-f", "s16le", str(output), timeout=120)
    if not output.is_file() or output.stat().st_size == 0:
        raise AudioInputError("video_processing_failed")
    if output.stat().st_size / 32000 > max_seconds + 0.05:
        output.unlink(missing_ok=True)
        raise AudioInputError("session_limit")
    return duration


async def mux_translated_video(source: Path, translated: Path, output: Path) -> None:
    """Replace source audio; pad short speech without cutting original video frames."""
    video_duration = await _probe_video(source)
    try:
        with wave.open(str(translated), "rb") as audio:
            translated_duration = audio.getnframes() / audio.getframerate()
    except (OSError, ValueError, wave.Error, ZeroDivisionError) as error:
        raise AudioInputError("malformed_response") from error
    if translated_duration <= 0:
        raise AudioInputError("no_translated_audio")
    duration = max(video_duration, translated_duration)
    await _ffmpeg("-i", str(source), "-i", str(translated), "-map", "0:v:0",
                  "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-af", "apad",
                  "-t", f"{duration:.3f}", "-movflags", "+faststart", str(output), timeout=180)
    if not output.is_file() or output.stat().st_size == 0:
        raise AudioInputError("video_processing_failed")
