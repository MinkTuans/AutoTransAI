"""Edge TTS must not hang the DUB stage: timeout + skip empty text."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.providers.audio.edge_tts_provider import EdgeTTSProvider


@pytest.mark.asyncio
async def test_generate_audio_times_out_instead_of_hanging(tmp_path: Path):
    provider = EdgeTTSProvider()
    out = tmp_path / "seg.wav"

    class HangCommunicate:
        def __init__(self, *a, **k):
            pass

        async def save(self, _path):
            await asyncio.sleep(60)

    with patch("app.providers.audio.edge_tts_provider.edge_tts.Communicate", HangCommunicate):
        with patch("app.providers.audio.edge_tts_provider.TTS_SEGMENT_TIMEOUT_SEC", 0.05):
            res = await provider.generate_audio("Xin chào", "vi-VN-HoaiMyNeural", out)

    assert res.success is False
    assert "timeout" in (res.error_message or "").lower() or "timed" in (res.error_message or "").lower()


@pytest.mark.asyncio
async def test_generate_audio_skips_empty_text(tmp_path: Path):
    provider = EdgeTTSProvider()
    with patch("app.providers.audio.edge_tts_provider.edge_tts.Communicate") as comm:
        res = await provider.generate_audio("   ", "vi-VN-HoaiMyNeural", tmp_path / "empty.wav")
    assert res.success is False
    comm.assert_not_called()
