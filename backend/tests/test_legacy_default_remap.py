"""Legacy default remapping against synthetic, disposable SQLite only."""
import json
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import MetaData, String, event, select
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIModel, AIFunctionConfig
from app.services.legacy_default_remap import remap_legacy_function_defaults
from tests.test_voice_version_width import mysql_db


async def test_shadow_comparison_reports_remap_without_writing(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
    async with db_factory.begin() as db:
        statements = []
        event.listen(db_factory.kw['bind'].sync_engine, 'before_cursor_execute',
                     lambda c, cur, sql, p, ctx, many: statements.append(sql))
        preview = await remap_legacy_function_defaults(db, dry_run=True)
        assert preview['counts']['resolved'] == 1 and preview['issues'] == []
        row = await db.get(AIFunctionConfig, 'stt')
        assert row.model_id == 'remote-stt' and row.configuration_error is None
        assert not any(sql.lstrip().upper().startswith(('UPDATE', 'INSERT', 'DELETE'))
                       for sql in statements)
        actual = await remap_legacy_function_defaults(db)
        assert actual == preview


async def test_shadow_comparison_rejects_pending_writes_without_flushing(db_factory):
    async with db_factory.begin() as db:
        await seed(db, catalog=False)
    async with db_factory() as db:
        config = await db.get(AIFunctionConfig, 'stt')
        config.function_name = 'uncommitted private name'
        statements = []
        event.listen(db_factory.kw['bind'].sync_engine, 'before_cursor_execute',
                     lambda c, cur, sql, p, ctx, many: statements.append(sql))
        with pytest.raises(RuntimeError, match='clean session'):
            await remap_legacy_function_defaults(db, dry_run=True)
        assert config.function_name == 'uncommitted private name'
        assert not any(sql.lstrip().upper().startswith(('UPDATE', 'INSERT', 'DELETE'))
                       for sql in statements)
        await db.rollback()


async def test_shadow_comparison_rejects_relevant_pending_default_change(db_factory):
    async with db_factory.begin() as db:
        model = await seed(db)
    async with db_factory() as db:
        config = await db.get(AIFunctionConfig, 'stt')
        config.model_id = model.id
        with pytest.raises(RuntimeError, match='clean session'):
            await remap_legacy_function_defaults(db, dry_run=True)
        assert config.model_id == model.id
        await db.rollback()


async def test_mysql_shadow_comparison_does_not_take_row_locks(mysql_db):
    for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
        model.__table__.create(mysql_db)
    mysql_db.commit()
    url = mysql_db.engine.url.set(drivername='mysql+aiomysql')
    engine = create_async_engine(url)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as db:
            await seed(db)
        statements = []
        event.listen(engine.sync_engine, 'before_cursor_execute',
                     lambda c, cur, sql, p, ctx, many: statements.append(sql))
        async with sessions() as db:
            preview = await remap_legacy_function_defaults(db, dry_run=True)
            assert preview['counts']['resolved'] == 1
            assert not any('FOR UPDATE' in sql.upper() for sql in statements)
            statements.clear()
            await remap_legacy_function_defaults(db)
            assert any('FOR UPDATE' in sql.upper() for sql in statements)
            await db.rollback()
    finally:
        await engine.dispose()


async def test_mysql_shadow_snapshot_can_differ_from_later_locked_execution(mysql_db):
    for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
        model.__table__.create(mysql_db)
    mysql_db.commit()
    engine = create_async_engine(mysql_db.engine.url.set(drivername='mysql+aiomysql'))
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions.begin() as db:
            await seed(db, catalog=False)
        async with sessions() as caller:
            assert (await caller.scalar(select(Provider.id))) == 'openai'
            async with sessions.begin() as writer:
                writer.add(CatalogModel(id='11111111-1111-4111-8111-111111111111',
                                        provider_id='openai', remote_model_id='remote-stt',
                                        source='discovered', capability_status='FULL_UNKNOWN',
                                        capabilities=[]))
                await writer.flush()
                writer.add(KeyModelAccess(key_id='22222222-2222-4222-8222-222222222222',
                                          model_id='11111111-1111-4111-8111-111111111111',
                                          provider_id='openai'))
            preview = await remap_legacy_function_defaults(caller, dry_run=True)
            assert preview['issues'] == ['missing_catalog_model']
            actual = await remap_legacy_function_defaults(caller)
            assert actual['counts']['resolved'] == 1
            await caller.rollback()
    finally:
        await engine.dispose()


@pytest.fixture
async def db_factory(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'defaults.sqlite'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    yield sessions
    await engine.dispose()


@pytest.fixture
async def nocase_db_factory(tmp_path):
    """Emulate MySQL-style case-insensitive equality on identity columns."""
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'nocase.sqlite'}")
    metadata = MetaData()
    for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIModel, AIFunctionConfig):
        model.__table__.to_metadata(metadata)
    for table_name, column_names in {
        "providers": ("id",),
        "ai_models": ("id", "provider_id"),
        "ai_catalog_models": ("id", "provider_id", "remote_model_id"),
        "api_keys": ("provider_id",),
        "ai_key_model_access": ("model_id", "provider_id"),
    }.items():
        for name in column_names:
            column = metadata.tables[table_name].c[name]
            column.type = String(column.type.length, collation="NOCASE")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    yield sessions
    await engine.dispose()


