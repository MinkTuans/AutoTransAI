"""Refresh safety with disposable SQLite, synthetic keys, and injected discovery."""
import json

import pytest
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models as models
from app.models.settings import AIFunctionConfig
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult
from app.services.credential_service import CredentialService


def listing(*ids, status="complete", scope="credential", error=None):
    return DiscoveryResult(status, tuple(DiscoveredModel(i) for i in ids), error, 1, scope)


@pytest.fixture
async def env(tmp_path):
    from app.services.model_refresh_service import ModelRefreshService
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (models.Provider, models.APIKey, models.CatalogModel, models.KeyModelAccess,
                      AIFunctionConfig, models.CatalogRefreshRun):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all([models.Provider(id=p, name=p, provider_type="llm")
                    for p in ("openai", "fal", "edge_tts", "kling")])
    responses = {}

    async def discover(provider, secret):
        result = responses[secret]
        if callable(result):
            return await result()
        return result

    async def key(secret, provider="openai"):
        async with sessions.begin() as db:
            return await (await CredentialService.open(db, tmp_path)).create(provider, secret)

    service = ModelRefreshService(sessions, tmp_path, discovery=discover)
    yield service, sessions, key, responses, tmp_path
    await engine.dispose()


async def inventory(sessions):
    async with sessions() as db:
        return {m.remote_model_id: m for m in (await db.scalars(select(models.CatalogModel))).all()}


async def test_additive_union_delete_retention_then_explicit_retirement(env):
    service, sessions, key, responses, path = env
    a, b = await key("synthetic-key-A"), await key("synthetic-key-B")
    responses.update({"synthetic-key-A": listing("A", "B"), "synthetic-key-B": listing("B", "C")})
    await service.discover_key(a.id)
    await service.discover_key(b.id)
    assert set(await inventory(sessions)) == {"A", "B", "C"}
    assert (await service.refresh()).status == "complete"
    async with sessions.begin() as db:
        await (await CredentialService.open(db, path)).delete(b.id)
    assert all(m.retired_at is None for m in (await inventory(sessions)).values())
    run = await service.refresh()
    rows = await inventory(sessions)
    assert rows["C"].retired_at is not None
    assert rows["A"].retired_at is rows["B"].retired_at is None
    assert run.summary["providers"]["openai"]["retired"] == 1
    async with sessions() as db:
        persisted = await db.get(models.CatalogRefreshRun, run.id)
        assert persisted.status == "complete" and persisted.completed_at is not None
        assert "synthetic-key" not in json.dumps(persisted.summary)


@pytest.mark.parametrize("result", [listing("A", status="partial", error="timeout"),
    listing(status="failed", error="rate_limited"), listing(status="failed", error="malformed"),
    listing(status="unsupported", error="unsupported"), listing(),
    listing("A", error="incomplete"), listing("A", scope="unknown")])
async def test_incomplete_provider_never_removes_models_or_edges(env, result):
    service, sessions, key, responses, _ = env
    a = await key("synthetic-key-A")
    responses["synthetic-key-A"] = listing("A", "B")
    await service.discover_key(a.id)
    responses["synthetic-key-A"] = result
    run = await service.refresh()
    assert run.status == "partial"
    assert all(m.retired_at is None for m in (await inventory(sessions)).values())
    async with sessions() as db:
        assert len((await db.scalars(select(models.KeyModelAccess))).all()) == 2


async def test_one_failed_key_blocks_provider_cleanup_but_not_other_provider(env):
    service, sessions, key, responses, _ = env
    a, b, f = await key("key-a"), await key("key-b"), await key("key-f", "fal")
    responses.update({"key-a": listing("A", "B"), "key-b": listing("C"),
                      "key-f": listing("F", "G", scope="catalog")})
    for k in (a, b, f):
        await service.discover_key(k.id)
    responses.update({"key-a": listing("A"), "key-b": listing(status="failed"),
                      "key-f": listing("F", scope="catalog")})
    await service.refresh()
    rows = await inventory(sessions)
    assert rows["B"].retired_at is rows["C"].retired_at is None
    assert rows["G"].retired_at is not None
    async with sessions() as db:
        assert not (await db.scalars(select(models.KeyModelAccess).where(models.KeyModelAccess.provider_id == "fal"))).all()


