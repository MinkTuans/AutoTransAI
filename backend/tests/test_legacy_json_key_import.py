"""Synthetic, disposable coverage for the disabled legacy JSON key importer."""
import json
from datetime import datetime

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, Provider
from app.services.credential_service import CredentialService
from app.services.legacy_json_key_import import import_legacy_json_keys


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
            Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False),
        ])
    yield factory
    await engine.dispose()


def entry(secret, **fields):
    return {"key_id": "legacy-id", "provider_id": "openai", "api_key": secret, **fields}


def write_json(path, data):
    path.write_bytes(json.dumps(data).encode())
    return path.read_bytes()


async def test_imports_multiple_disabled_keys_with_safe_metadata_and_no_plaintext(sessions, tmp_path, caplog):
    secret_a = "synthetic-secret-one-1234"
    secret_b = "synthetic-secret-two-5678"
    path = tmp_path / "api_keys.json"
    original = write_json(path, {"openai": [
        entry(secret_a, priority=2, status="active", total_requests=7,
              successful_requests=5, failed_requests=2, last_error="private diagnostic",
              quota_info={"private": secret_a}),
        entry(secret_b, key_id="legacy-id-2", priority=3, status="rate_limited",
              cooldown_until=1893456000),
    ]})
    master = Fernet.generate_key()
    async with sessions() as db:
        result = await import_legacy_json_keys(db, json_path=path, master_key=master)
        assert result == {"status": "imported", "counts": {"imported": 2, "duplicate_source": 0,
            "duplicate_existing": 0, "skipped_missing_provider": 0, "skipped_keyless_provider": 0,
            "normalized_metadata": 0}}
        rows = (await db.scalars(select(APIKey).order_by(APIKey.priority))).all()
        assert len(rows) == 2
        assert all(not row.enabled for row in rows)
        assert (rows[0].priority, rows[0].runtime_status, rows[0].request_count,
                rows[0].success_count, rows[0].failure_count) == (2, "ready", 7, 5, 2)
        assert rows[0].last_error_code is None
        assert rows[1].runtime_status == "rate_limited"
        assert rows[1].cooldown_until == datetime(2030, 1, 1)
        assert all("legacy-id" not in row.id for row in rows)
        assert all(secret not in row.ciphertext for row in rows for secret in (secret_a, secret_b))
        assert await (await CredentialService.open(db, tmp_path, master_key=master)).reveal(rows[0].id) == secret_a
        assert all(secret not in str(result) + caplog.text for secret in (secret_a, secret_b))
        assert "legacy-id" not in str(result) + caplog.text
        await db.rollback()
    async with sessions() as db:
        assert (await db.scalars(select(APIKey))).all() == []
    assert path.read_bytes() == original
    assert not (tmp_path / ".api_key_master_key").exists()


async def test_duplicate_source_existing_and_repeat_are_idempotent(sessions, tmp_path):
    master = Fernet.generate_key()
    path = tmp_path / "api_keys.json"
    write_json(path, {"openai": [entry("synthetic-existing"), entry("synthetic-new", key_id="two"),
                                 entry("synthetic-new", key_id="three")]})
    async with sessions.begin() as db:
        await (await CredentialService.open(db, tmp_path, master_key=master)).create("openai", "synthetic-existing")
    async with sessions.begin() as db:
        first = await import_legacy_json_keys(db, json_path=path, master_key=master)
        revision_after_first = (await db.get(Provider, "openai")).catalog_revision
    async with sessions.begin() as db:
        second = await import_legacy_json_keys(db, json_path=path, master_key=master)
        rows = (await db.scalars(select(APIKey))).all()
        revision_after_second = (await db.get(Provider, "openai")).catalog_revision
    assert first["counts"]["imported"] == 1
    assert first["counts"]["duplicate_source"] == 1
    assert first["counts"]["duplicate_existing"] == 1
    assert second["counts"]["imported"] == 0
    assert len(rows) == 2
    assert revision_after_second == revision_after_first
    assert all(row.id != "legacy-id" for row in rows)


@pytest.mark.parametrize("kind", ["missing", "malformed", "symlink", "nonregular", "oversize", "invalid_entry", "mismatch", "too_many"])
async def test_bad_sources_fail_closed_without_writes(sessions, tmp_path, kind, caplog):
    path = tmp_path / "api_keys.json"
    secret = "synthetic-secret-sentinel"
    if kind == "malformed":
        path.write_text('{"openai": ["' + secret)
    elif kind == "symlink":
        target = tmp_path / "target.json"
        write_json(target, {"openai": [entry(secret)]})
        path.symlink_to(target)
    elif kind == "nonregular":
        path.mkdir()
    elif kind == "oversize":
        path.write_bytes(b" " * (1024 * 1024 + 1))
    elif kind == "invalid_entry":
        write_json(path, {"openai": [entry(secret), {"key_id": "bad", "provider_id": "openai"}]})
    elif kind == "mismatch":
        write_json(path, {"openai": [entry(secret), entry(secret + "-2", provider_id="wrong")]})
    elif kind == "too_many":
        write_json(path, {"openai": [entry(secret)] * 5001})
    async with sessions() as db:
        result = await import_legacy_json_keys(db, json_path=path, master_key=Fernet.generate_key())
        assert (await db.scalars(select(APIKey))).all() == []
    assert result["status"] == ("missing_source" if kind == "missing" else "invalid_source")
    assert secret not in str(result) + caplog.text


async def test_skips_missing_and_keyless_providers_and_normalizes_invalid_metadata(sessions, tmp_path):
    path = tmp_path / "api_keys.json"
    write_json(path, {"missing": [{**entry("synthetic-missing"), "provider_id": "missing"}],
                      "edge_tts": [{**entry("synthetic-keyless"), "provider_id": "edge_tts"}],
                      "openai": [entry("synthetic-valid", priority=0, status="unknown",
                                       total_requests=-4, successful_requests="bad",
                                       failed_requests=2, cooldown_until="bad")]})
    async with sessions.begin() as db:
        result = await import_legacy_json_keys(db, json_path=path, master_key=Fernet.generate_key())
        rows = (await db.scalars(select(APIKey))).all()
        assert len(rows) == 1
        assert (rows[0].priority, rows[0].runtime_status, rows[0].request_count,
                rows[0].success_count, rows[0].failure_count, rows[0].cooldown_until) == (100, "ready", 0, 0, 2, None)
    assert result["counts"]["skipped_missing_provider"] == 1
    assert result["counts"]["skipped_keyless_provider"] == 1
    assert result["counts"]["normalized_metadata"] >= 1


async def test_caller_rollback_removes_flushed_import_and_database_has_no_plaintext(sessions, tmp_path):
    secret = "synthetic-rollback-secret"
    path = tmp_path / "api_keys.json"
    original = write_json(path, {"openai": [entry(secret)]})
    async with sessions() as db:
        result = await import_legacy_json_keys(db, json_path=path, master_key=Fernet.generate_key())
        assert result["counts"]["imported"] == 1
        assert len((await db.scalars(select(APIKey))).all()) == 1
        await db.rollback()
    async with sessions() as db:
        assert (await db.scalars(select(APIKey))).all() == []
    assert secret.encode() not in (tmp_path / "keys.sqlite").read_bytes()
    assert path.read_bytes() == original
