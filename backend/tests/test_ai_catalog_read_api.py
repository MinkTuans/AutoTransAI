"""Canonical catalog GET contracts against disposable SQLite and synthetic credentials."""
from datetime import datetime
import socket

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.main import app
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig


@pytest.fixture
async def catalog_api(tmp_path, monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("Unexpected outbound connection")))
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for table in (Provider, APIKey, CatalogModel, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(table.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def isolated_db():
        async with sessions() as db:
            yield db

    app.dependency_overrides[get_db] = isolated_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions
    finally:
        app.dependency_overrides.pop(get_db, None)
        await engine.dispose()


async def test_dynamic_provider_counts_and_distinct_enabled_key_access(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add_all([Provider(id="openai", name="Open AI", provider_type="llm"),
                    Provider(id="fal", name="Fal", provider_type="video"),
                    Provider(id="empty", name="Empty", provider_type="llm")])
        await db.flush()
        model = CatalogModel(id="model-one", provider_id="openai", remote_model_id="remote-1",
                             display_name="First", source="discovered")
        public = CatalogModel(id="model-public", provider_id="fal", remote_model_id="fal/film",
                              source="discovered")
        keys = [APIKey(id=f"key-{n}", provider_id="openai", ciphertext=f"cipher-secret-{n}",
                       fingerprint=f"finger-secret-{n}", masked_key="****", enabled=n != 3)
                for n in (1, 2, 3)]
        fal_key = APIKey(id="fal-key", provider_id="fal", ciphertext="fal-secret",
                         fingerprint="fal-fingerprint", masked_key="****")
        db.add_all([model, public, *keys, fal_key])
        await db.flush()
        db.add_all([KeyModelAccess(key_id=k.id, model_id=model.id, provider_id="openai") for k in keys])
    providers = (await client.get("/api/ai/providers")).json()["data"]
    assert {p["id"] for p in providers} == {"openai", "fal", "empty"}
    assert next(p for p in providers if p["id"] == "empty")["enabled_key_count"] == 0
    assert next(p for p in providers if p["id"] == "openai")["model_count"] == 1
    models = (await client.get("/api/ai/models")).json()["data"]["items"]
    assert len(models) == 2
    assert next(m for m in models if m["id"] == "model-one")["available_key_count"] == 2
    public_row = next(m for m in models if m["id"] == "model-public")
    assert public_row["available_key_count"] == 1
    assert public_row["access_scope"] == "catalog_unverified"
    stt_rows = {m["id"]: m for m in (await client.get(
        "/api/ai/models", params={"capability": "STT"})).json()["data"]["items"]}
    assert stt_rows["model-one"]["capability"]["status"] == "FULL_UNKNOWN"
    assert stt_rows["model-one"]["selectable"] is True
    assert "secret" not in str(providers) + str(models)
    assert "fingerprint" not in str(providers) + str(models)


async def test_search_filter_pagination_status_defaults_and_read_only(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add_all([Provider(id="acme", name="Acme Studio", provider_type="llm"),
                    Provider(id="other", name="Other", provider_type="llm")])
        await db.flush()
        db.add_all([CatalogModel(id="one", provider_id="acme", remote_model_id="remote-alpha",
                                 display_name="Vision Alpha", source="manual", capability_status="KNOWN",
                                 capabilities=["VISUAL_GENDER"], discovery_metadata={"api_key": "secret-marker"}),
                    CatalogModel(id="two", provider_id="acme", remote_model_id="remote-beta",
                                 source="discovered", retired_at=datetime(2026, 1, 1)),
                    CatalogModel(id="three", provider_id="other", remote_model_id="remote-gamma",
                                 source="manual", capability_status="KNOWN", capabilities=["TTS"], enabled=False)])
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender",
                                capability="VISUAL_GENDER", primary_provider_id="acme", model_id="one"))
        db.add(AIFunctionConfig(function_id="stt", function_name="Speech to Text",
                                capability="STT", primary_provider_id="acme", model_id="two"))
    for term in ("remote-alpha", "Vision Alpha", "VISUAL_GENDER"):
        result = (await client.get("/api/ai/models", params={"q": term})).json()["data"]
        assert [m["id"] for m in result["items"]] == ["one"]
    assert {m["id"] for m in (await client.get("/api/ai/models", params={"q": "Acme Studio"})).json()["data"]["items"]} == {"one", "two"}
    unknown = (await client.get("/api/ai/models", params={"capability": "STT"})).json()["data"]
    assert {m["id"] for m in unknown["items"]} == {"two"}
    assert (await client.get("/api/ai/models", params={"provider_id": "missing"})).status_code == 404
    page = (await client.get("/api/ai/models", params={"page": 2, "limit": 1})).json()["data"]
    assert page["total"] == 3 and len(page["items"]) == 1
    assert (await client.get("/api/ai/models", params={"limit": 101})).status_code == 422
    detail = (await client.get("/api/ai/models/one")).json()["data"]
    assert detail["default_for"] == ["visual_gender"]
    assert detail["metadata"] == {}
    assert detail["status"] == "active"
    assert (await client.get("/api/ai/models/two")).json()["data"]["status"] == "retired"
    assert (await client.get("/api/ai/models/three")).json()["data"]["status"] == "disabled"
    assert (await client.get("/api/ai/models/missing")).status_code == 404
    functions = (await client.get("/api/ai/functions")).json()["data"]
    visual = next(row for row in functions if row['function_id'] == 'visual_gender')
    assert visual["model_id"] == "one" and visual["configuration_error"] is None
    assert visual["model_display_name"] == "Vision Alpha"
    stt = next(row for row in functions if row['function_id'] == 'stt')
    assert stt['model_display_name'] == 'remote-beta'
    assert stt['default_status'] == 'retired'
    assert "secret-marker" not in str(detail)
    async with sessions() as db:
        assert len((await db.scalars(select(CatalogModel))).all()) == 3
        assert len((await db.scalars(select(AIFunctionConfig))).all()) == 2


async def test_keyless_system_provider_is_ready_without_credentials(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False))
        await db.flush()
        db.add(CatalogModel(id="edge", provider_id="edge_tts", remote_model_id="edge-tts",
                            source="system", capability_status="KNOWN", capabilities=["TTS"]))
    provider = (await client.get("/api/ai/providers")).json()["data"][0]
    model = (await client.get("/api/ai/models/edge")).json()["data"]
    assert provider["status"] == "ready"
    assert provider["keyless"] is True
    assert model["access_scope"] == "keyless"


async def test_fresh_function_inventory_is_visible_without_database_writes(catalog_api):
    client, sessions = catalog_api
    functions = (await client.get('/api/ai/functions')).json()['data']
    assert {row['function_id'] for row in functions} == {
        'stt', 'translation', 'tts', 'video_generation', 'visual_gender', 'image_generation'
    }
    assert all(row['default_status'] == 'unconfigured' and row['model_display_name'] is None and
               row['primary_provider_id'] == '' and row['model_id'] == '' for row in functions)
    async with sessions() as db:
        assert (await db.scalars(select(AIFunctionConfig))).all() == []


async def test_keyless_provider_identity_does_not_depend_on_active_models(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add_all([Provider(id="edge_tts", name="Edge", provider_type="audio", requires_api_key=False),
                    Provider(id="pollinations", name="Pollinations", provider_type="image", requires_api_key=False),
                    Provider(id="local_image", name="Local Image", provider_type="image", requires_api_key=False),
                    Provider(id="local_video", name="Local Video", provider_type="video", requires_api_key=False),
                    Provider(id="unknown", name="Unknown", provider_type="video", is_custom=True),
                    Provider(id="openai", name="Open AI", provider_type="llm")])
        await db.flush()
    empty_rows = {row["id"]: row for row in (await client.get("/api/ai/providers")).json()["data"]}
    assert empty_rows["edge_tts"]["keyless"] is True
    assert empty_rows["pollinations"]["keyless"] is True
    assert empty_rows["local_image"]["keyless"] is True
    assert empty_rows["local_video"]["keyless"] is True
    assert empty_rows["openai"]["keyless"] is False
    assert empty_rows["unknown"]["keyless"] is False
    async with sessions.begin() as db:
        db.add(CatalogModel(id="retired-edge", provider_id="edge_tts", remote_model_id="edge-tts",
                            source="system", capability_status="KNOWN", capabilities=["TTS"],
                            retired_at=datetime(2026, 1, 1)))
    rows = {row["id"]: row for row in (await client.get("/api/ai/providers")).json()["data"]}
    assert rows["edge_tts"]["keyless"] is True
    assert rows["pollinations"]["keyless"] is True
    assert rows["local_image"]["keyless"] is True
    assert rows["local_video"]["keyless"] is True
    assert rows["openai"]["keyless"] is False


async def test_capability_filtered_keyless_eligibility_matches_function_write(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add_all([Provider(id="pollinations", name="Pollinations", provider_type="image"),
                    Provider(id="local_image", name="Local Image", provider_type="image"),
                    Provider(id="edge_tts", name="Edge", provider_type="audio")])
        await db.flush()
        db.add_all([
            CatalogModel(id="pollinations-model", provider_id="pollinations", remote_model_id="image-default",
                         source="system", capability_status="FULL_UNKNOWN"),
            CatalogModel(id="local-model", provider_id="local_image", remote_model_id="local-default",
                         source="system", capability_status="FULL_UNKNOWN"),
            CatalogModel(id="edge-model", provider_id="edge_tts", remote_model_id="edge-tts",
                         source="system", capability_status="FULL_UNKNOWN"),
        ])

    stt = {m["id"]: m for m in (await client.get("/api/ai/models", params={"capability": "STT"})).json()["data"]["items"]}
    for model_id in ("pollinations-model", "local-model"):
        assert stt[model_id]["capability"]["status"] == "FULL_UNKNOWN"
        assert stt[model_id]["selectable"] is False
        assert stt[model_id]["access_scope"] == "none"
    assert "edge-model" not in stt  # Known TTS-only evidence is filtered out.

    image = {m["id"]: m for m in (await client.get("/api/ai/models", params={"capability": "IMAGE_GENERATION"})).json()["data"]["items"]}
    for model_id in ("pollinations-model", "local-model"):
        assert image[model_id]["selectable"] is True
        assert image[model_id]["access_scope"] == "keyless"
    assert "edge-model" not in image

    tts = {m["id"]: m for m in (await client.get("/api/ai/models", params={"capability": "TTS"})).json()["data"]["items"]}
    assert tts["edge-model"]["selectable"] is True
    assert tts["edge-model"]["access_scope"] == "keyless"
    for model_id in ("pollinations-model", "local-model"):
        assert tts[model_id]["selectable"] is False

    unfiltered = {m["id"]: m for m in (await client.get("/api/ai/models")).json()["data"]["items"]}
    assert unfiltered["pollinations-model"]["access_scope"] == "keyless"
    assert unfiltered["pollinations-model"]["selectable"] is None
    detail = (await client.get("/api/ai/models/pollinations-model")).json()["data"]
    assert detail["access_scope"] == "keyless" and detail["selectable"] is None


async def test_unexpected_read_error_does_not_expose_credential_text(catalog_api, caplog):
    client, _ = catalog_api

    async def broken_db():
        raise RuntimeError("synthetic-ciphertext-and-fingerprint")
        yield  # pragma: no cover

    app.dependency_overrides[get_db] = broken_db
    response = await client.get("/api/ai/providers")
    assert response.status_code == 500
    assert "synthetic-ciphertext-and-fingerprint" not in response.text
    assert "synthetic-ciphertext-and-fingerprint" not in caplog.text


async def test_function_defaults_report_retired_missing_and_legacy_state(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="Open AI", provider_type="llm"))
        await db.flush()
        db.add(CatalogModel(id="retired-id", provider_id="openai", remote_model_id="remote-retired",
                            retired_at=datetime(2026, 1, 1)))
        db.add(CatalogModel(id="canonical-legacy", provider_id="openai", remote_model_id="old-model-name"))
        db.add_all([
            AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                             primary_provider_id="openai", model_id="retired-id"),
            AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                             primary_provider_id="openai", model_id="deleted-id"),
            AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                             primary_provider_id="openai", model_id="old-model-name"),
        ])
    functions = {f["function_id"]: f for f in (await client.get("/api/ai/functions")).json()["data"]}
    assert functions["stt"]["default_status"] == "retired"
    assert functions["stt"]["selectable"] is False
    assert functions["translation"]["default_status"] == "missing"
    assert functions["translation"]["selectable"] is False
    assert functions["visual_gender"]["default_status"] == "legacy_unmigrated"
    assert functions["visual_gender"]["selectable"] is False