async def seed(db, *, function_id="stt", provider="openai", remote="remote-stt", capability="STT",
               legacy_caps='["STT"]', catalog=True, source="discovered", catalog_caps=(),
               status="FULL_UNKNOWN", access=True, key=True, model_enabled=True,
               provider_enabled=True, retired=False, error=None, metadata=None):
    db.add(Provider(id=provider, name=provider, provider_type="llm", enabled=provider_enabled))
    db.add(AIModel(id=remote, provider_id=provider, model_name="archival", capabilities=legacy_caps,
                   is_default=True, description="unchanged historical row"))
    db.add(AIFunctionConfig(function_id=function_id, function_name="Speech", capability=capability,
                            primary_provider_id=provider, model_id=remote, configuration_error=error,
                            fallback_enabled=True, fallback_provider_id="old_fallback"))
    await db.flush()
    model = None
    if catalog:
        model = CatalogModel(id="11111111-1111-4111-8111-111111111111", provider_id=provider,
                             remote_model_id=remote, source=source, capabilities=list(catalog_caps),
                             capability_status=status, discovery_metadata=metadata,
                             enabled=model_enabled,
                             retired_at=datetime(2026, 1, 1) if retired else None)
        db.add(model)
        await db.flush()
    if key:
        credential = APIKey(id="22222222-2222-4222-8222-222222222222", provider_id=provider,
                            ciphertext="synthetic-only", fingerprint="a" * 64, masked_key="****")
        db.add(credential)
        await db.flush()
        if access and model:
            db.add(KeyModelAccess(key_id=credential.id, model_id=model.id, provider_id=provider))
    return model


async def test_matching_accessible_model_remaps_without_touching_archive_or_fallback(db_factory):
    async with db_factory.begin() as db:
        model = await seed(db, error="legacy_default_unresolved")
    async with db_factory.begin() as db:
        archive = await db.get(AIModel, "remote-stt")
        before = tuple(getattr(archive, column.name) for column in AIModel.__table__.columns)
        config = await db.get(AIFunctionConfig, "stt")
        fallback = (config.fallback_enabled, config.fallback_provider_id)
        first = await remap_legacy_function_defaults(db)
        assert first == {"counts": {"resolved": 1, "unresolved": 0, "already_canonical": 0, "conflicts": 0}, "issues": []}
        assert config.model_id == model.id and config.primary_provider_id == "openai"
        assert config.configuration_error is None
        assert (config.fallback_enabled, config.fallback_provider_id) == fallback
        archive = await db.get(AIModel, "remote-stt")
        assert tuple(getattr(archive, column.name) for column in AIModel.__table__.columns) == before
        updated_at = config.updated_at
        second = await remap_legacy_function_defaults(db)
        await db.flush()
        assert second["counts"] == {"resolved": 0, "unresolved": 0, "already_canonical": 1, "conflicts": 0}
        assert config.updated_at == updated_at
    async with db_factory() as db:
        assert (await db.get(AIFunctionConfig, "stt")).model_id == model.id


