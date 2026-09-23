"""Dry-run inventory against disposable data only."""
import json

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, Provider
from app.models.settings import AIModel, AIFunctionConfig
from app.services.legacy_migration_inventory import inventory_legacy_migration


@pytest.fixture
async def inventory_db(tmp_path):
    path = tmp_path / "fixture.sqlite"
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, AIModel, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    yield sessions, path
    await engine.dispose()


async def test_inventory_counts_conflicts_and_preserves_db_and_secret_files(inventory_db, tmp_path, caplog):
    sessions, db_path = inventory_db
    secret = "synthetic-secret-never-visible-123"
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="OpenAI", provider_type="llm"))
        await db.flush()
        db.add_all([
            AIModel(id="shared", provider_id="openai", model_name="Shared", capabilities='["STT"]'),
            AIModel(id="orphan", provider_id="missing", model_name="Orphan", capabilities='["BAD"]'),
            AIModel(id="bad-json", provider_id="openai", model_name="Bad", capabilities="oops"),
            CatalogModel(id="canonical", provider_id="openai", remote_model_id="shared"),
            APIKey(id="key", provider_id="openai", ciphertext="synthetic-cipher", fingerprint="f" * 64, masked_key="****"),
            AIFunctionConfig(function_id="stt", function_name="STT", capability="STT", primary_provider_id="missing", model_id="shared", fallback_enabled=True, fallback_provider_id="absent"),
            AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS", primary_provider_id="openai", model_id="unknown"),
        ])
    key_path = tmp_path / "api_keys.json"
    key_path.write_text(json.dumps({"openai": [
        {"key_id": "one", "provider_id": "openai", "api_key": secret},
        {"key_id": "one", "provider_id": "wrong", "api_key": secret},
    ]}))
    env_path = tmp_path / ".env"
    env_path.write_text(f"OPENAI_API_KEY=other-{secret}\n")
    before = (db_path.read_bytes(), key_path.read_bytes(), env_path.read_bytes())
    async with sessions() as db:
        first = await inventory_legacy_migration(db, json_path=key_path, env_path=env_path)
        second = await inventory_legacy_migration(db, json_path=key_path, env_path=env_path)
    assert first == second
    assert first["counts"] == {
        "providers": 1, "legacy_models": 3, "function_configs": 2,
        "fallback_enabled": 1, "fallback_references": 1,
        "catalog_models": 1, "api_keys": 1,
        "json_providers": 1, "json_keys": 2, "env_providers": 1, "env_keys": 1,
        "effective_keys": 2, "duplicate_json_keys": 1, "duplicate_env_keys": 0,
        "key_provider_mismatches": 1, "source_disagreements": 1,
        "model_provider_conflicts": 1, "missing_model_providers": 1,
        "invalid_model_capabilities": 2, "unresolved_defaults": 2,
        "missing_fallback_providers": 1, "existing_canonical_identities": 1,
    }
    assert first["issues"] == [
        "duplicate_json_keys", "existing_canonical_identity", "invalid_model_capability",
        "key_provider_mismatch", "missing_fallback_provider", "missing_model_provider",
        "model_provider_conflict", "source_disagreement", "unresolved_default",
    ]
    assert first["key_source"] == "json"
    assert (db_path.read_bytes(), key_path.read_bytes(), env_path.read_bytes()) == before
    assert secret not in str(first) + caplog.text


async def test_missing_files_produce_empty_fixed_summary(inventory_db, tmp_path):
    sessions, _ = inventory_db
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=tmp_path / "absent.json")
    assert result["key_source"] == "none"
    assert result["issues"] == []
    assert all(value == 0 for value in result["counts"].values())


async def test_malformed_json_fails_visibly_without_env_fallback(inventory_db, tmp_path, caplog):
    sessions, _ = inventory_db
    secret = "synthetic-secret-error-456"
    path = tmp_path / "api_keys.json"
    path.write_text('{"openai": ["' + secret)
    env = tmp_path / ".env"
    env.write_text(f"OPENAI_API_KEY={secret}\n")
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=path, env_path=env)
    assert result["key_source"] == "invalid_json"
    assert result["counts"]["effective_keys"] == 0
    assert result["counts"]["env_keys"] == 1
    assert result["issues"] == ["invalid_json"]
    assert secret not in str(result) + caplog.text


async def test_refuses_symlinks_and_oversize_files(inventory_db, tmp_path):
    sessions, _ = inventory_db
    real = tmp_path / "real.json"
    real.write_text("{}")
    link = tmp_path / "api_keys.json"
    link.symlink_to(real)
    huge = tmp_path / ".env"
    huge.write_bytes(b"x" * (1024 * 1024 + 1))
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=link, env_path=huge)
    assert result["issues"] == ["env_file_too_large", "json_symlink_refused"]
    assert result["key_source"] == "invalid_json"


async def test_env_bootstrap_counts_supported_indexed_keys(inventory_db, tmp_path):
    sessions, _ = inventory_db
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=first\nOPENAI_API_KEY_1=second\nOPENAI_API_KEY_2=first\nOTHER_API_KEY=ignored\n")
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=tmp_path / "missing.json", env_path=env)
    assert result["key_source"] == "env"
    assert result["counts"]["env_keys"] == 3
    assert result["counts"]["effective_keys"] == 3
    assert result["counts"]["duplicate_env_keys"] == 1
    assert result["issues"] == ["duplicate_env_keys"]


async def test_invalid_late_json_entry_does_not_publish_partial_counts(inventory_db, tmp_path):
    sessions, _ = inventory_db
    path = tmp_path / "api_keys.json"
    path.write_text(json.dumps({"openai": [
        {"key_id": "valid", "provider_id": "openai", "api_key": "synthetic-secret"},
        {"key_id": "valid", "provider_id": "wrong", "api_key": "synthetic-secret"},
        {"key_id": "broken", "provider_id": "openai"},
    ]}))
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=path)
    assert result["key_source"] == "invalid_json"
    assert result["issues"] == ["invalid_json"]
    assert result["counts"]["json_keys"] == 0
    assert result["counts"]["duplicate_json_keys"] == 0
    assert result["counts"]["key_provider_mismatches"] == 0


async def test_empty_existing_json_is_authoritative_over_env(inventory_db, tmp_path):
    sessions, _ = inventory_db
    path = tmp_path / "api_keys.json"
    path.write_text("{}")
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=synthetic-secret\n")
    async with sessions() as db:
        result = await inventory_legacy_migration(db, json_path=path, env_path=env)
    assert result["key_source"] == "json"
    assert result["counts"]["effective_keys"] == 0
    assert result["counts"]["source_disagreements"] == 1