async def test_catalog_gets_issue_no_database_writes(catalog_api):
    client, sessions = catalog_api
    engine = sessions.kw["bind"]
    writes = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"}:
            writes.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        for path in ("/api/ai/providers", "/api/ai/models", "/api/ai/models/absent", "/api/ai/functions"):
            response = await client.get(path)
            assert response.status_code in {200, 404}
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert writes == []


async def test_malformed_persisted_metadata_cannot_break_or_expand_detail(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(Provider(id="fal", name="Fal", provider_type="video"))
        await db.flush()
        db.add(CatalogModel(id="malformed", provider_id="fal", remote_model_id="fal/model",
                            discovery_metadata={"category": {"api_key": "synthetic-secret"},
                                                "ciphertext": "synthetic-secret"}))
    response = await client.get("/api/ai/models/malformed")
    assert response.status_code == 200
    assert response.json()["data"]["metadata"] == {}
    assert "synthetic-secret" not in response.text


async def test_function_error_text_is_restricted_to_known_codes(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="missing", model_id="missing",
                                configuration_error="synthetic-secret"))
    response = await client.get("/api/ai/functions")
    assert response.status_code == 200
    stt = next(row for row in response.json()['data'] if row['function_id'] == 'stt')
    assert stt["configuration_error"] == "configuration_error"
    assert "synthetic-secret" not in response.text


