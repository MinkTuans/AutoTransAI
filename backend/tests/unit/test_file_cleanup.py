"""
Unit tests for FileCleanupService, job workspace cleanup, asset reference counting, and orphan scanning.
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.cleanup_service import FileCleanupService
from app.config import get_settings

settings = get_settings()


def test_cleanup_job_workspace_purges_temps(tmp_path):
    """Verify job workspace cleanup removes temporary dirs/audio files while keeping job.log and final video."""
    mock_job_dir = tmp_path / "translator" / "jobs" / "VT-TEST-CLEANUP"
    mock_job_dir.mkdir(parents=True)

    # Create permanent files
    (mock_job_dir / "job.log").write_text("job log content")
    (mock_job_dir / "final_dubbed_video.mp4").write_bytes(b"video bytes")

    # Create temp subdirectories and files
    tts_dir = mock_job_dir / "tts"
    tts_dir.mkdir()
    (tts_dir / "seg_001.wav").write_bytes(b"wav bytes")

    synced_dir = mock_job_dir / "synced"
    synced_dir.mkdir()
    (synced_dir / "seg_001_synced.wav").write_bytes(b"wav bytes")

    chunks_dir = mock_job_dir / "chunks"
    chunks_dir.mkdir()
    (chunks_dir / "chunk_000.wav").write_bytes(b"wav bytes")

    work_dir = mock_job_dir / "work"
    work_dir.mkdir()
    (work_dir / "combined.wav").write_bytes(b"wav bytes")

    (mock_job_dir / "extracted_audio.wav").write_bytes(b"extracted wav")

    with patch("app.services.cleanup_service.settings.DATA_DIR", tmp_path):
        res = FileCleanupService.cleanup_job_workspace("VT-TEST-CLEANUP", keep_logs=True, keep_final_video=True)

    # Check files directly in mock_job_dir
    assert (mock_job_dir / "job.log").exists()
    assert (mock_job_dir / "final_dubbed_video.mp4").exists()

    assert not (mock_job_dir / "extracted_audio.wav").exists()
    assert not tts_dir.exists()
    assert not synced_dir.exists()
    assert not chunks_dir.exists()
    assert not work_dir.exists()


def test_cleanup_job_workspace_idempotent(tmp_path):
    """Verify running cleanup_job_workspace multiple times is idempotent and does not crash."""
    mock_job_dir = tmp_path / "VT-TEST-IDEM"
    mock_job_dir.mkdir(parents=True)

    with patch("app.services.cleanup_service.settings.DATA_DIR", tmp_path.parent):
        res1 = FileCleanupService.cleanup_job_workspace("VT-TEST-IDEM")
        res2 = FileCleanupService.cleanup_job_workspace("VT-TEST-IDEM")
        res3 = FileCleanupService.cleanup_job_workspace("NON-EXISTENT-JOB")

    assert res1["status"] in ["success", "job_dir_not_found"]
    assert res2["status"] in ["success", "job_dir_not_found"]
    assert res3["status"] == "job_dir_not_found"
