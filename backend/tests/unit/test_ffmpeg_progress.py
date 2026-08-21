"""
Unit tests for FFmpeg Real-time Progress parsing, process management, and logging.
"""

from pathlib import Path
import pytest
import asyncio

from app.media.ffmpeg_process import run_ffmpeg_with_progress_async, FFmpegExecutionError
from app.services.video_translator.translator_service import calculate_overall_progress
from app.core.job_logger import log_job_event, get_job_logs


@pytest.mark.anyio
async def test_ffmpeg_progress_parsing():
    """Test A: Verify real-time FFmpeg out_time and progress parsing with valid video file."""
    sample_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not sample_video.exists():
        pytest.skip("sample_video test_with_audio.mp4 does not exist")


    out_audio = sample_video.parent / "tmp_unit_progress_out.wav"
    out_audio.unlink(missing_ok=True)

    progress_events = []

    def on_prog(stats):
        progress_events.append(dict(stats))

    cmd = [
        "ffmpeg", "-y",
        "-i", str(sample_video),
        "-vn",
        "-acodec", "pcm_s16le",
        str(out_audio),
    ]

    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=5.0,
        on_progress=on_prog,
        timeout=30.0,
    )

    out_audio.unlink(missing_ok=True)

    assert stats["status"] == "COMPLETED"
    assert stats["progress_pct"] == 100.0
    assert len(progress_events) > 0


@pytest.mark.anyio
async def test_ffmpeg_process_failure_handling():
    """Test B: Verify FFmpeg process error handling on non-zero exit code."""
    cmd = ["ffmpeg", "-y", "-i", "non_existent_file_xyz.mp4", "-vn", "out.wav"]

    with pytest.raises(FFmpegExecutionError) as excinfo:
        await run_ffmpeg_with_progress_async(cmd, timeout=10.0)

    assert excinfo.value.exit_code != 0
    assert excinfo.value.stderr_text != ""


def test_calculate_overall_progress():
    """Test stage weight and overall progress calculation."""
    assert calculate_overall_progress("EXTRACTING_AUDIO", 50.0) == 15.0  # 10 + 10*0.5
    assert calculate_overall_progress("COMPLETED", 100.0) == 100.0
    assert calculate_overall_progress("SEGMENT_EDITING", 0.0) == 60.0


def test_job_logger():
    """Test job-specific logger formatting and retrieval."""
    job_id = "VT-TEST-LOG"
    log_job_event(job_id, "TEST_STAGE", "Executing test logger entry")
    logs = get_job_logs(job_id)

    assert job_id in logs
    assert "TEST_STAGE" in logs
    assert "Executing test logger entry" in logs


@pytest.mark.anyio
async def test_ffmpeg_subprocess_spawn_on_windows():
    """Test spawning FFmpeg subprocess on Windows: PID captured, no NotImplementedError, out file produced."""
    sample_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not sample_video.exists():
        pytest.skip("test_with_audio.mp4 missing")

    out_wav = sample_video.parent / "tmp_win_test_out.wav"
    out_wav.unlink(missing_ok=True)

    captured_pid = []

    def on_pid(pid):
        captured_pid.append(pid)

    cmd = ["ffmpeg", "-y", "-i", str(sample_video), "-vn", "-acodec", "pcm_s16le", str(out_wav)]

    stats = await run_ffmpeg_with_progress_async(
        cmd,
        total_duration=3.0,
        on_pid=on_pid,
        timeout=30.0,
    )

    assert len(captured_pid) == 1
    assert captured_pid[0] > 0
    assert stats["status"] == "COMPLETED"
    assert out_wav.exists()
    assert out_wav.stat().st_size > 0

    out_wav.unlink(missing_ok=True)

