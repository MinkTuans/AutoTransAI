"""Legacy Settings compatibility checks on disposable SQLite only."""
import json
import socket
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, func, select
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes import settings as settings_router
from app.main import app
from app.models import APIKey, CatalogModel, Provider
from app.models.settings import AIModel, AIFunctionConfig, SystemSetting
from app.services import settings_service


@pytest.fixture
async def legacy_api(tmp_path, monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("Unexpected outbound connection")))

    class EmptyKeyPool:
        async def get_keys_for_provider(self, _provider):
            return []

    monkeypatch.setattr(settings_service, "get_key_manager", lambda: EmptyKeyPool())
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'settings.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for table in (Provider, APIKey, CatalogModel, SystemSetting, AIFunctionConfig, AIModel):
            await conn.run_sync(table.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def isolated_db():
        async with sessions() as db:
            yield db

    app.dependency_overrides[settings_router.get_db] = isolated_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions
    finally:
        app.dependency_overrides.pop(settings_router.get_db, None)
        await engine.dispose()


async def test_legacy_gets_are_read_only_and_keep_virtual_system_defaults(legacy_api):
    client, sessions = legacy_api
    writes = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
            writes.append(statement)

    engine = sessions.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        settings = await client.get("/api/settings")
        functions = await client.get("/api/settings/functions")
        models = await client.get("/api/settings/models")
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert settings.status_code == functions.status_code == models.status_code == 200
    assert settings.json()["data"]["storage_provider"] == "local"
    assert functions.json()["data"] == [] and models.json()["data"] == []
    assert writes == []
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(SystemSetting)) == 0
        assert await db.scalar(select(func.count()).select_from(AIFunctionConfig)) == 0
        assert await db.scalar(select(func.count()).select_from(AIModel)) == 0


async def test_get_models_does_not_resurrect_deleted_legacy_model(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(AIModel(id="historical", provider_id="openai", model_name="Historical",
                       capabilities=json.dumps(["STT"])))
    assert (await client.delete("/api/settings/models/historical")).status_code == 200
    assert (await client.get("/api/settings/models")).json()["data"] == []
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(AIModel)) == 0


async def test_get_functions_does_not_switch_fal_image_default_without_legacy_key(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(AIModel(id="fal-image", provider_id="fal", model_name="Fal Image",
                       capabilities=json.dumps(["IMAGE_GENERATION"])))
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image",
                                capability="IMAGE_GENERATION", primary_provider_id="fal", model_id="fal-image"))
    data = (await client.get("/api/settings/functions")).json()["data"]
    assert data[0]["primary_provider_id"] == "fal" and data[0]["model_id"] == "fal-image"
    async with sessions() as db:
        config = await db.get(AIFunctionConfig, "image_generation")
        assert config.primary_provider_id == "fal" and config.model_id == "fal-image"
        assert await db.get(AIModel, "pollinations-default") is None


@pytest.mark.parametrize("retired", [False, True])
async def test_legacy_function_put_rejects_canonical_default_without_change(legacy_api, retired):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="catalog-id", provider_id="openai", remote_model_id="remote",
                            retired_at=datetime(2026, 1, 1) if retired else None))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="catalog-id",
                                fallback_enabled=False, fallback_provider_id=None))
    result = await client.put("/api/settings/functions/stt", json={"model_id": "legacy-model",
                                                                 "fallback_enabled": True})
    assert result.status_code == 409
    assert result.json()["detail"] == "Use /api/ai/functions/{function_id} to change this default."
    async with sessions() as db:
        config = await db.get(AIFunctionConfig, "stt")
        assert config.model_id == "catalog-id" and config.primary_provider_id == "openai"
        assert config.fallback_enabled is False


async def test_legacy_function_put_still_updates_unmigrated_default(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="gemini", model_id="gemini-legacy"))
    result = await client.put("/api/settings/functions/stt", json={"model_id": "openai-legacy",
                                                                 "primary_provider_id": "openai",
                                                                 "fallback_enabled": True})
    assert result.status_code == 200
    async with sessions() as db:
        config = await db.get(AIFunctionConfig, "stt")
        assert config.model_id == "openai-legacy" and config.primary_provider_id == "openai"
        assert config.fallback_enabled is True


