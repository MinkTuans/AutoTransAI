"""
Unit tests for AI Model Routing & Gemini STT Model Selection.
Verifies Single Source of Truth hierarchy, model string cleaning, and exact API request URLs.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from app.providers.llm.gemini_provider import strip_gemini_model_prefix
from app.services.model_resolver import AIModelResolver
from app.services.video_translator.translator_service import transcribe_audio_with_gemini


def test_strip_gemini_model_prefix():
    """Verify Gemini model prefix stripping."""
    assert strip_gemini_model_prefix("gemini-2.0-flash") == "gemini-2.0-flash"
    assert strip_gemini_model_prefix("models/gemini-2.0-flash") == "gemini-2.0-flash"
    assert strip_gemini_model_prefix("models/gemini-3.5-flash-lite") == "gemini-3.5-flash-lite"
    assert strip_gemini_model_prefix(None) == ""


@pytest.mark.asyncio
async def test_ai_model_resolver_stt_hierarchy():
    """Verify AIModelResolver resolution hierarchy."""
    # Explicit requested model override
    res1 = await AIModelResolver.resolve_stt_model(db=None, requested_model="gemini-2.0-flash")
    assert res1["model_id"] == "gemini-2.0-flash"
    assert res1["source"] == "REQUESTED MODEL"


@pytest.mark.asyncio
async def test_transcribe_audio_with_gemini_uses_configured_model(tmp_path: Path):
    """Assert that transcribe_audio_with_gemini sends request using configured gemini-2.0-flash."""
    dummy_audio = tmp_path / "test_audio.wav"
    dummy_audio.write_bytes(b"RIFF" + b"\x00" * 100)

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

    captured_urls = []

    async def mock_post(url, json=None):
        captured_urls.append(url)
        return mock_res

    with patch("httpx.AsyncClient.post", side_effect=mock_post), \
         patch("app.services.video_translator.translator_service.probe_duration_async", AsyncMock(return_value=2.5)), \
         patch("app.services.video_translator.translator_service.settings.GEMINI_API_KEY", "test_key_123"):

        segments, lang = await transcribe_audio_with_gemini(
            dummy_audio,
            job_id="VT-ROUTING-TEST",
            model_name="gemini-2.0-flash",
        )

        assert len(segments) == 1
        assert segments[0]["text"] == "Hello world"
        assert len(captured_urls) > 0
        assert "gemini-2.0-flash" in captured_urls[0]
