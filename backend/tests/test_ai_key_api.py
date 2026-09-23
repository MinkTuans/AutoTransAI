"""Canonical key API with disposable SQLite and injected discovery only."""
import logging
import socket

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult
from app.services.credential_service import CredentialService


@pytest.fixture(autouse=True)
def no_outbound_connections(monkeypatch):
    def blocked(*_args, **_kwargs):
        raise AssertionError("Unexpected outbound connection")
    monkeypatch.setattr(socket.socket, "connect", blocked)


def listing(*names, status="complete", scope="credential", error=None):
    return DiscoveryResult(status, tuple(DiscoveredModel(name) for name in names), error, 1, scope)


@pytest.fixture
async def key_api(tmp_path):
    from app.api.routes import ai_keys

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'keys.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for table in (Provider, APIKey, CatalogModel, KeyModelAccess, AIFunctionConfig, CatalogRefreshRun):
            await conn.run_sync(table.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all([Provider(id=p, name=p, provider_type="llm") for p in ("openai", "fal")])
    responses = {}

    async def discover(provider, secret):
        result = responses[secret]
        return await result() if callable(result) else result

    from app.services.model_refresh_service import ModelRefreshService

    def context():
        return ai_keys.KeyAPIContext(sessions, tmp_path, ModelRefreshService(sessions, tmp_path, discovery=discover))

    app.dependency_overrides[ai_keys.get_key_api_context] = context
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions, responses
    finally:
        app.dependency_overrides.pop(ai_keys.get_key_api_context, None)
        await engine.dispose()


async def test_add_lists_masked_key_and_adds_models_after_commit(key_api):
    client, sessions, responses = key_api
    responses["synthetic-key-one"] = listing("model-one")
    result = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key-one"})
    assert result.status_code == 201
    data = result.json()["data"]
    assert data["key"]["masked_key"] == "****-one"
    assert data["key"]["enabled"] is True
    assert data["discovery"]["status"] == "complete"
    assert "synthetic-key-one" not in result.text
    rows = (await client.get("/api/ai/providers/openai/keys")).json()["data"]
    assert rows == [data["key"]]
    async with sessions() as db:
        assert (await db.scalar(select(CatalogModel).where(CatalogModel.remote_model_id == "model-one"))) is not None


async def test_rejected_discovery_stays_disabled_and_response_is_safe(key_api):
    client, sessions, responses = key_api
    responses["synthetic-secret-invalid"] = listing(status="failed", error="auth_invalid")
    result = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-secret-invalid"})
    assert result.status_code == 201
    assert result.json()["data"]["key"]["enabled"] is False
    assert result.json()["data"]["discovery"]["error_code"] == "auth_invalid"
    assert "synthetic-secret-invalid" not in result.text
    async with sessions() as db:
        assert (await db.scalar(select(APIKey))).enabled is False


async def test_bad_input_does_not_echo_secret(key_api):
    client, _, _ = key_api
    secret = "synthetic-secret-never-echo"
    for kwargs in ({"json": {"key": {"nested": secret}}},
                   {"content": '{"key": "' + secret + '",', "headers": {"content-type": "application/json"}}):
        result = await client.post("/api/ai/providers/openai/keys", **kwargs)
        assert result.status_code == 422
        assert secret not in result.text


@pytest.mark.parametrize("mutation", ["rotate", "disable"])
async def test_add_does_not_enable_key_changed_after_discovery(key_api, monkeypatch, mutation, tmp_path):
    from app.services.model_refresh_service import ModelRefreshService

    client, sessions, responses = key_api
    responses["synthetic-key-before"] = listing("model-one")
    original = ModelRefreshService.discover_key

    async def discover_then_change(self, key_id):
        outcome = await original(self, key_id)
        async with sessions.begin() as db:
            credentials = await CredentialService.open(db, tmp_path)
            if mutation == "rotate":
                await credentials.rotate(key_id, "synthetic-key-after")
            else:
                await credentials.set_enabled(key_id, False)
        return outcome

    monkeypatch.setattr(ModelRefreshService, "discover_key", discover_then_change)
    response = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key-before"})
    assert response.status_code == 409
    assert "synthetic-key-before" not in response.text
    async with sessions() as db:
        key = await db.scalar(select(APIKey))
        assert key.enabled is False
        assert key.revision == 2


async def test_duplicate_and_two_distinct_keys_same_provider(key_api):
    client, sessions, responses = key_api
    responses.update({"synthetic-key-A": listing("A", "B"), "synthetic-key-B": listing("B", "C")})
    first = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key-A"})
    second = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key-B"})
    duplicate = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key-A"})
    assert first.status_code == second.status_code == 201
    assert duplicate.status_code == 409
    assert "synthetic-key-A" not in duplicate.text
    assert len((await client.get("/api/ai/providers/openai/keys")).json()["data"]) == 2
    async with sessions() as db:
        assert {m.remote_model_id for m in (await db.scalars(select(CatalogModel))).all()} == {"A", "B", "C"}


@pytest.mark.parametrize("status,error,scope", [
    ("partial", "timeout", "credential"), ("unsupported", "unsupported", "unknown"),
    ("complete", None, "credential"), ("failed", "rate_limited", "unknown"),
    ("complete", None, "catalog"),
])
async def test_incomplete_or_public_listing_keeps_new_key_disabled(key_api, status, error, scope):
    client, sessions, responses = key_api
    models = () if status == "complete" and scope == "credential" else ("public-model",)
    responses["synthetic-key"] = listing(*models, status=status, error=error, scope=scope)
    result = await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key"})
    assert result.status_code == 201
    assert result.json()["data"]["key"]["enabled"] is False
    assert result.json()["data"]["discovery"]["verified_for_generation"] is False
    async with sessions() as db:
        assert (await db.scalar(select(APIKey))).enabled is False


async def test_disable_then_retry_enable_requires_new_complete_discovery(key_api):
    client, sessions, responses = key_api
    responses["synthetic-key"] = listing("A")
    added = (await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key"})).json()["data"]
    key_id = added["key"]["id"]
    disabled = await client.patch(f"/api/ai/keys/{key_id}", json={"enabled": False})
    assert disabled.status_code == 200 and disabled.json()["data"]["key"]["enabled"] is False
    responses["synthetic-key"] = listing(status="failed", error="rate_limited")
    retry = await client.patch(f"/api/ai/keys/{key_id}", json={"enabled": True})
    assert retry.status_code == 200 and retry.json()["data"]["key"]["enabled"] is False
    assert retry.json()["data"]["discovery"]["error_code"] == "rate_limited"
    responses["synthetic-key"] = listing("A", "B")
    enabled = await client.patch(f"/api/ai/keys/{key_id}", json={"enabled": True})
    assert enabled.status_code == 200 and enabled.json()["data"]["key"]["enabled"] is True
    async with sessions() as db:
        assert {m.remote_model_id for m in (await db.scalars(select(CatalogModel))).all()} == {"A", "B"}


async def test_delete_retains_models_until_explicit_refresh(key_api):
    client, sessions, responses = key_api
    responses["synthetic-key"] = listing("A")
    key_id = (await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-key"})).json()["data"]["key"]["id"]
    deleted = await client.delete(f"/api/ai/keys/{key_id}")
    assert deleted.status_code == 200
    async with sessions() as db:
        assert (await db.scalar(select(CatalogModel))).retired_at is None
    refreshed = await client.post("/api/ai/models/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["data"]["status"] == "complete"
    async with sessions() as db:
        assert (await db.scalar(select(CatalogModel))).retired_at is not None


async def test_refresh_union_and_partial_failure_retains_models(key_api):
    client, sessions, responses = key_api
    responses.update({"key-A": listing("A", "B"), "key-B": listing("B", "C")})
    for key in ("key-A", "key-B"):
        assert (await client.post("/api/ai/providers/openai/keys", json={"key": key})).status_code == 201
    responses.update({"key-A": listing("A"), "key-B": listing(status="failed", error="rate_limited")})
    partial = (await client.post("/api/ai/models/refresh")).json()["data"]
    assert partial["status"] == "partial"
    assert {row["error_code"] for row in partial["providers"]["openai"]["results"]} == {None, "rate_limited"}
    async with sessions() as db:
        assert (await db.scalar(select(CatalogModel).where(CatalogModel.remote_model_id == "C"))).retired_at is None
    responses["key-B"] = listing("B")
    complete = (await client.post("/api/ai/models/refresh")).json()["data"]
    assert complete["status"] == "complete"
    assert complete["providers"]["openai"]["retired"] == 1
    async with sessions() as db:
        assert (await db.scalar(select(CatalogModel).where(CatalogModel.remote_model_id == "C"))).retired_at is not None


async def test_secret_in_injected_exception_absent_from_response_and_logs(key_api, monkeypatch, caplog):
    from app.services.model_refresh_service import ModelRefreshService
    client, _, _ = key_api
    secret = "synthetic-secret-exception"

    async def explode(_self, _key_id):
        raise RuntimeError(secret)

    monkeypatch.setattr(ModelRefreshService, "discover_key", explode)
    with caplog.at_level(logging.DEBUG):
        response = await client.post("/api/ai/providers/openai/keys", json={"key": secret})
    assert response.status_code == 500
    assert secret not in response.text
    assert secret not in caplog.text


@pytest.mark.parametrize("status", ["failed", "stale"])
async def test_refresh_reports_failed_and_stale_without_secret_text(key_api, monkeypatch, status):
    from app.services.model_refresh_service import ModelRefreshService, RefreshOutcome

    client, _, _ = key_api

    async def outcome(_self):
        return RefreshOutcome("synthetic-run", status,
                              {"error_code": "refresh_failed", "private": "synthetic-secret"})

    monkeypatch.setattr(ModelRefreshService, "refresh", outcome)
    result = await client.post("/api/ai/models/refresh")
    assert result.status_code == 200
    assert result.json()["data"]["status"] == status
    assert result.json()["data"]["providers"] == {}
    assert "synthetic-secret" not in result.text


async def test_enable_does_not_activate_rotated_key_after_discovery(key_api, monkeypatch, tmp_path):
    from app.services.model_refresh_service import ModelRefreshService

    client, sessions, responses = key_api
    responses["synthetic-original"] = listing(status="failed", error="rate_limited")
    key_id = (await client.post("/api/ai/providers/openai/keys", json={"key": "synthetic-original"})).json()["data"]["key"]["id"]
    responses["synthetic-original"] = listing("A")
    original = ModelRefreshService.discover_key

    async def discover_then_rotate(self, discovered_key_id):
        result = await original(self, discovered_key_id)
        async with sessions.begin() as db:
            await (await CredentialService.open(db, tmp_path)).rotate(discovered_key_id, "synthetic-replacement")
        return result

    monkeypatch.setattr(ModelRefreshService, "discover_key", discover_then_rotate)
    result = await client.patch(f"/api/ai/keys/{key_id}", json={"enabled": True})
    assert result.status_code == 409
    async with sessions() as db:
        assert (await db.get(APIKey, key_id)).enabled is False
