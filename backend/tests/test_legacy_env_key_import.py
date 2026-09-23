"""Disposable SQLite and synthetic source fixtures for explicit env fallback."""
import json
import os

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, Provider
from app.services.credential_service import CredentialService
from app.services.legacy_env_key_import import import_legacy_env_fallback_keys
from app.services import legacy_migration_inventory as inventory_module


@pytest.fixture
async def sessions(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'keys.sqlite'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Provider.__table__.create)
        await conn.run_sync(APIKey.__table__.create)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory.begin() as db:
        db.add_all([
            Provider(id="openai", name="OpenAI", provider_type="llm", requires_api_key=True),
            Provider(id="gemini", name="Gemini", provider_type="llm", requires_api_key=True),
            Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False),
        ])
    yield factory
    await engine.dispose()


def paths(tmp_path, text):
    env_path = tmp_path / "legacy.env"
    env_path.write_text(text, encoding="utf-8")
    return tmp_path / "api_keys.json", env_path


async def run_import(db, json_path, env_path, master):
    return await import_legacy_env_fallback_keys(
        db, json_path=json_path, env_path=env_path, master_key=master,
    )


async def test_env_imports_primary_multiline_indexed_and_multiple_providers_disabled(sessions, tmp_path, caplog):
    secrets = ["synthetic-alpha", "synthetic-beta", "synthetic-gamma", "synthetic-delta"]
    json_path, env_path = paths(tmp_path,
        'OPENAI_API_KEY=" synthetic-alpha\n synthetic-beta "\n'
        'OPENAI_API_KEY_2=" synthetic-gamma "\nGEMINI_API_KEY=synthetic-delta\n')
    original = env_path.read_bytes()
    master = Fernet.generate_key()
    async with sessions() as db:
        result = await run_import(db, json_path, env_path, master)
        rows = (await db.scalars(select(APIKey).order_by(APIKey.provider_id, APIKey.priority))).all()
        assert result["status"] == "imported"
        assert result["counts"]["imported"] == 4
        assert [(r.provider_id, r.priority) for r in rows] == [
            ("gemini", 1), ("openai", 1), ("openai", 2), ("openai", 3)]
        assert all(not r.enabled and r.runtime_status == "ready" and r.request_count == 0
                   and r.success_count == 0 and r.failure_count == 0 for r in rows)
        service = await CredentialService.open(db, tmp_path, master_key=master)
        assert [await service.reveal(r.id) for r in rows] == [secrets[3], *secrets[:3]]
        assert all(secret not in str(result) + caplog.text + (tmp_path / "keys.sqlite").read_bytes().decode("latin1")
                   for secret in secrets)
        await db.rollback()
    async with sessions() as db:
        assert (await db.scalars(select(APIKey))).all() == []
    assert env_path.read_bytes() == original
    assert not (tmp_path / ".api_key_master_key").exists()


async def test_dedupes_source_and_existing_and_repeat_keeps_revision(sessions, tmp_path):
    json_path, env_path = paths(tmp_path,
        "OPENAI_API_KEY=synthetic-existing\nOPENAI_API_KEY_1=synthetic-new\n"
        "OPENAI_API_KEY_2=synthetic-new\nGEMINI_API_KEY=synthetic-new\n")
    master = Fernet.generate_key()
    async with sessions.begin() as db:
        await (await CredentialService.open(db, tmp_path, master_key=master)).create("openai", "synthetic-existing")
    async with sessions.begin() as db:
        first = await run_import(db, json_path, env_path, master)
        revision = (await db.get(Provider, "openai")).catalog_revision
    async with sessions.begin() as db:
        second = await run_import(db, json_path, env_path, master)
        rows = (await db.scalars(select(APIKey))).all()
        assert (await db.get(Provider, "openai")).catalog_revision == revision
    assert first["counts"]["imported"] == 2
    assert first["counts"]["duplicate_source"] == 1
    assert first["counts"]["duplicate_existing"] == 1
    assert second["counts"]["imported"] == 0
    assert len(rows) == 3