async def test_empty_key_pool_retires_supported_models_but_preserves_edge_and_unsupported(env):
    service, sessions, _, _, _ = env
    async with sessions.begin() as db:
        db.add_all([models.CatalogModel(provider_id="edge_tts", remote_model_id="edge", source="system"),
                    models.CatalogModel(provider_id="openai", remote_model_id="old"),
                    models.CatalogModel(provider_id="kling", remote_model_id="unsupported")])
    await service.refresh()
    rows = await inventory(sessions)
    assert rows["old"].retired_at is not None
    assert rows["edge"].retired_at is rows["unsupported"].retired_at is None


async def test_add_discovery_preserves_previous_edges_and_disabled_choice(env):
    service, sessions, key, responses, _ = env
    a = await key("synthetic-key-A")
    responses["synthetic-key-A"] = listing("A", "B")
    await service.discover_key(a.id)
    async with sessions.begin() as db:
        (await db.scalar(select(models.CatalogModel).where(models.CatalogModel.remote_model_id == "A"))).enabled = False
    responses["synthetic-key-A"] = listing("A")
    await service.discover_key(a.id)
    assert (await inventory(sessions))["B"].retired_at is None
    assert not (await inventory(sessions))["A"].enabled
    async with sessions() as db:
        assert len((await db.scalars(select(models.KeyModelAccess))).all()) == 2


@pytest.mark.parametrize("change", ["create", "delete", "rotate", "disable"])
async def test_concurrent_key_change_invalidates_snapshot_without_network_transaction(env, change):
    service, sessions, key, responses, path = env
    a = await key("synthetic-key-A")
    responses["synthetic-key-A"] = listing("A", "B")
    await service.discover_key(a.id)

    async def changed():
        # A separate writer must commit while discovery is in flight (no write lock held).
        async with sessions.begin() as db:
            credentials = await CredentialService.open(db, path)
            if change == "create":
                await credentials.create("openai", "synthetic-new-key")
            elif change == "delete":
                await credentials.delete(a.id)
            elif change == "rotate":
                await credentials.rotate(a.id, "synthetic-new-key")
            else:
                await credentials.set_enabled(a.id, False)
        return listing("A")

    responses["synthetic-key-A"] = changed
    run = await service.refresh()
    assert run.status == "stale"
    assert all(m.retired_at is None for m in (await inventory(sessions)).values())


async def test_retired_default_has_visible_error_and_reappearance_clears_it(env):
    service, sessions, key, responses, _ = env
    a = await key("synthetic-key-A")
    responses["synthetic-key-A"] = listing("A", "B")
    await service.discover_key(a.id)
    async with sessions.begin() as db:
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                               primary_provider_id="openai", model_id="B"))
    responses["synthetic-key-A"] = listing("A")
    await service.refresh()
    async with sessions() as db:
        config = await db.get(AIFunctionConfig, "translation")
        assert config.model_id == "B" and config.configuration_error == "catalog_model_retired"
    responses["synthetic-key-A"] = listing("A", "B")
    await service.refresh()
    async with sessions() as db:
        assert (await db.get(AIFunctionConfig, "translation")).configuration_error is None


async def test_discovery_exception_is_sanitized_and_disables_cleanup(env):
    service, sessions, key, responses, _ = env
    a = await key("synthetic-key-A")
    responses["synthetic-key-A"] = listing("A", "B")
    await service.discover_key(a.id)

    async def explode():
        raise RuntimeError("synthetic-secret-must-not-leak")

    responses["synthetic-key-A"] = explode
    run = await service.refresh()
    assert run.status == "partial" and "synthetic-secret" not in json.dumps(run.summary)
    assert all(m.retired_at is None for m in (await inventory(sessions)).values())


