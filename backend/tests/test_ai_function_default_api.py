"""Canonical function-default writes use disposable SQLite and no outbound calls."""
from datetime import datetime
import logging
import socket

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, event, select
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.main import app
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.credential_service import CredentialService


@pytest.fixture
async def default_api(tmp_path, monkeypatch):
    from app.api.routes import ai_function_defaults

    monkeypatch.setattr(socket.socket, "connect", lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("Unexpected outbound connection")))
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'defaults.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for table in (Provider, APIKey, CatalogModel, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(table.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def isolated_db():
        async with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = isolated_db
    app.dependency_overrides[ai_function_defaults.get_function_sessions] = lambda: sessions
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions, tmp_path
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(ai_function_defaults.get_function_sessions, None)
        await engine.dispose()


async def seed(sessions, path, *, provider="openai", capability="STT", model_id="catalog-id",
               source="discovered", status="FULL_UNKNOWN", capabilities=(), with_key=True,
               with_edge=True, model_enabled=True, provider_enabled=True, retired=False):
    async with sessions.begin() as db:
        db.add(Provider(id=provider, name=provider, provider_type="llm", enabled=provider_enabled))
        await db.flush()
        db.add(AIFunctionConfig(function_id="stt", function_name="Speech", capability=capability,
                                primary_provider_id="legacy", model_id="legacy-remote",
                                configuration_error="catalog_model_retired", fallback_enabled=True,
                                fallback_provider_id="historical"))
        db.add(CatalogModel(id=model_id, provider_id=provider, remote_model_id="remote-model",
                            display_name="Readable Speech",
                            source=source, capability_status=status, capabilities=list(capabilities),
                            enabled=model_enabled, retired_at=datetime(2026, 1, 1) if retired else None))
    if with_key:
        async with sessions.begin() as db:
            key = await (await CredentialService.open(db, path)).create(provider, "synthetic-secret-key")
            if with_edge:
                db.add(KeyModelAccess(key_id=key.id, model_id=model_id, provider_id=provider))


async def test_put_persists_exact_catalog_id_and_provider_clears_error_preserves_fallback(default_api):
    client, sessions, path = default_api
    await seed(sessions, path)
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["model_id"] == "catalog-id" and data["primary_provider_id"] == "openai"
    assert data["model_display_name"] == "Readable Speech"
    assert data["default_status"] == "ready" and data["selectable"] is True
    assert data["configuration_error"] is None
    assert "synthetic-secret-key" not in response.text
    listed = (await client.get("/api/ai/functions")).json()["data"]
    stored_view = next(row for row in listed if row['function_id'] == 'stt')
    assert stored_view['model_id'] == 'catalog-id'
    assert stored_view['model_display_name'] == 'Readable Speech'
    async with sessions() as db:
        config = await db.get(AIFunctionConfig, "stt")
        assert config.model_id == "catalog-id" and config.primary_provider_id == "openai"
        assert config.configuration_error is None
        assert config.fallback_enabled and config.fallback_provider_id == "historical"


async def test_put_creates_missing_known_function_after_virtual_inventory(default_api):
    client, sessions, path = default_api
    await seed(sessions, path)
    async with sessions.begin() as db:
        await db.execute(delete(AIFunctionConfig).where(AIFunctionConfig.function_id == 'stt'))
    listed = (await client.get('/api/ai/functions')).json()['data']
    assert next(row for row in listed if row['function_id'] == 'stt')['default_status'] == 'unconfigured'
    response = await client.put('/api/ai/functions/stt', json={'model_id': 'catalog-id'})
    assert response.status_code == 200
    assert response.json()['data']['default_status'] == 'ready'
    async with sessions() as db:
        stored = await db.get(AIFunctionConfig, 'stt')
        assert stored.model_id == 'catalog-id' and stored.primary_provider_id == 'openai'


async def test_unavailable_model_does_not_persist_virtual_function(default_api):
    client, sessions, path = default_api
    await seed(sessions, path, with_key=False)
    async with sessions.begin() as db:
        await db.execute(delete(AIFunctionConfig).where(AIFunctionConfig.function_id == 'stt'))
    response = await client.put('/api/ai/functions/stt', json={'model_id': 'catalog-id'})
    assert response.status_code == 409
    async with sessions() as db:
        assert await db.get(AIFunctionConfig, 'stt') is None


async def test_openrouter_video_default_rejects_unsupported_configured_duration(default_api):
    from app.config import get_settings
    client, sessions, path = default_api
    duration = get_settings().VIDEO_TARGET_DURATION
    await seed(sessions, path, provider="openrouter", capability="VIDEO_GENERATION",
               with_edge=False)
    async with sessions.begin() as db:
        model = await db.get(CatalogModel, "catalog-id")
        model.discovery_metadata = {"architecture": {
            "input_modalities": ["text"], "output_modalities": ["video"]},
            "video": {"supported_durations": [duration + 1]}}
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 409


@pytest.mark.parametrize("case", ["incompatible", "retired", "model_disabled", "provider_disabled",
                                   "no_key", "no_edge"])
