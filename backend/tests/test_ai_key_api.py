"""Canonical key API with disposable SQLite and injected discovery only."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult


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
    from app.services.credential_service import CredentialService
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