async def test_rollback_restores_original_default(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
    async with db_factory() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"]["resolved"] == 1
        await db.flush()
        await db.rollback()
    async with db_factory() as db:
        row = await db.get(AIFunctionConfig, "stt")
        assert row.model_id == "remote-stt" and row.configuration_error is None


@pytest.mark.parametrize("change,issue", [
    ("missing_catalog", "missing_catalog_model"),
    ("retired", "catalog_unavailable"),
    ("model_disabled", "catalog_unavailable"),
    ("provider_disabled", "catalog_unavailable"),
    ("incompatible", "capability_mismatch"),
    ("no_key", "no_credential_access"),
    ("no_access", "no_credential_access"),
    ("invalid_key", "no_credential_access"),
    ("cooldown", "no_credential_access"),
    ("manual_catalog", "catalog_unavailable"),
    ("invalid_legacy_caps", "invalid_legacy_capability"),
    ("legacy_mismatch", "capability_mismatch"),
])
async def test_unresolved_default_stays_visible_and_preserves_choice(db_factory, change, issue):
    async with db_factory.begin() as db:
        await seed(db, provider="gemini" if change == "incompatible" else "openai",
                   capability="TRANSLATION" if change == "incompatible" else "STT",
                   catalog=change != "missing_catalog", retired=change == "retired",
                   model_enabled=change != "model_disabled", provider_enabled=change != "provider_disabled",
                   source="manual" if change == "manual_catalog" else "discovered",
                   status="KNOWN" if change == "incompatible" else "FULL_UNKNOWN",
                   metadata={"supportedGenerationMethods": []} if change == "incompatible" else None,
                   key=change != "no_key", access=change != "no_access",
                   legacy_caps="bad-json" if change == "invalid_legacy_caps" else
                               '["TTS"]' if change == "legacy_mismatch" else
                               '["TRANSLATION"]' if change == "incompatible" else '["STT"]')
        if change == "invalid_key":
            (await db.get(APIKey, "22222222-2222-4222-8222-222222222222")).runtime_status = "invalid"
        if change == "cooldown":
            (await db.get(APIKey, "22222222-2222-4222-8222-222222222222")).cooldown_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1)
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        row = await db.get(AIFunctionConfig, "stt")
        assert row.model_id == "remote-stt" and row.primary_provider_id == ("gemini" if change == "incompatible" else "openai")
        assert row.configuration_error == "legacy_default_unresolved"
        assert row.fallback_enabled and row.fallback_provider_id == "old_fallback"
        assert result["counts"]["unresolved"] == 1 and result["issues"] == [issue]


async def test_default_sentinel_and_missing_provider_fail_closed(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
        db.add(Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False))
        db.add(AIFunctionConfig(function_id="tts", function_name="Voice", capability="TTS",
                                primary_provider_id="edge_tts", model_id="default"))
        db.add(AIFunctionConfig(function_id="image_generation", function_name="Image", capability="IMAGE_GENERATION",
                                primary_provider_id="missing", model_id="remote"))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"] == {"resolved": 1, "unresolved": 2, "already_canonical": 0, "conflicts": 0}
        assert result["issues"] == ["default_sentinel", "missing_provider"]
        for name in ("tts", "image_generation"):
            row = await db.get(AIFunctionConfig, name)
            assert row.configuration_error == "legacy_default_unresolved"


async def test_default_sentinel_never_becomes_canonical_even_with_id_collision(db_factory):
    async with db_factory.begin() as db:
        db.add(Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False))
        await db.flush()
        db.add(CatalogModel(id="default", provider_id="edge_tts", remote_model_id="edge-tts",
                            source="system", capability_status="KNOWN", capabilities=["TTS"]))
        db.add(AIFunctionConfig(function_id="tts", function_name="Voice", capability="TTS",
                                primary_provider_id="edge_tts", model_id="default"))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"] == {"resolved": 0, "unresolved": 1, "already_canonical": 0, "conflicts": 0}
        assert result["issues"] == ["default_sentinel"]
        assert (await db.get(AIFunctionConfig, "tts")).configuration_error == "legacy_default_unresolved"


async def test_keyless_edge_system_model_is_eligible(db_factory):
    async with db_factory.begin() as db:
        model = await seed(db, provider="edge_tts", remote="edge-tts", capability="TTS",
                           legacy_caps='["TTS"]', source="system", key=False,
                           status="KNOWN", catalog_caps=["TTS"])
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"]["resolved"] == 1
        assert (await db.get(AIFunctionConfig, "stt")).model_id == model.id