async def test_large_catalog_first_page_fetches_access_only_for_visible_models(catalog_api):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="Open AI", provider_type="llm"))
        await db.flush()
        keys = [APIKey(id=f"key-{n}", provider_id="openai", ciphertext=f"cipher-{n}",
                       fingerprint=f"finger-{n}", masked_key="****") for n in (1, 2)]
        db.add_all(keys)
        models = [CatalogModel(id=f"model-{n:04d}", provider_id="openai",
                               remote_model_id=f"remote-{n:04d}") for n in range(600)]
        db.add_all(models)
        await db.flush()
        db.add_all([KeyModelAccess(key_id=k.id, model_id=m.id, provider_id="openai")
                    for m in models for k in keys])
    statements = []
    model_statements = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        if "ai_key_model_access" in statement and statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)
        if "ai_catalog_models" in statement and statement.lstrip().upper().startswith("SELECT"):
            model_statements.append(statement)

    engine = sessions.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await client.get("/api/ai/models", params={"page": 1, "limit": 25})
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    page = response.json()["data"]
    assert page["total"] == 600
    assert [m["id"] for m in page["items"]] == [f"model-{n:04d}" for n in range(25)]
    assert all(m["available_key_count"] == 2 for m in page["items"])
    assert statements and all(" IN (" in statement.upper() for statement in statements)
    assert any("LIMIT" in statement.upper() for statement in model_statements)


