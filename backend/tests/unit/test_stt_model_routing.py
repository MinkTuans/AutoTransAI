"""
Unit tests for AI Model Routing & Gemini STT Model Selection.
Verifies Single Source of Truth hierarchy, model normalization, and exact API request URLs.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from app.providers.llm.gemini_provider import normalize_gemini_model_name, GEMINI_MODEL_CANDIDATES
from app.providers.ai_router import AIRouter
from app.services.video_translator.translator_service import transcribe_audio_with_gemini


def test_normalize_gemini_model_name():
    """Verify Gemini model string normalization."""
    assert normalize_gemini_model_name("gemini-2.5-flash") == "gemini-2.5-flash"
    assert normalize_gemini_model_name("models/gemini-2.5-flash") == "gemini-2.5-flash"
    # Legacy deprecated model auto-migrated
    assert normalize_gemini_model_name("gemini-2.0-flash") == "gemini-2.5-flash"
    assert normalize_gemini_model_name(None) == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_ai_router_resolve_stt_model_hierarchy():
    """Verify AIRouter resolution hierarchy."""
    # Requested model override
    res1 = await AIRouter.resolve_stt_model(requested_model="gemini-2.5-flash")
    assert res1["model_id"] == "gemini-2.5-flash"
    assert res1["source"] == "REQUESTED MODEL"

    # Default fallback
    res2 = await AIRouter.resolve_stt_model(db=None)
    assert res2["model_id"] == "gemini-2.5-flash"


@pytest.mark.asyncio
async def test_transcribe_audio_with_gemini_uses_configured_model(tmp_path: Path):
    """Assert that transcribe_audio_with_gemini sends request using configured gemini-2.5-flash."""
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
            model_name="gemini-2.5-flash",
        )

        assert len(segments) == 1
        assert segments[0]["text"] == "Hello world"
        assert len(captured_urls) > 0
        # Verify actual API request model URL contains gemini-2.5-flash and DOES NOT contain gemini-2.0-flash
        assert "gemini-2.5-flash" in captured_urls[0]
        assert "gemini-2.0-flash" not in captured_urls[0]
