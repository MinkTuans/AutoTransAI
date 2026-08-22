"""
Unit tests for Gemini Speech-to-Text service and audio chunking.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.video_translator.translator_service import transcribe_audio_with_gemini
from app.media.ffmpeg_process import run_ffmpeg_with_progress_async


def test_gemini_imports():
    """Verify Gemini STT function can be imported and uses valid FFmpeg runner."""
    from app.services.video_translator.translator_service import transcribe_audio_with_gemini
    assert callable(transcribe_audio_with_gemini)
    assert callable(run_ffmpeg_with_progress_async)


@pytest.mark.anyio
async def test_transcribe_audio_with_gemini_mocked(tmp_path):
    """Verify Gemini STT audio flow with mocked settings and HTTP response."""
    dummy_audio = tmp_path / "test_audio.wav"
    dummy_audio.write_bytes(b"RIFF dummy wav data " * 100)

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{\n  "language": "English",\n  "segments": [\n    {"start_time": 0.0, "end_time": 2.5, "text": "Hello world"}\n  ]\n}'
                        }
                    ]
                }
            }
        ]
    }

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = mock_gemini_response

    with patch("app.services.video_translator.translator_service.settings.GEMINI_API_KEY", "mock_key"), \
         patch("app.services.video_translator.translator_service.probe_duration_async", AsyncMock(return_value=2.5)), \
         patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_res)):

        segments, lang = await transcribe_audio_with_gemini(dummy_audio, job_id="VT-TEST-GEMINI")

        assert lang == "English"
        assert len(segments) == 1
        assert segments[0]["text"] == "Hello world"
        assert segments[0]["start_time"] == 0.0
        assert segments[0]["end_time"] == 2.5


@pytest.mark.anyio
async def test_transcribe_audio_with_gemini_large_audio_chunking(tmp_path):
    """Verify large audio chunking uses run_ffmpeg_with_progress_async successfully."""
    dummy_large_audio = tmp_path / "large_test_audio.wav"
    # Make file_size_mb > 12MB (e.g. 13MB)
    dummy_large_audio.write_bytes(b"0" * (13 * 1024 * 1024))

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{\n  "language": "English",\n  "segments": [\n    {"start_time": 0.0, "end_time": 5.0, "text": "Chunk transcription"}\n  ]\n}'
                        }
                    ]
                }
            }
        ]
    }

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = mock_gemini_response

    async def mock_run_ffmpeg(cmd, timeout=120.0):
        # Create chunk file specified in cmd
        out_chunk = Path(cmd[-1])
        out_chunk.write_bytes(b"RIFF chunk wav data")
        return {"status": "COMPLETED", "progress_pct": 100.0}

    with patch("app.services.video_translator.translator_service.settings.GEMINI_API_KEY", "mock_key"), \
         patch("app.services.video_translator.translator_service.probe_duration_async", AsyncMock(return_value=350.0)), \
         patch("app.services.video_translator.translator_service.run_ffmpeg_with_progress_async", side_effect=mock_run_ffmpeg) as mock_ffmpeg, \
         patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_res)):

        segments, lang = await transcribe_audio_with_gemini(dummy_large_audio, job_id="VT-TEST-CHUNK")

        assert mock_ffmpeg.called
        assert len(segments) > 0
        assert lang == "English"


@pytest.mark.anyio
async def test_transcribe_audio_with_gemini_chunk_creation_failure(tmp_path):
    """Verify error is raised and cleanup happens if chunk creation fails."""
    dummy_large_audio = tmp_path / "large_test_audio.wav"
    dummy_large_audio.write_bytes(b"0" * (13 * 1024 * 1024))

    async def mock_run_ffmpeg_fail(cmd, timeout=120.0):
        # Do NOT create the chunk file
        return {"status": "FAILED", "progress_pct": 0.0}

    with patch("app.services.video_translator.translator_service.settings.GEMINI_API_KEY", "mock_key"), \
         patch("app.services.video_translator.translator_service.probe_duration_async", AsyncMock(return_value=350.0)), \
         patch("app.services.video_translator.translator_service.run_ffmpeg_with_progress_async", side_effect=mock_run_ffmpeg_fail):

        with pytest.raises(RuntimeError, match="Audio chunk file lost or failed to generate"):
            await transcribe_audio_with_gemini(dummy_large_audio, job_id="VT-TEST-FAIL")

    # Confirm temp chunk directory was cleaned up
    temp_dir = dummy_large_audio.parent / "gemini_chunks_VT-TEST-FAIL"
    assert not temp_dir.exists()