async def test_already_canonical_and_foreign_uuid_collision(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
        db.add(Provider(id="gemini", name="Gemini", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="33333333-3333-4333-8333-333333333333", provider_id="gemini",
                            remote_model_id="other"))
        db.add(CatalogModel(id="44444444-4444-4444-8444-444444444444", provider_id="openai",
                            remote_model_id="retired", retired_at=datetime(2026, 1, 1)))
        db.add(AIModel(id="33333333-3333-4333-8333-333333333333", provider_id="openai",
                       model_name="Archive", capabilities='["STT"]'))
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="STT",
                                primary_provider_id="openai", model_id="33333333-3333-4333-8333-333333333333"))
        db.add(AIFunctionConfig(function_id="tts", function_name="Voice", capability="STT",
                                primary_provider_id="openai", model_id="11111111-1111-4111-8111-111111111111",
                                configuration_error="unrelated_error"))
        db.add(AIFunctionConfig(function_id="video_generation", function_name="Video", capability="VIDEO_GENERATION",
                                primary_provider_id="openai", model_id="44444444-4444-4444-8444-444444444444",
                                configuration_error="unrelated_error"))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"] == {"resolved": 1, "unresolved": 1, "already_canonical": 2, "conflicts": 1}
        assert (await db.get(AIFunctionConfig, "translation")).model_id == "33333333-3333-4333-8333-333333333333"
        assert (await db.get(AIFunctionConfig, "translation")).configuration_error == "legacy_default_unresolved"
        assert (await db.get(AIFunctionConfig, "tts")).configuration_error == "unrelated_error"
        retired_default = await db.get(AIFunctionConfig, "video_generation")
        assert retired_default.model_id == "44444444-4444-4444-8444-444444444444"
        assert retired_default.configuration_error == "unrelated_error"


async def test_foreign_catalog_uuid_is_remapped_by_archival_provider_and_remote_identity(db_factory):
    foreign_uuid = "33333333-3333-4333-8333-333333333333"
    async with db_factory.begin() as db:
        target = await seed(db, remote=foreign_uuid)
        db.add(Provider(id="gemini", name="Gemini", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id=foreign_uuid, provider_id="gemini", remote_model_id="other"))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"]["resolved"] == 1
        assert (await db.get(AIFunctionConfig, "stt")).model_id == target.id


async def test_archival_provider_mismatch_is_a_conflict(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
        (await db.get(AIModel, "remote-stt")).provider_id = "gemini"
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"] == {"resolved": 0, "unresolved": 1, "already_canonical": 0, "conflicts": 1}
        assert result["issues"] == ["legacy_provider_conflict"]
        assert (await db.get(AIFunctionConfig, "stt")).model_id == "remote-stt"


@pytest.mark.parametrize("variant,expected_issue", [
    ("provider", "missing_provider"),
    ("legacy_id", "missing_legacy_model"),
    ("catalog_remote", "missing_catalog_model"),
    ("catalog_provider", "missing_catalog_model"),
    ("key_provider", "no_credential_access"),
    ("edge_provider", "no_credential_access"),
])
async def test_nocase_sql_matches_do_not_change_exact_legacy_identity(nocase_db_factory, variant, expected_issue):
    async with nocase_db_factory.begin() as db:
        await seed(db)
        if variant == "provider":
            (await db.get(AIFunctionConfig, "stt")).primary_provider_id = "OpenAI"
        elif variant == "legacy_id":
            (await db.get(AIFunctionConfig, "stt")).model_id = "REMOTE-STT"
        elif variant == "catalog_remote":
            (await db.get(CatalogModel, "11111111-1111-4111-8111-111111111111")).remote_model_id = "REMOTE-STT"
        elif variant == "catalog_provider":
            (await db.get(CatalogModel, "11111111-1111-4111-8111-111111111111")).provider_id = "OpenAI"
            (await db.get(APIKey, "22222222-2222-4222-8222-222222222222")).provider_id = "OpenAI"
            (await db.get(KeyModelAccess, ("22222222-2222-4222-8222-222222222222",
                                           "11111111-1111-4111-8111-111111111111"))).provider_id = "OpenAI"
        elif variant == "key_provider":
            (await db.get(APIKey, "22222222-2222-4222-8222-222222222222")).provider_id = "OpenAI"
        else:
            (await db.get(KeyModelAccess, ("22222222-2222-4222-8222-222222222222",
                                           "11111111-1111-4111-8111-111111111111"))).provider_id = "OpenAI"
    async with nocase_db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        config = await db.get(AIFunctionConfig, "stt")
        assert result["counts"]["resolved"] == 0
        assert result["issues"] == [expected_issue]
        assert config.model_id == ("REMOTE-STT" if variant == "legacy_id" else "remote-stt")
        assert config.primary_provider_id == ("OpenAI" if variant == "provider" else "openai")
        assert config.configuration_error == "legacy_default_unresolved"


async def test_non_uuid_catalog_id_collision_does_not_hide_legacy_choice(db_factory):
    async with db_factory.begin() as db:
        target = await seed(db)
        db.add(CatalogModel(id="remote-stt", provider_id="openai", remote_model_id="unrelated"))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["counts"]["resolved"] == 1
        assert (await db.get(AIFunctionConfig, "stt")).model_id == target.id


async def test_ambiguous_catalog_identity_stays_unresolved(db_factory):
    # A damaged/imported catalog may predate its unique identity constraint.
    engine = db_factory.kw["bind"]
    async with engine.begin() as conn:
        await conn.exec_driver_sql("CREATE TABLE ai_catalog_models_copy AS SELECT * FROM ai_catalog_models WHERE 0")
        await conn.exec_driver_sql("DROP TABLE ai_catalog_models")
        await conn.exec_driver_sql("ALTER TABLE ai_catalog_models_copy RENAME TO ai_catalog_models")
    async with db_factory.begin() as db:
        db.add(Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False))
        db.add(AIModel(id="edge-tts", provider_id="edge_tts", model_name="Archive", capabilities='["TTS"]'))
        db.add(AIFunctionConfig(function_id="tts", function_name="Voice", capability="TTS",
                                primary_provider_id="edge_tts", model_id="edge-tts"))
        await db.flush()
        for number in (1, 2):
            db.add(CatalogModel(id=f"{number:08d}-1111-4111-8111-111111111111", provider_id="edge_tts",
                                remote_model_id="edge-tts", source="system", capability_status="KNOWN",
                                capabilities=["TTS"]))
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["issues"] == ["ambiguous_catalog_model"]
        assert (await db.get(AIFunctionConfig, "tts")).model_id == "edge-tts"


