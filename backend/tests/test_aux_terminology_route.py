"""Canonical terminology LLM routing without live credentials or provider calls."""

import asyncio
import json
import socket

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import RouteConfigurationError, RouteExhausted
from app.services.credential_service import CredentialService
from app.services import terminology_extractor as terms


@pytest.fixture(autouse=True)
def no_outbound_network(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("terminology test attempted outbound network")

    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(httpx.AsyncClient, "request", reject)
    monkeypatch.setattr(httpx.AsyncClient, "get", reject)
    monkeypatch.setattr(httpx.AsyncClient, "post", reject)


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("openai", "gemini", "anthropic"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, provider, remote, secret, *, metadata=None):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=["LLM"], discovery_metadata=metadata or {})
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def term_response(source="Alice", translated="An"):
    return json.dumps({"terms": [{"source_term": source, "suggested_term": translated,
                                    "term_type": "character", "confidence": 0.9}]})


@pytest.mark.asyncio
async def test_terminology_uses_default_then_cross_provider_with_exact_request_credentials(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        primary = await add_model(db, path, "openai", "primary-v9", "synthetic-primary")
        await add_model(db, path, "gemini", "backup-v3", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=primary.id))
    calls = []

    class LLM:
        async def generate_text(self, prompt, *, route_target, api_key):
            calls.append((route_target.provider_id, route_target.remote_model_id, api_key))
            if route_target.provider_id == "openai":
                error = RuntimeError("secret remote body")
                error.http_status = 404
                raise error
            return term_response()

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: LLM()})(), raising=False)
    result = await terms.llm_extract_terms("Alice says hello there", sessions=sessions, data_dir=path)
    assert result[0]["source_term"] == "Alice"
    assert calls == [("openai", "primary-v9", "synthetic-primary"),
                     ("gemini", "backup-v3", "synthetic-backup")]


@pytest.mark.asyncio
async def test_terminology_concurrent_jobs_do_not_share_model_or_key(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        primary = await add_model(db, path, "openai", "first-v1", "synthetic-first")
        await add_model(db, path, "openai", "second-v2", "synthetic-second")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=primary.id))
    seen = []

    class LLM:
        async def generate_text(self, prompt, *, route_target, api_key):
            await asyncio.sleep(0)
            seen.append((prompt[-20:], route_target.remote_model_id, api_key))
            return term_response()

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: LLM()})(), raising=False)
    results = await asyncio.gather(*(terms.llm_extract_terms(f"Alice sentence {n}", sessions=sessions, data_dir=path)
                                     for n in range(2)))
    assert len(results) == 2 and all(item[0]["source_term"] == "Alice" for item in results)
    assert len(seen) == 2
    assert {(model, key) for _, model, key in seen} == {("first-v1", "synthetic-first")}


@pytest.mark.asyncio
async def test_terminology_invalid_default_fails_without_legacy_escape(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "openai", "available", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id="nonexistent"))
    monkeypatch.setattr(terms, "get_registry", lambda: (_ for _ in ()).throw(AssertionError("legacy escape")), raising=False)
    with pytest.raises(RouteConfigurationError):
        await terms.llm_extract_terms("Alice sentence", sessions=sessions, data_dir=path)


@pytest.mark.asyncio
async def test_terminology_missing_adapter_is_classified_not_silent_success(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        primary = await add_model(db, path, "anthropic", "unsupported-v1", "synthetic")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="anthropic", model_id=primary.id))
    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: None})(), raising=False)
    with pytest.raises(RouteExhausted, match="capability_mismatch") as error:
        await terms.llm_extract_terms("Alice sentence", sessions=sessions, data_dir=path)
    assert "synthetic" not in str(error.value)


@pytest.mark.asyncio
async def test_malformed_terminology_response_advances_to_same_provider_backup(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "a-first", "synthetic-first")
        await add_model(db, path, "openai", "b-backup", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    class LLM:
        async def generate_text(self, prompt, *, route_target, api_key):
            calls.append(route_target.remote_model_id)
            return "provider broken output secret" if route_target.remote_model_id == "a-first" else term_response()

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: LLM()})(), raising=False)
    result = await terms.llm_extract_terms("Alice sentence", sessions=sessions, data_dir=path)
    assert result[0]["source_term"] == "Alice"
    assert calls == ["a-first", "b-backup"]