async def test_filtered_page_closes_stream_before_loading_page_access(catalog_api, monkeypatch):
    client, sessions = catalog_api
    async with sessions.begin() as db:
        db.add(Provider(id="openai", name="Open AI", provider_type="llm"))
        await db.flush()
        db.add(APIKey(id="key", provider_id="openai", ciphertext="synthetic-cipher",
                      fingerprint="synthetic-fingerprint", masked_key="****"))
        models = [CatalogModel(id=f"model-{n:03d}", provider_id="openai",
                               remote_model_id=f"remote-{n:03d}") for n in range(200)]
        db.add_all(models)
        await db.flush()
        db.add_all([KeyModelAccess(key_id="key", model_id=m.id, provider_id="openai") for m in models])
    closed = [False]
    original_stream = AsyncSession.stream_scalars

    async def tracked_stream(self, *args, **kwargs):
        result = await original_stream(self, *args, **kwargs)

        class TrackedResult:
            def __aiter__(self):
                return result.__aiter__()

            async def close(self):
                await result.close()
                closed[0] = True

        return TrackedResult()

    monkeypatch.setattr(AsyncSession, "stream_scalars", tracked_stream)
    access_queries = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        if "ai_key_model_access" in statement and statement.lstrip().upper().startswith("SELECT"):
            access_queries.append((statement, closed[0]))

    engine = sessions.kw["bind"]
    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await client.get("/api/ai/models", params={"q": "remote-", "page": 2, "limit": 10})
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    page = response.json()["data"]
    assert page["total"] == 200
    assert [m["id"] for m in page["items"]] == [f"model-{n:03d}" for n in range(10, 20)]
    assert access_queries and all(was_closed and " IN (" in sql.upper() for sql, was_closed in access_queries)
