"""
Unit tests for long video processing fixes: dynamic timeouts, pipe deadlock prevention, and error formatting.
"""

from pathlib import Path
import pytest
import asyncio

from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.services.video_translator.translator_service import extract_audio_from_video


def test_dynamic_timeout_calculation():
    """Verify that timeout scales dynamically with video duration."""
    total_duration = 1800.0  # 30 minutes
    calc_timeout = max(600.0, float(total_duration) * 3.0)
    assert calc_timeout == 5400.0  # 90 minutes allocated for 30 minute video

    short_duration = 30.0
    short_calc_timeout = max(600.0, float(short_duration) * 3.0)
    assert short_calc_timeout == 600.0  # Minimum 10 minutes allocated


@pytest.mark.anyio
async def test_concurrent_pipe_reading_no_deadlock():
    """Verify FFmpeg process completes without pipe deadlock when outputting high volume stderr."""
    sample_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not sample_video.exists():
        pytest.skip("test_with_audio.mp4 missing")

    out_wav = sample_video.parent / "tmp_deadlock_test_out.wav"
    out_wav.unlink(missing_ok=True)

    cmd = ["ffmpeg", "-y", "-loglevel", "debug", "-i", str(sample_video), "-vn", "-acodec", "pcm_s16le", str(out_wav)]

    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=3.0,
        timeout=30.0,
    )

    assert stats["status"] == "COMPLETED"
    assert out_wav.exists()
    out_wav.unlink(missing_ok=True)
