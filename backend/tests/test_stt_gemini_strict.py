"""
Unit tests verifying strict Gemini STT enforcement and fallback blocking behavior.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.services.video_translator.translator_service import speech_to_text_and_detect_language, transcribe_audio_with_gemini, transcribe_audio_with_whisper


@pytest.mark.asyncio
async def test_stt_gemini_strict_success(tmp_path):
    """Verify primary STT uses Gemini and returns transcribed segments."""
    fake_audio = tmp_path / "test.wav"
    fake_audio.write_bytes(b"RIFF....WAVEfmt ....data....")

    mock_gemini_res = (
        [{"number": 1, "start_time": 0.0, "end_time": 3.0, "text": "Hello Gemini STT"}],
        "en"
    )

    with patch("app.services.video_translator.translator_service.probe_duration_async", return_value=5.0), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_gemini", new=AsyncMock(return_value=mock_gemini_res)) as mock_gemini, \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_whisper", new=AsyncMock()) as mock_whisper, \
         patch("app.services.video_translator.translator_service.get_settings") as mock_settings:

        settings_obj = AsyncMock()
        settings_obj.DEFAULT_LLM_PROVIDER = "gemini"
        settings_obj.GEMINI_API_KEY = "AIzaFakeKey"
        settings_obj.OPENAI_API_KEY = "sk-FakeKey"
        settings_obj.ENABLE_OPENAI_FALLBACK = False
        mock_settings.return_value = settings_obj

        segs, lang = await speech_to_text_and_detect_language(fake_audio, llm_provider_id="gemini")

        assert len(segs) == 1
        assert segs[0]["text"] == "Hello Gemini STT"
        assert lang == "en"
        # Assert Gemini was called, Whisper was NOT called
        mock_gemini.assert_called_once()
        mock_whisper.assert_not_called()


@pytest.mark.asyncio
async def test_stt_gemini_failure_stops_without_calling_whisper(tmp_path):
    """Verify Gemini STT error when fallback is disabled stops execution immediately and NEVER calls Whisper."""
    fake_audio = tmp_path / "test.wav"
    fake_audio.write_bytes(b"RIFF....WAVEfmt ....data....")

    with patch("app.services.video_translator.translator_service.probe_duration_async", return_value=5.0), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_gemini", side_effect=RuntimeError("Gemini 429 Rate Limit")), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_whisper", new=AsyncMock()) as mock_whisper, \
         patch("app.services.video_translator.translator_service.get_settings") as mock_settings:

        settings_obj = AsyncMock()
        settings_obj.DEFAULT_LLM_PROVIDER = "gemini"
        settings_obj.GEMINI_API_KEY = "AIzaFakeKey"
        settings_obj.OPENAI_API_KEY = "sk-FakeKey"
        settings_obj.ENABLE_OPENAI_FALLBACK = False
        mock_settings.return_value = settings_obj

        with pytest.raises(RuntimeError) as exc_info:
            await speech_to_text_and_detect_language(fake_audio, llm_provider_id="gemini")

        assert "STT FAILED" in str(exc_info.value)
        assert "Gemini STT error occurred and Fallback is DISABLED" in str(exc_info.value) or "Gemini" in str(exc_info.value)
        # CRITICAL ASSERTION: OpenAI / Whisper was NOT called!
        mock_whisper.assert_not_called()
