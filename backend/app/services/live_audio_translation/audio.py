"""Bounded audio decoding for Gemini Live Translation only."""

from __future__ import annotations

import asyncio
import json
import math
from pathlib import Path


SUPPORTED_SUFFIXES = frozenset({".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"})


class AudioInputError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


async def _run(*args: str, timeout: float) -> bytes:
    try:
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout)
        except (TimeoutError, asyncio.CancelledError):
            process.kill()
            await process.wait()
            raise
        if process.returncode != 0:
            raise AudioInputError("unsupported_audio_format")
        return stdout
    except FileNotFoundError as error:
        raise AudioInputError("converter_unavailable") from error
    except TimeoutError as error:
        raise AudioInputError("conversion_timeout") from error


async def convert_to_pcm(source: Path, output: Path, *, max_seconds: float) -> float:
    """Decode an audio-only file to signed 16-bit mono 16 kHz PCM."""
    if source.suffix.lower() not in SUPPORTED_SUFFIXES or not source.is_file():
        raise AudioInputError("unsupported_audio_format")
    raw = await _run("ffprobe", "-v", "error", "-show_entries",
                     "format=duration:stream=codec_type", "-of", "json", str(source), timeout=15)
    try:
        details = json.loads(raw)
        streams = details["streams"]
        duration = float(details["format"]["duration"])
    except (ValueError, TypeError, KeyError) as error:
        raise AudioInputError("unsupported_audio_format") from error
    if (not isinstance(streams, list) or not streams
            or any(not isinstance(stream, dict) or stream.get("codec_type") != "audio"
                   for stream in streams)):
        raise AudioInputError("unsupported_audio_format")
    if not math.isfinite(duration) or duration <= 0:
        raise AudioInputError("unsupported_audio_format")
    if duration > max_seconds:
        raise AudioInputError("session_limit")
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-nostdin", "-v", "error", "-i", str(source), "-vn", "-ac", "1",
            "-ar", "16000", "-f", "s16le", "-y", str(output),
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        try:
            await asyncio.wait_for(process.wait(), timeout=120)
        except (TimeoutError, asyncio.CancelledError):
            process.kill()
            await process.wait()
            raise
    except FileNotFoundError as error:
        raise AudioInputError("converter_unavailable") from error
    except TimeoutError as error:
        raise AudioInputError("conversion_timeout") from error
    if process.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        raise AudioInputError("unsupported_audio_format")
    converted_duration = output.stat().st_size / 32000
    if converted_duration > max_seconds + 0.02:
        output.unlink(missing_ok=True)
        raise AudioInputError("session_limit")
    return converted_duration