@pytest.mark.parametrize("json_content,expected_status,expected_count", [
    ({}, "imported", 0),
    ({"openai": [{"key_id": "old-id", "provider_id": "openai", "api_key": "synthetic-json"}]}, "imported", 1),
    ("broken", "invalid_source", 0),
])
async def test_json_precedence(sessions, tmp_path, json_content, expected_status, expected_count):
    json_path, env_path = paths(tmp_path, "OPENAI_API_KEY=synthetic-env\n")
    json_path.write_text(json.dumps(json_content) if json_content != "broken" else "{broken")
    master = Fernet.generate_key()
    async with sessions.begin() as db:
        result = await run_import(db, json_path, env_path, master)
        rows = (await db.scalars(select(APIKey))).all()
        if rows:
            assert await (await CredentialService.open(db, tmp_path, master_key=master)).reveal(rows[0].id) == "synthetic-json"
    assert result["status"] == expected_status
    assert result["counts"]["imported"] == expected_count
    assert len(rows) == expected_count
    assert all("synthetic-env" not in row.ciphertext for row in rows)


async def test_env_entry_cap_rejects_entire_source_before_writes(sessions, tmp_path):
    json_path, env_path = paths(tmp_path,
        'OPENAI_API_KEY="' + "\n".join(f"synthetic-{i}" for i in range(5001)) + '"\n')
    async with sessions() as db:
        result = await run_import(db, json_path, env_path, Fernet.generate_key())
        assert (await db.scalars(select(APIKey))).all() == []
    assert result["status"] == "invalid_source"


@pytest.mark.parametrize("kind", ["missing", "malformed", "oversize", "symlink", "fifo", "duplicate_variable", "bare_variable"])
async def test_invalid_env_fails_closed(sessions, tmp_path, kind, caplog):
    json_path, env_path = paths(tmp_path, "OPENAI_API_KEY=synthetic-secret\n")
    if kind == "missing":
        env_path.unlink()
    elif kind == "malformed":
        env_path.write_text('OPENAI_API_KEY="synthetic-secret\n')
    elif kind == "oversize":
        env_path.write_bytes(b" " * (1024 * 1024 + 1))
    elif kind == "symlink":
        env_path.unlink()
        env_path.symlink_to(tmp_path / "target.env")
    elif kind == "fifo":
        env_path.unlink()
        os.mkfifo(env_path)
    elif kind == "duplicate_variable":
        env_path.write_text("OPENAI_API_KEY=synthetic-secret\nOPENAI_API_KEY=synthetic-other\n")
    elif kind == "bare_variable":
        env_path.write_text("OPENAI_API_KEY\n")
    async with sessions() as db:
        result = await run_import(db, json_path, env_path, Fernet.generate_key())
        assert (await db.scalars(select(APIKey))).all() == []
    assert result["status"] == ("missing_source" if kind == "missing" else "invalid_source")
    assert "synthetic-secret" not in str(result) + caplog.text


async def test_interpolation_is_literal_and_does_not_read_process_environment(sessions, tmp_path, monkeypatch):
    json_path, env_path = paths(tmp_path, 'OPENAI_API_KEY="${INJECTED_KEY}"\n')
    monkeypatch.setenv("INJECTED_KEY", "synthetic-process-secret")
    master = Fernet.generate_key()
    async with sessions.begin() as db:
        result = await run_import(db, json_path, env_path, master)
        row = (await db.scalars(select(APIKey))).one()
        revealed = await (await CredentialService.open(db, tmp_path, master_key=master)).reveal(row.id)
    assert result["counts"]["imported"] == 1
    assert revealed == "${INJECTED_KEY}"


@pytest.mark.parametrize("kind", ["symlink", "oversize", "missing_during_open"])
async def test_unreadable_json_never_falls_back_to_env(sessions, tmp_path, monkeypatch, kind):
    json_path, env_path = paths(tmp_path, "OPENAI_API_KEY=synthetic-env\n")
    if kind == "symlink":
        target = tmp_path / "target.json"
        target.write_text("{}")
        json_path.symlink_to(target)
    elif kind == "oversize":
        json_path.write_bytes(b" " * (1024 * 1024 + 1))
    else:
        json_path.write_text("{}")
        real_open = inventory_module.os.open

        def disappear_at_open(path, *args, **kwargs):
            if path == json_path:
                raise FileNotFoundError
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(inventory_module.os, "open", disappear_at_open)
    async with sessions() as db:
        result = await run_import(db, json_path, env_path, Fernet.generate_key())
        assert (await db.scalars(select(APIKey))).all() == []
    assert result["status"] == "invalid_source"