async def test_refresh_replaces_each_complete_keys_edges_with_union_retirement(env):
    service, sessions, key, responses, _ = env
    a, b = await key("key-a"), await key("key-b")
    responses.update({"key-a": listing("A", "B"), "key-b": listing("B", "C")})
    await service.refresh()
    responses.update({"key-a": listing("A"), "key-b": listing("B")})
    await service.refresh()
    rows = await inventory(sessions)
    async with sessions() as db:
        pairs = {(edge.key_id, edge.model_id) for edge in (await db.scalars(select(models.KeyModelAccess))).all()}
        assert pairs == {(a.id, rows["A"].id), (b.id, rows["B"].id)}
    assert rows["C"].retired_at is not None


async def test_newer_refresh_invalidates_older_inflight_refresh(env):
    service, sessions, key, responses, path = env
    await key("key-a")

    async def newer():
        responses["key-a"] = listing("A", "B")
        assert (await service.refresh()).status == "complete"
        return listing("A")

    responses["key-a"] = newer
    assert (await service.refresh()).status == "stale"
    assert (await inventory(sessions))["B"].retired_at is None


async def test_run_summary_preserves_safe_error_classification(env):
    service, _, key, responses, _ = env
    await key("key-a")
    responses["key-a"] = listing(status="failed", error="rate_limited")
    run = await service.refresh()
    assert run.summary["providers"]["openai"]["results"][0]["error_code"] == "rate_limited"
    responses["key-a"] = listing(status="failed", error="private-secret")
    assert "private-secret" not in json.dumps((await service.refresh()).summary)


async def test_rotated_credential_keeps_id_changes_secret_and_revokes_old_listing(env):
    service, sessions, key, responses, path = env
    a = await key("key-a")
    responses["key-a"] = listing("A")
    await service.discover_key(a.id)
    async with sessions.begin() as db:
        credentials = await CredentialService.open(db, path)
        replacement = await credentials.rotate(a.id, "key-replacement")
        assert replacement.id == a.id and replacement.revision == a.revision + 1
        assert await credentials.reveal(a.id) == "key-replacement"
        assert (await db.scalars(select(models.KeyModelAccess))).all() == []
    assert (await inventory(sessions))["A"].retired_at is None


@pytest.mark.parametrize("bad", [None, {"status": "complete"}, listing(""), listing("A", scope="bad")])
async def test_malformed_discovery_result_cannot_authorize_cleanup(env, bad):
    service, sessions, key, responses, _ = env
    a = await key("key-a")
    responses["key-a"] = listing("A", "B")
    await service.discover_key(a.id)
    responses["key-a"] = bad
    assert (await service.refresh()).status == "partial"
    assert all(m.retired_at is None for m in (await inventory(sessions)).values())


async def test_provider_activation_during_scan_invalidates_empty_pool_snapshot(env):
    service, sessions, key, responses, _ = env
    await key("key-a")
    await key("key-f", "fal")
    async with sessions.begin() as db:
        (await db.get(models.Provider, "openai")).enabled = False
        db.add(models.CatalogModel(provider_id="openai", remote_model_id="A"))

    async def activate():
        async with sessions.begin() as db:
            (await db.get(models.Provider, "openai")).enabled = True
        return listing("F", scope="catalog")

    responses["key-f"] = activate
    assert (await service.refresh()).status == "stale"
    assert (await inventory(sessions))["A"].retired_at is None


async def test_write_failure_rolls_back_entire_catalog_reconciliation(env):
    service, sessions, key, responses, _ = env
    await key("key-a")
    responses["key-a"] = listing("A", "B")
    await service.refresh()
    responses["key-a"] = listing("A", "C")

    def fail_retirement(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("UPDATE ai_catalog_models"):
            raise RuntimeError("synthetic-database-error-with-private-data")

    engine = sessions.kw["bind"].sync_engine
    event.listen(engine, "before_cursor_execute", fail_retirement)
    try:
        run = await service.refresh()
    finally:
        event.remove(engine, "before_cursor_execute", fail_retirement)
    assert run.status == "failed" and "private-data" not in json.dumps(run.summary)
    rows = await inventory(sessions)
    assert set(rows) == {"A", "B"} and rows["B"].retired_at is None