async def test_public_listing_uses_eligible_provider_key_without_edge(db_factory):
    async with db_factory.begin() as db:
        model = await seed(db, provider="fal", remote="image-model", capability="IMAGE_GENERATION",
                           legacy_caps='["IMAGE_GENERATION"]', access=False)
    async with db_factory.begin() as db:
        assert (await remap_legacy_function_defaults(db))["counts"]["resolved"] == 1
        assert (await db.get(AIFunctionConfig, "stt")).model_id == model.id


async def test_summary_contains_only_fixed_codes_and_counts(db_factory):
    async with db_factory.begin() as db:
        await seed(db, remote="synthetic-user-model-name", catalog=False)
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert set(result) == {"counts", "issues"}
        assert set(result["counts"]) == {"resolved", "unresolved", "already_canonical", "conflicts"}
        assert "synthetic-user-model-name" not in json.dumps(result)


async def test_malformed_function_capability_fails_closed(db_factory):
    async with db_factory.begin() as db:
        await seed(db, capability="not-a-capability")
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["issues"] == ["invalid_function_capability"]
        row = await db.get(AIFunctionConfig, "stt")
        assert row.model_id == "remote-stt" and row.configuration_error == "legacy_default_unresolved"


async def test_deep_legacy_capability_json_fails_closed(db_factory):
    async with db_factory.begin() as db:
        await seed(db, legacy_caps="[" * 10000 + '"STT"' + "]" * 10000)
    async with db_factory.begin() as db:
        result = await remap_legacy_function_defaults(db)
        assert result["issues"] == ["invalid_legacy_capability"]
        row = await db.get(AIFunctionConfig, "stt")
        assert row.model_id == "remote-stt" and row.configuration_error == "legacy_default_unresolved"


async def test_unresolved_repeat_has_no_revision_or_timestamp_drift(db_factory):
    async with db_factory.begin() as db:
        await seed(db, catalog=False)
    async with db_factory.begin() as db:
        first = await remap_legacy_function_defaults(db)
        config = await db.get(AIFunctionConfig, "stt")
        provider = await db.get(Provider, "openai")
        timestamp = config.updated_at
        revision = provider.catalog_revision
        second = await remap_legacy_function_defaults(db)
        assert first == second
        assert config.updated_at == timestamp and provider.catalog_revision == revision
        assert (await db.scalars(select(CatalogModel))).all() == []


async def test_recheck_uses_mysql_current_locking_reads(db_factory):
    async with db_factory.begin() as db:
        await seed(db)
    statements = []

    def capture(_conn, _cursor, _statement, _params, context, _many):
        compiled = getattr(context, "compiled", None)
        if compiled is not None and getattr(compiled.statement, "_for_update_arg", None) is not None:
            statements.append(str(compiled.statement.compile(dialect=mysql.dialect())))

    engine = db_factory.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        async with db_factory.begin() as db:
            await remap_legacy_function_defaults(db)
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert any("FROM ai_function_configs" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("FROM providers" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("FROM ai_catalog_models" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("FROM ai_models" in sql and "FOR UPDATE" in sql for sql in statements)
    assert any("FROM api_keys" in sql and "FOR UPDATE" in sql for sql in statements)
    provider_lock = next(index for index, sql in enumerate(statements) if "FROM providers" in sql)
    config_lock = next(index for index, sql in enumerate(statements) if "FROM ai_function_configs" in sql)
    assert provider_lock < config_lock
