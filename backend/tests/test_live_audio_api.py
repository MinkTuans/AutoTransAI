"""Standalone Live Translation route and lifecycle contracts."""
import asyncio
import io
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _audio_wav() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\0\0" * 2400)
    return buffer.getvalue()


@pytest.fixture
async def live_client(tmp_path, monkeypatch):
    from app.api.routes import live_audio_translation as routes
    from app.services.live_audio_translation.jobs import LiveJobManager

    config = SimpleNamespace(
        LIVE_AUDIO_TRANSLATION_ENABLED=True,
        GEMINI_LIVE_TRANSLATE_API_KEY="synthetic-live-key",
        GEMINI_LIVE_TRANSLATE_MODEL="gemini-3.5-live-translate-preview",
        STORAGE_ROOT=tmp_path,
    )
    monkeypatch.setattr(routes, "get_settings", lambda: config)
    async def resolve_config_key(_settings, _sessions):
        return config.GEMINI_LIVE_TRANSLATE_API_KEY
    monkeypatch.setattr(routes, "resolve_live_api_key", resolve_config_key)

    async def convert(_source, pcm, *, max_seconds):
        assert max_seconds <= 300
        pcm.write_bytes(b"\0\0" * 1600)
        return 0.1

    async def translate(_pcm, output, *, key, model, on_connected):
        assert key == "synthetic-live-key"
        assert model == "gemini-3.5-live-translate-preview"
        on_connected()
        output.write_bytes(_audio_wav())

    manager = LiveJobManager(tmp_path, convert=convert, translate=translate)
    app.dependency_overrides[routes.get_live_manager] = lambda: manager
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, manager, config
    finally:
        await manager.close()
        app.dependency_overrides.pop(routes.get_live_manager, None)


async def test_live_audio_upload_status_download_and_cancel(live_client):
    client, manager, _ = live_client
    started = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")},
        data={"source_language": "auto", "target_language": "vi"})
    assert started.status_code == 202
    job_id = started.json()["data"]["id"]
    for _ in range(20):
        status = (await client.get(f"/api/live-audio-translations/{job_id}")).json()["data"]
        if status["status"] == "completed":
            break
        await asyncio.sleep(0.01)
    assert status["status"] == "completed"
    assert status["source_language"] == "auto" and status["target_language"] == "vi"
    result = await client.get(f"/api/live-audio-translations/{job_id}/audio")
    assert result.status_code == 200 and result.headers["content-type"].startswith("audio/wav")
    assert result.content == _audio_wav()
    assert (await client.post(f"/api/live-audio-translations/{job_id}/cancel")).status_code == 409
    assert manager.jobs[job_id].directory.is_dir()


async def test_live_audio_config_and_format_errors_do_not_start_job(live_client):
    client, manager, config = live_client
    config.GEMINI_LIVE_TRANSLATE_API_KEY = ""
    missing = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    assert missing.status_code == 503 and missing.json()["detail"] == "missing_api_key"
    config.GEMINI_LIVE_TRANSLATE_API_KEY = "synthetic-live-key"
    invalid = await client.post("/api/live-audio-translations", files={
        "file": ("speech.txt", _audio_wav(), "text/plain")})
    assert invalid.status_code == 415 and invalid.json()["detail"] == "unsupported_audio_format"
    assert manager.jobs == {}
    config.LIVE_AUDIO_TRANSLATION_ENABLED = False
    disabled = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    assert disabled.status_code == 503 and disabled.json()["detail"] == "feature_disabled"
    config.LIVE_AUDIO_TRANSLATION_ENABLED = True
    config.GEMINI_LIVE_TRANSLATE_MODEL = ""
    missing_model = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    assert missing_model.status_code == 503 and missing_model.json()["detail"] == "model_unavailable"
    config.GEMINI_LIVE_TRANSLATE_MODEL = "gemini-3.5-live-translate-preview"
    invalid_source = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")}, data={"source_language": "en"})
    assert invalid_source.status_code == 422


async def test_live_audio_rejects_large_upload_and_excess_concurrent_session(live_client, monkeypatch):
    from app.api.routes import live_audio_translation as routes
    client, manager, _ = live_client
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 8)
    large = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    assert large.status_code == 413 and manager.jobs == {}
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 25 * 1024 * 1024)
    manager.max_active = 1
    started_event = asyncio.Event()

    async def slow(_pcm, _output, *, key, model, on_connected):
        on_connected()
        started_event.set()
        await asyncio.Event().wait()

    manager.translate = slow
    first = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    await asyncio.wait_for(started_event.wait(), 1)
    second = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    assert second.status_code == 429 and second.json()["detail"] == "session_limit"
    assert len(manager.jobs) == 1
    await client.post(f"/api/live-audio-translations/{first.json()['data']['id']}/cancel")


async def test_live_audio_upstream_error_is_status_and_never_falls_back(live_client):
    from app.services.live_audio_translation.live_api import LiveTranslationError
    client, manager, _ = live_client

    async def fails(_pcm: Path, _output: Path, *, key: str, model: str, on_connected):
        on_connected()
        raise LiveTranslationError("quota_or_rate_limit")

    manager.translate = fails
    started = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    job_id = started.json()["data"]["id"]
    for _ in range(20):
        status = (await client.get(f"/api/live-audio-translations/{job_id}")).json()["data"]
        if status["status"] == "failed":
            break
        await asyncio.sleep(0.01)
    assert status["status"] == "failed" and status["error_code"] == "quota_or_rate_limit"
    assert (await client.get(f"/api/live-audio-translations/{job_id}/audio")).status_code == 409


async def test_live_audio_cancel_stops_only_its_session(live_client):
    client, manager, _ = live_client
    started_event = asyncio.Event()

    async def slow(_pcm, _output, *, key, model, on_connected):
        on_connected()
        started_event.set()
        await asyncio.Event().wait()

    manager.translate = slow
    started = await client.post("/api/live-audio-translations", files={
        "file": ("speech.wav", _audio_wav(), "audio/wav")})
    job_id = started.json()["data"]["id"]
    await asyncio.wait_for(started_event.wait(), 1)
    cancelled = await client.post(f"/api/live-audio-translations/{job_id}/cancel")
    assert cancelled.status_code == 200
    assert (await client.get(f"/api/live-audio-translations/{job_id}")).json()["data"]["status"] == "cancelled"
