"""Explicit legacy data cutover on disposable SQLite only."""

import json

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIModel, AIFunctionConfig
from tests.test_voice_version_width import mysql_db


@pytest.fixture
async def cutover_db(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'cutover.sqlite'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    yield sessions
    await engine.dispose()


def legacy_keys(path, *, provider="openai"):
    path.write_text(json.dumps({provider: [{
        "key_id": "legacy-one", "provider_id": provider,
        "api_key": "synthetic-cutover-secret-123",
    }]}), encoding="utf-8")
    return path


async def test_preview_reads_only_and_apply_replays_without_touching_archive(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    path = legacy_keys(tmp_path / "api_keys.json")
    master = Fernet.generate_key()
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIModel(id="archived-model", provider_id="openai", model_name="Archived",
                       capabilities='["STT"]'))
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="archived-model"))

    statements = []
    event.listen(sessions.kw["bind"].sync_engine, "before_cursor_execute",
                 lambda conn, cursor, sql, params, context, many: statements.append(sql))
    source = path.read_bytes()
    async with sessions() as db:
        preview = await run_legacy_data_cutover(db, json_path=path, dry_run=True)
        assert preview["status"] == "preview"
        assert preview["inventory"]["counts"]["legacy_models"] == 1
        assert preview["defaults"]["counts"]["unresolved"] == 1
        assert not any(sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
                       for sql in statements)
        assert not db.new and not db.dirty
        await db.rollback()

    async with sessions.begin() as db:
        applied = await run_legacy_data_cutover(db, json_path=path,
                                                master_key=master, dry_run=False)
        assert applied["status"] == "applied"
        assert applied["catalog"]["counts"]["imported"] == 1
        assert applied["keys"]["counts"]["imported"] == 1
        assert applied["defaults"]["counts"]["unresolved"] == 1
        assert (await db.scalar(select(APIKey))).enabled is False
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "archived-model"
    async with sessions.begin() as db:
        replay = await run_legacy_data_cutover(db, json_path=path,
                                               master_key=master, dry_run=False)
        assert replay["status"] == "applied"
        assert replay["catalog"]["counts"] == {"imported": 0, "existing": 1}
        assert replay["keys"]["counts"]["duplicate_existing"] == 1
        assert (await db.get(AIModel, "archived-model")).model_name == "Archived"
    assert path.read_bytes() == source


async def test_invalid_json_blocks_before_writes_or_env_fallback(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    bad_json = tmp_path / "api_keys.json"
    bad_json.write_text('{"openai": ["synthetic-secret"', encoding="utf-8")
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=synthetic-env-secret\n", encoding="utf-8")
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIModel(id="archived-model", provider_id="openai", model_name="Archived",
                       capabilities='["STT"]'))
    async with sessions.begin() as db:
        result = await run_legacy_data_cutover(db, json_path=bad_json, env_path=env,
                                               master_key=Fernet.generate_key(), dry_run=False)
        assert result["status"] == "blocked"
        assert result["reason"] == "invalid_source"
        assert (await db.scalars(select(CatalogModel))).all() == []
        assert (await db.scalars(select(APIKey))).all() == []


async def test_catalog_only_cutover_needs_no_credential_master(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIModel(id="archive", provider_id="openai", model_name="Archived",
                       capabilities='["STT"]'))
    async with sessions.begin() as db:
        result = await run_legacy_data_cutover(db, json_path=tmp_path / "missing.json",
                                               dry_run=False)
        assert result["status"] == "applied"
        assert result["catalog"]["counts"]["imported"] == 1
        assert (await db.scalars(select(APIKey))).all() == []