async def test_legacy_model_mutators_cannot_change_canonical_row(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="same-id", provider_id="openai", remote_model_id="canonical-remote",
                            display_name="Canonical", source="discovered"))
        db.add(AIModel(id="same-id", provider_id="openai", model_name="Legacy",
                       capabilities=json.dumps(["STT"]), is_custom=True))
    updated = await client.put("/api/settings/models/same-id", json={"model_name": "Changed Legacy"})
    assert updated.status_code == 200
    deleted = await client.delete("/api/settings/models/same-id")
    assert deleted.status_code == 200
    async with sessions() as db:
        canonical = await db.get(CatalogModel, "same-id")
        assert canonical.remote_model_id == "canonical-remote" and canonical.display_name == "Canonical"
        assert await db.get(AIModel, "same-id") is None


async def test_legacy_model_delete_does_not_reassign_canonical_default_on_id_collision(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="same-id", provider_id="openai", remote_model_id="canonical-remote"))
        db.add(AIModel(id="same-id", provider_id="openai", model_name="Legacy",
                       capabilities=json.dumps(["STT"]), is_custom=True))
        db.add(AIModel(id="alternate", provider_id="openai", model_name="Alternative",
                       capabilities=json.dumps(["STT"]), is_custom=True))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="same-id"))
    result = await client.delete("/api/settings/models/same-id")
    assert result.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "same-id"
        assert await db.get(CatalogModel, "same-id") is not None


async def test_legacy_writers_lock_function_row_before_canonical_identity_check(legacy_api):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="same-id", provider_id="openai", remote_model_id="canonical-remote"))
        db.add(AIModel(id="same-id", provider_id="openai", model_name="Legacy",
                       capabilities=json.dumps(["STT"]), is_custom=True))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="same-id"))
    statements = []

    def capture(_conn, _cursor, _statement, _params, context, _many):
        compiled = getattr(context, "compiled", None)
        if compiled is not None and getattr(compiled.statement, "_for_update_arg", None) is not None:
            statements.append(str(compiled.statement.compile(dialect=mysql.dialect())))

    engine = sessions.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        assert (await client.put("/api/settings/functions/stt", json={"model_id": "legacy"})).status_code == 409
        assert any("FROM ai_function_configs" in sql and "FOR UPDATE" in sql for sql in statements)
        statements.clear()
        assert (await client.delete("/api/settings/models/same-id")).status_code == 409
        assert any("FROM ai_function_configs" in sql and "FOR UPDATE" in sql for sql in statements)
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)


async def test_legacy_put_sees_canonical_choice_committed_before_row_lock(legacy_api, monkeypatch):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="canonical", provider_id="openai", remote_model_id="remote"))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="gemini", model_id="legacy"))
    original = settings_service.SettingsService.update_function_config

    async def concurrent_canonical_choice(db, function_id, payload):
        async with sessions.begin() as writer:
            config = await writer.get(AIFunctionConfig, function_id)
            config.primary_provider_id = "openai"
            config.model_id = "canonical"
        return await original(db, function_id, payload)

    monkeypatch.setattr(settings_service.SettingsService, "update_function_config", concurrent_canonical_choice)
    result = await client.put("/api/settings/functions/stt", json={"model_id": "legacy-replacement"})
    assert result.status_code == 409
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "canonical"


@pytest.mark.parametrize("enabled", [False, True])
async def test_legacy_function_get_uses_canonical_key_flags_without_legacy_store(legacy_api, monkeypatch, enabled):
    client, sessions = legacy_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="legacy"))
        await db.flush()
        db.add(APIKey(id="synthetic-key-id", provider_id="openai", ciphertext="synthetic-ciphertext",
                      fingerprint="synthetic-fingerprint", masked_key="****", enabled=enabled))

    def forbidden_legacy_key_store():
        raise AssertionError("Legacy key store must not be initialized on GET")

    monkeypatch.setattr(settings_service, "get_key_manager", forbidden_legacy_key_store)
    response = await client.get("/api/settings/functions")
    assert response.status_code == 200
    eligible = response.json()["data"][0]["eligible_providers"]
    assert next(p for p in eligible if p["id"] == "openai")["configured"] is enabled