async def test_put_rejects_unavailable_or_incompatible_model(default_api, case):
    client, sessions, path = default_api
    await seed(sessions, path, source="manual" if case == "incompatible" else "discovered",
               status="KNOWN" if case == "incompatible" else "FULL_UNKNOWN",
               capabilities=("TTS",) if case == "incompatible" else (),
               retired=case == "retired", model_enabled=case != "model_disabled",
               provider_enabled=case != "provider_disabled", with_key=case != "no_key",
               with_edge=case != "no_edge")
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "legacy-remote"


@pytest.mark.parametrize("provider,capability,source", [
    ("fal", "IMAGE_GENERATION", "discovered"),
    ("elevenlabs", "TTS", "discovered"),
    ("edge_tts", "TTS", "system"),
    ("pollinations", "IMAGE_GENERATION", "system"),
    ("local_image", "IMAGE_GENERATION", "system"),
])
async def test_public_catalog_and_keyless_availability_matches_router(default_api, provider, capability, source):
    client, sessions, path = default_api
    await seed(sessions, path, provider=provider, capability=capability, source=source,
               with_key=source != "system", with_edge=False)
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 200
    assert response.json()["data"]["default_status"] == "ready"
    assert "verified" not in response.text


async def test_imported_archival_model_cannot_replace_function_default(default_api):
    client, sessions, path = default_api
    await seed(sessions, path, provider="fal", capability="IMAGE_GENERATION",
               source="legacy_import", with_key=True, with_edge=False)
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "legacy-remote"


async def test_unknown_function_model_and_remote_name_are_rejected(default_api):
    client, sessions, path = default_api
    await seed(sessions, path)
    for function_id, model_id in (("missing", "catalog-id"), ("stt", "missing"),
                                  ("stt", "remote-model")):
        response = await client.put(f"/api/ai/functions/{function_id}", json={"model_id": model_id})
        assert response.status_code == 404


async def test_bad_body_and_fallback_fields_are_rejected_without_secret_echo(default_api):
    client, sessions, path = default_api
    await seed(sessions, path)
    secret = "synthetic-secret-never-echo"
    for body in ({"model_id": "catalog-id", "fallback_enabled": True},
                 {"model_id": {"secret": secret}},
                 {"model_id": "catalog-id", "primary_provider_id": secret}):
        response = await client.put("/api/ai/functions/stt", json=body)
        assert response.status_code == 422
        assert secret not in response.text
    response = await client.put("/api/ai/functions/stt", content='{"model_id":"' + secret,
                                headers={"content-type": "application/json"})
    assert response.status_code == 422 and secret not in response.text


async def test_secret_bearing_internal_exception_is_not_logged_or_returned(default_api, monkeypatch, caplog):
    from app.api.routes import ai_function_defaults

    client, sessions, path = default_api
    await seed(sessions, path)
    secret = "synthetic-secret-exception"

    async def explode(*_args):
        raise RuntimeError(secret)

    monkeypatch.setattr(ai_function_defaults, "lock_catalog_provider", explode)
    with caplog.at_level(logging.DEBUG):
        response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 500
    assert secret not in response.text and secret not in caplog.text


async def test_refresh_retirement_at_lock_boundary_rejects_write(default_api, monkeypatch):
    from app.api.routes import ai_function_defaults

    client, sessions, path = default_api
    await seed(sessions, path)
    original = ai_function_defaults.lock_catalog_provider

    async def retire_then_lock(db, provider_id):
        await original(db, provider_id)
        model = await db.get(CatalogModel, "catalog-id")
        model.retired_at = datetime(2026, 1, 1)
        await db.flush()

    monkeypatch.setattr(ai_function_defaults, "lock_catalog_provider", retire_then_lock)
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "legacy-remote"


@pytest.mark.parametrize("change", ["retire", "disable_model", "disable_provider", "disable_key"])
async def test_concurrent_change_before_provider_lock_rejects_default(default_api, monkeypatch, change):
    from app.api.routes import ai_function_defaults

    client, sessions, path = default_api
    await seed(sessions, path)
    original = ai_function_defaults.lock_catalog_provider

    async def change_then_lock(db, provider_id):
        # This writer commits after pre-lookup but before the selection lock.
        async with sessions.begin() as writer:
            if change == "retire":
                (await writer.get(CatalogModel, "catalog-id")).retired_at = datetime(2026, 1, 1)
            elif change == "disable_model":
                (await writer.get(CatalogModel, "catalog-id")).enabled = False
            elif change == "disable_provider":
                (await writer.get(Provider, "openai")).enabled = False
            else:
                (await writer.scalar(select(APIKey))).enabled = False
        await original(db, provider_id)

    monkeypatch.setattr(ai_function_defaults, "lock_catalog_provider", change_then_lock)
    response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    assert response.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "legacy-remote"


async def test_validation_uses_mysql_current_locking_reads(default_api):
    client, sessions, path = default_api
    await seed(sessions, path)
    statements = []

    def capture(_conn, _cursor, _statement, _params, context, _many):
        compiled = getattr(context, "compiled", None)
        if compiled is not None and getattr(compiled.statement, "_for_update_arg", None) is not None:
            statements.append(str(compiled.statement.compile(dialect=mysql.dialect())))

    engine = sessions.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await client.put("/api/ai/functions/stt", json={"model_id": "catalog-id"})
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert any("FROM ai_catalog_models" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("FROM providers" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("JOIN ai_key_model_access" in sql and "FOR UPDATE" in sql for sql in statements)