async def test_later_catalog_conflict_rolls_back_imported_keys(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    path = legacy_keys(tmp_path / "api_keys.json")
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        db.add(AIModel(id="orphan-model", provider_id="missing", model_name="Orphan",
                       capabilities='["STT"]'))
    async with sessions.begin() as db:
        result = await run_legacy_data_cutover(db, json_path=path,
                                               master_key=Fernet.generate_key(), dry_run=False)
        assert result["status"] == "blocked"
        assert result["reason"] == "catalog_conflict"
        assert (await db.scalars(select(APIKey))).all() == []
        assert (await db.scalars(select(CatalogModel))).all() == []


async def test_missing_key_provider_rolls_back_all_imported_keys(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    path = tmp_path / "api_keys.json"
    path.write_text(json.dumps({provider: [{
        "key_id": provider, "provider_id": provider,
        "api_key": f"synthetic-{provider}-secret",
    }] for provider in ("openai", "missing")}), encoding="utf-8")
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
    async with sessions.begin() as db:
        result = await run_legacy_data_cutover(db, json_path=path,
                                               master_key=Fernet.generate_key(), dry_run=False)
        assert result["status"] == "blocked"
        assert result["reason"] == "key_provider_conflict"
        assert (await db.scalars(select(APIKey))).all() == []


async def test_mysql_savepoint_rolls_back_key_import_after_catalog_conflict(mysql_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
        model.__table__.create(mysql_db)
    mysql_db.commit()
    engine = create_async_engine(mysql_db.engine.url.set(drivername="mysql+aiomysql"))
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    path = legacy_keys(tmp_path / "api_keys.json")
    try:
        async with sessions.begin() as db:
            db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
            db.add(AIModel(id="orphan-model", provider_id="missing", model_name="Orphan",
                           capabilities='["STT"]'))
        async with sessions.begin() as db:
            result = await run_legacy_data_cutover(db, json_path=path,
                                                   master_key=Fernet.generate_key(), dry_run=False)
            assert result == {"status": "blocked", "reason": "catalog_conflict"}
            assert (await db.scalars(select(APIKey))).all() == []
            assert (await db.get(Provider, "openai")).catalog_revision == 0
        async with sessions() as db:
            assert (await db.scalars(select(APIKey))).all() == []
    finally:
        await engine.dispose()


async def test_mysql_successful_apply_still_obeys_caller_rollback(mysql_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
        model.__table__.create(mysql_db)
    mysql_db.commit()
    engine = create_async_engine(mysql_db.engine.url.set(drivername="mysql+aiomysql"))
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    path = legacy_keys(tmp_path / "api_keys.json")
    try:
        async with sessions.begin() as db:
            db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        async with sessions() as db:
            result = await run_legacy_data_cutover(db, json_path=path,
                                                   master_key=Fernet.generate_key(), dry_run=False)
            assert result["status"] == "applied"
            assert (await db.scalars(select(APIKey))).one().enabled is False
            await db.rollback()
        async with sessions() as db:
            assert (await db.scalars(select(APIKey))).all() == []
    finally:
        await engine.dispose()


async def test_successful_sqlite_apply_still_obeys_caller_rollback(cutover_db, tmp_path):
    from app.services.legacy_data_cutover import run_legacy_data_cutover

    sessions = cutover_db
    path = legacy_keys(tmp_path / "api_keys.json")
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
    async with sessions() as db:
        result = await run_legacy_data_cutover(db, json_path=path,
                                               master_key=Fernet.generate_key(), dry_run=False)
        assert result["status"] == "applied"
        assert (await db.scalars(select(APIKey))).one().enabled is False
        await db.rollback()
    async with sessions() as db:
        assert (await db.scalars(select(APIKey))).all() == []


async def test_source_swap_during_inventory_cannot_select_env_fallback(cutover_db, tmp_path, monkeypatch):
    from app.services import legacy_data_cutover as cutover

    sessions = cutover_db
    path = legacy_keys(tmp_path / "api_keys.json")
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=synthetic-different-secret\n", encoding="utf-8")
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
    real_inventory = cutover.inventory_legacy_migration

    async def racing_inventory(db, **kwargs):
        result = await real_inventory(db, **kwargs)
        path.unlink()
        return result

    monkeypatch.setattr(cutover, "inventory_legacy_migration", racing_inventory)
    async with sessions.begin() as db:
        result = await cutover.run_legacy_data_cutover(
            db, json_path=path, env_path=env, master_key=Fernet.generate_key(), dry_run=False,
        )
        assert result == {"status": "blocked", "reason": "source_changed"}
        assert (await db.scalars(select(APIKey))).all() == []
