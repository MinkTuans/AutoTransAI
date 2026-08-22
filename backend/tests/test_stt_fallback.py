"""
Unit tests for STT Provider Fallback Controls & Isolation.
Verifies that OpenAI is NOT called automatically when Gemini STT fails and ENABLE_OPENAI_FALLBACK is False.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.config import Settings
from app.services.video_translator.translator_service import speech_to_text_and_detect_language


@pytest.mark.asyncio
async def test_gemini_stt_failure_does_not_call_openai_when_fallback_disabled(monkeypatch, tmp_path):
    """Test: When Gemini fails and ENABLE_OPENAI_FALLBACK=False, OpenAI Whisper must NOT be called."""
    dummy_audio = tmp_path / "test_audio.wav"
    dummy_audio.write_bytes(b"\x00" * 2048)

    mock_settings = Settings(
        ENABLE_OPENAI_FALLBACK=False,
        GEMINI_API_KEY="dummy_gemini_key",
        OPENAI_API_KEY="dummy_openai_key"
    )

    mock_probe = AsyncMock(return_value=10.0)
    mock_gemini = AsyncMock(side_effect=RuntimeError("Gemini API connection error"))
    mock_whisper = AsyncMock(return_value=([{"number": 1, "start_time": 0.0, "end_time": 5.0, "text": "Hello"}], "English"))

    with patch("app.services.video_translator.translator_service.get_settings", return_value=mock_settings), \
         patch("app.services.video_translator.translator_service.probe_duration_async", mock_probe), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_gemini", mock_gemini), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_whisper", mock_whisper):

        with pytest.raises(RuntimeError) as exc_info:
            await speech_to_text_and_detect_language(
                dummy_audio,
                job_id="TEST-JOB-FALLBACK",
                llm_provider_id="gemini"
            )

        assert "STT FAILED" in str(exc_info.value)
        assert "Gemini STT failed" in str(exc_info.value)
        # Crucial check: Whisper MUST NOT have been called
        mock_whisper.assert_not_called()


@pytest.mark.asyncio
async def test_gemini_stt_failure_calls_openai_only_when_fallback_enabled(monkeypatch, tmp_path):
    """Test: When Gemini fails and ENABLE_OPENAI_FALLBACK=True, OpenAI Whisper IS called as fallback."""
    dummy_audio = tmp_path / "test_audio.wav"
    dummy_audio.write_bytes(b"\x00" * 2048)

    mock_settings = Settings(
        ENABLE_OPENAI_FALLBACK=True,
        GEMINI_API_KEY="dummy_gemini_key",
        OPENAI_API_KEY="dummy_openai_key"
    )

    mock_probe = AsyncMock(return_value=10.0)
    mock_gemini = AsyncMock(side_effect=RuntimeError("Gemini API connection error"))
    expected_segments = [{"number": 1, "start_time": 0.0, "end_time": 5.0, "text": "Fallback text"}]
    mock_whisper = AsyncMock(return_value=(expected_segments, "English"))

    with patch("app.services.video_translator.translator_service.get_settings", return_value=mock_settings), \
         patch("app.services.video_translator.translator_service.probe_duration_async", mock_probe), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_gemini", mock_gemini), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_whisper", mock_whisper):

        result_segs, result_lang = await speech_to_text_and_detect_language(
            dummy_audio,
            job_id="TEST-JOB-FALLBACK-ENABLED",
            llm_provider_id="gemini"
        )

        assert result_segs == expected_segments
        assert result_lang == "English"
        mock_whisper.assert_called_once()