@pytest.mark.asyncio
async def test_terminology_prompt_respects_each_target_input_limit(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "first", "synthetic-first",
                                metadata={"max_input_tokens": 2700})
        await add_model(db, path, "gemini", "second", "synthetic-second",
                        metadata={"inputTokenLimit": 2500})
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    observed = []

    class LLM:
        async def generate_text(self, prompt, *, route_target, api_key):
            observed.append((route_target.remote_model_id, len(prompt.encode("utf-8"))))
            if route_target.remote_model_id == "first":
                error = RuntimeError("synthetic model unavailable")
                error.http_status = 404
                raise error
            return term_response()

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: LLM()})(), raising=False)
    await terms.llm_extract_terms("Alice " + "長文本" * 3000, sessions=sessions, data_dir=path)
    assert [name for name, _ in observed] == ["first", "second"]
    assert observed[0][1] <= 2700 - 512
    assert observed[1][1] <= 2500 - 512


@pytest.mark.asyncio
async def test_unified_forwards_catalog_session_to_terminology(monkeypatch):
    from app.workflow.stages import translate_stage as unified

    unified_sessions = object()
    monkeypatch.setattr(unified, "async_session_factory", unified_sessions)
    observed = []

    async def capture(db, project_id, segments, target_lang, *, sessions=None):
        observed.append((project_id, sessions))
        return 0

    monkeypatch.setattr(terms, "extract_and_persist_from_segments", capture)
    context = type("Context", (), {"project_id": "unified", "source_segments": [{"text": "Alice sentence"}],
                                    "raw_transcript": "", "target_language": "vi"})()
    await unified.TranslateStage()._extract_entities(context, object())
    assert observed == [("unified", unified_sessions)]


def test_invalid_terminology_logging_does_not_emit_source_text(monkeypatch):
    secret_source = "PRIVATE_TRANSCRIPT_SENTENCE_123"
    logged = []
    monkeypatch.setattr(terms.logger, "warning", lambda *args, **kwargs: logged.append((args, kwargs)))
    result = terms.validate_and_align_extracted_terms(
        [{"source_term": secret_source, "suggested_term": "private"}], "Unrelated transcript"
    )
    assert result == []
    assert secret_source not in str(logged)


@pytest.mark.parametrize("payload", [
    '{"terms":null}', '{"terms":{"source_term":"Alice"}}',
    '{"terms":[{"foo":"bar"}]}', '[1,2]', '{"terms":[null]}',
])
def test_strict_term_parser_rejects_structured_garbage(payload):
    with pytest.raises(terms.InvalidTerminologyOutput):
        terms._parse_llm_terms(payload, strict=True)
    assert terms._parse_llm_terms('{"terms":[]}', strict=True) == []


@pytest.mark.asyncio
async def test_tiny_backup_budget_does_not_veto_usable_default(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "a-default", "synthetic-default",
                                metadata={"max_input_tokens": 8000})
        await add_model(db, path, "gemini", "b-tiny", "synthetic-tiny",
                        metadata={"inputTokenLimit": 600})
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="LLM",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    class LLM:
        async def generate_text(self, prompt, *, route_target, api_key):
            calls.append((route_target.remote_model_id, len(prompt.encode("utf-8"))))
            return term_response()

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {"get_llm": lambda _, p: LLM()})(), raising=False)
    result = await terms.llm_extract_terms("Alice sentence", sessions=sessions, data_dir=path)
    assert result[0]["source_term"] == "Alice"
    assert calls == [("a-default", calls[0][1])]
    assert calls[0][1] <= 6000


@pytest.mark.asyncio
async def test_legacy_terminology_error_log_never_includes_upstream_secret(monkeypatch):
    marker = "SYNTHETIC_SECRET_RESPONSE_MARKER"
    logged = []

    class LLM:
        async def generate_text(self, prompt, *, model=None):
            raise RuntimeError(f"transport returned {marker}")

    monkeypatch.setattr(terms, "get_registry", lambda: type("Registry", (), {
        "get_llm": lambda _, p: LLM(), "_llm": {"gemini": LLM()},
    })())
    monkeypatch.setattr(terms.logger, "warning", lambda *args, **kwargs: logged.append((args, kwargs)))
    assert await terms.llm_extract_terms("Alice sentence") == []
    assert logged and marker not in str(logged)
