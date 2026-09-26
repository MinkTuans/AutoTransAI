"""Live Audio uses an enabled Gemini Catalog credential when no Live override is set."""

import asyncio
import io
import wave
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app.models import APIKey, Provider
from app.services.credential_service import CredentialService


def _wav() -> bytes:
    data = io.BytesIO()
    with wave.open(data, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\0\0" * 2400)
    return data.getvalue()


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        await connection.run_sync(Provider.__table__.create)
        await connection.run_sync(APIKey.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add(Provider(id="gemini", name="Gemini", provider_type="llm"))
    yield sessions, tmp_path
    await engine.dispose()


async def _add_key(sessions, data_dir, secret, *, enabled=True, priority=100):
    async with sessions.begin() as db:
        service = await CredentialService.open(db, data_dir)
        key = await service.create("gemini", secret, enabled=enabled)
        if priority != 100:
            await service.set_priority(key.id, priority)
    return key.id


async def test_live_audio_uses_catalog_gemini_key_without_env_key(catalog, monkeypatch):
    from app.api.routes import live_audio_translation as routes
    from app.services.live_audio_translation.jobs import LiveJobManager

    sessions, data_dir = catalog
    await _add_key(sessions, data_dir, "synthetic-catalog-gemini-key")
    settings = SimpleNamespace(LIVE_AUDIO_TRANSLATION_ENABLED=True,
                               GEMINI_LIVE_TRANSLATE_API_KEY="",
                               GEMINI_LIVE_TRANSLATE_MODEL="gemini-3.5-live-translate-preview",
                               STORAGE_ROOT=data_dir, DATA_DIR=data_dir)
    monkeypatch.setattr(routes, "get_settings", lambda: settings)
    monkeypatch.setattr(routes, "async_session_factory", sessions, raising=False)
    seen = []

    async def convert(_source, pcm, *, max_seconds):
        pcm.write_bytes(b"\0\0" * 1600)
        return 0.1

    async def translate(_pcm, output, *, key, model, on_connected):
        seen.append((key, model))
        on_connected()
        output.write_bytes(_wav())

    manager = LiveJobManager(data_dir, convert=convert, translate=translate)
    app.dependency_overrides[routes.get_live_manager] = lambda: manager
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/live-audio-translations", files={
                "file": ("speech.wav", _wav(), "audio/wav")})
        assert response.status_code == 202
        await asyncio.wait_for(manager.jobs[response.json()["data"]["id"]].task, 1)
        assert seen == [("synthetic-catalog-gemini-key", "gemini-3.5-live-translate-preview")]
    finally:
        await manager.close()
        app.dependency_overrides.pop(routes.get_live_manager, None)


async def test_live_key_prefers_explicit_override_and_skips_disabled_catalog_key(catalog):
    from app.api.routes.live_audio_translation import resolve_live_api_key

    sessions, data_dir = catalog
    await _add_key(sessions, data_dir, "synthetic-disabled-key", enabled=False)
    settings = SimpleNamespace(GEMINI_LIVE_TRANSLATE_API_KEY="explicit-live-key", DATA_DIR=data_dir)
    assert await resolve_live_api_key(settings, sessions) == "explicit-live-key"
    settings.GEMINI_LIVE_TRANSLATE_API_KEY = ""
    assert await resolve_live_api_key(settings, sessions) is None


async def test_live_key_selects_eligible_catalog_key_by_priority(catalog):
    from app.api.routes.live_audio_translation import resolve_live_api_key

    sessions, data_dir = catalog
    await _add_key(sessions, data_dir, "synthetic-low-priority", priority=50)
    selected = await _add_key(sessions, data_dir, "synthetic-high-priority", priority=1)
    async with sessions.begin() as db:
        row = await db.get(APIKey, selected)
        row.runtime_status = "invalid"
    settings = SimpleNamespace(GEMINI_LIVE_TRANSLATE_API_KEY="", DATA_DIR=data_dir)
    assert await resolve_live_api_key(settings, sessions) == "synthetic-low-priority"


async def test_live_key_respects_provider_disable_and_key_removal(catalog):
    from app.api.routes.live_audio_translation import resolve_live_api_key

    sessions, data_dir = catalog
    key_id = await _add_key(sessions, data_dir, "synthetic-removable-key")
    settings = SimpleNamespace(GEMINI_LIVE_TRANSLATE_API_KEY="", DATA_DIR=data_dir)
    assert await resolve_live_api_key(settings, sessions) == "synthetic-removable-key"
    async with sessions.begin() as db:
        (await db.get(Provider, "gemini")).enabled = False
    assert await resolve_live_api_key(settings, sessions) is None
    async with sessions.begin() as db:
        (await db.get(Provider, "gemini")).enabled = True
        await db.delete(await db.get(APIKey, key_id))
    assert await resolve_live_api_key(settings, sessions) is None
