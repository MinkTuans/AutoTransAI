"""Canonical routing uses synthetic keys and an isolated SQLite catalog."""
import asyncio
from dataclasses import FrozenInstanceError, asdict

import pytest
from sqlalchemy import delete, event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.credential_service import CredentialService


@pytest.fixture
async def routing_db(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'route.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all([Provider(id=p, name=p, provider_type="llm") for p in ("openai", "gemini", "edge_tts", "fal", "elevenlabs")])
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, provider, remote, *, caps=None, status="FULL_UNKNOWN", metadata=None):
    model = CatalogModel(provider_id=provider, remote_model_id=remote,
                         capabilities=caps or [], capability_status=status,
                         source="manual" if status != "FULL_UNKNOWN" else "discovered",
                         discovery_metadata=metadata)
    db.add(model)
    await db.flush()
    return model


async def add_key(db, path, provider, models, secret):
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    for model in models:
        db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return key


def test_capability_evidence_and_unknown():
    from app.services.capability_registry import classify, compatible
    gemini = classify("gemini", {"supportedGenerationMethods": ["generateContent"]})
    assert compatible("TRANSLATION", gemini)
    assert compatible("LLM", gemini)
    assert gemini.status == "PARTIAL"
    assert compatible("STT", gemini) and compatible("VISUAL_GENDER", gemini)
    speech = classify("elevenlabs", {"can_do_text_to_speech": True})
    assert compatible("TTS", speech) and compatible("STT", speech)
    negative = classify("elevenlabs", {"can_do_text_to_speech": False})
    assert not compatible("TTS", negative)
    assert compatible("STT", negative)
    visual_negative = classify("anthropic", {"capabilities": {"image_input": {"supported": False}}})
    assert not compatible("VISUAL_GENDER", visual_negative)
    assert compatible("TRANSLATION", visual_negative)
    unknown = classify("openai", {})
    assert unknown.status == "FULL_UNKNOWN"
    assert all(compatible(cap, unknown) for cap in (
        "STT", "TRANSLATION", "LLM", "TTS", "VIDEO_GENERATION", "IMAGE_GENERATION", "VISUAL_GENDER"))
    assert compatible("TTS", classify("edge_tts", {}))
    assert classify("openai", {}, remote_model_id="whisper-1").status == "FULL_UNKNOWN"


def test_legacy_compatibility_check_does_not_invent_stt():
    from app.services.model_resolver import _is_capability_compatible
    assert not _is_capability_compatible("STT", ["LLM"], "gemini")
    assert not _is_capability_compatible("STT", ["TRANSLATION"], "openai")
    assert _is_capability_compatible("STT", ["STT"], "gemini")
    assert _is_capability_compatible("TRANSLATION", ["LLM"], "anthropic")
    assert not _is_capability_compatible("LLM", ["TRANSLATION"], "anthropic")


def test_translation_only_catalog_annotation_does_not_imply_general_llm():
    from app.services.capability_registry import compatible, model_evidence
    model = CatalogModel(provider_id="gemini", remote_model_id="translation-only", source="manual",
                         capability_status="KNOWN", capabilities=["TRANSLATION"])
    evidence = model_evidence(model)
    assert compatible("TRANSLATION", evidence)
    assert not compatible("LLM", evidence)


def test_partial_curated_annotations_leave_omitted_capabilities_unknown():
    from app.services.capability_registry import compatible, model_evidence
    model = CatalogModel(provider_id="openai", remote_model_id="partial", source="manual",
                         capability_status="PARTIAL", capabilities=["TTS"])
    evidence = model_evidence(model)
    assert evidence.status == "PARTIAL"
    assert compatible("TTS", evidence)
    assert compatible("STT", evidence)
    assert "STT" not in evidence.incompatible
    model.capabilities = []
    assert model_evidence(model).status == "FULL_UNKNOWN"


@pytest.mark.asyncio
async def test_partial_curated_model_remains_routable_for_unknown_function(routing_db):
    from app.services.ai_routing import build_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "partial", caps=["TTS"], status="PARTIAL")
        await add_key(db, path, "openai", [model], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "STT")
    assert route.targets[0].model_id == model.id


def test_catalog_capability_summary_computes_from_persisted_evidence():
    from app.services.capability_registry import catalog_capability_summary
    model = CatalogModel(provider_id="gemini", remote_model_id="opaque", source="discovered",
                         capabilities=[], capability_status="FULL_UNKNOWN",
                         discovery_metadata={"supportedGenerationMethods": ["generateContent"]})
    summary = catalog_capability_summary(model)
    assert summary["status"] == "PARTIAL"
    assert summary["capabilities"] == ["LLM", "TRANSLATION"]
    assert "STT" in summary["unknown_capabilities"]
    assert summary["incompatible_capabilities"] == []
    assert "discovery_metadata" not in summary
    model.capability_status = "KNOWN"
    assert catalog_capability_summary(model) == summary


@pytest.mark.asyncio
async def test_llm_route_uses_translation_default_without_implying_stt(routing_db):
    from app.services.ai_routing import build_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "gemini", "text", caps=["LLM"], status="KNOWN")
        await add_key(db, path, "gemini", [model], "synthetic-private")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="gemini", model_id=model.id))
    async with sessions() as db:
        assert (await build_route(db, "LLM")).targets[0].model_id == model.id
        with pytest.raises(Exception):
            await build_route(db, "STT")


@pytest.mark.asyncio
async def test_provider_collision_and_deterministic_chain(routing_db):
    from app.services.ai_routing import build_route, RouteConfigurationError
    sessions, path = routing_db
    async with sessions.begin() as db:
        selected = await add_model(db, "openai", "shared", caps=["STT"], status="KNOWN")
        same_provider = await add_model(db, "openai", "next", caps=["STT"], status="KNOWN")
        other = await add_model(db, "gemini", "shared", caps=["STT"], status="KNOWN")
        first = await add_key(db, path, "openai", [selected, same_provider], "synthetic-first")
        second = await add_key(db, path, "openai", [selected], "synthetic-second")
        third = await add_key(db, path, "gemini", [other], "synthetic-third")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=selected.id))
    async with sessions() as db:
        route = await build_route(db, "STT")
    key_ids = sorted((first.id, second.id))
    assert [(t.provider_id, t.model_id, t.key_id) for t in route.targets] == [
        ("openai", selected.id, key_ids[0]), ("openai", selected.id, key_ids[1]),
        ("openai", same_provider.id, first.id), ("gemini", other.id, third.id)]
    assert route.targets[0].remote_model_id == "shared"
    with pytest.raises(FrozenInstanceError):
        route.targets[0].provider_id = "gemini"
    assert "synthetic-" not in repr(route) + str(asdict(route))
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "stt")).primary_provider_id = "gemini"
    async with sessions() as db:
        with pytest.raises(RouteConfigurationError):
            await build_route(db, "STT")


@pytest.mark.asyncio
async def test_default_sentinel_prefers_configured_provider(routing_db):
    from app.services.ai_routing import build_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        preferred = await add_model(db, "openai", "speech", caps=["STT"], status="KNOWN")
        other = await add_model(db, "gemini", "speech", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [preferred], "synthetic-openai")
        await add_key(db, path, "gemini", [other], "synthetic-gemini")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="default"))
    async with sessions() as db:
        route = await build_route(db, "STT")
        config = await db.get(AIFunctionConfig, "stt")
    assert [target.provider_id for target in route.targets] == ["openai", "gemini"]
    assert route.configured_model_id is None
    assert config.model_id == "default"


@pytest.mark.asyncio
async def test_default_sentinel_without_accessible_configured_provider_is_error(routing_db):
    from app.services.ai_routing import build_route, RouteConfigurationError
    sessions, path = routing_db
    async with sessions.begin() as db:
        other = await add_model(db, "gemini", "speech", caps=["STT"], status="KNOWN")
        await add_key(db, path, "gemini", [other], "synthetic-gemini")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="default"))
    async with sessions() as db:
        with pytest.raises(RouteConfigurationError, match="configured provider"):
            await build_route(db, "STT")


@pytest.mark.asyncio
async def test_public_listing_is_not_key_access_and_edge_is_keyless(routing_db):
    from app.services.ai_routing import build_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        public = await add_model(db, "openai", "public", caps=["TTS"], status="KNOWN")
        edge = await add_model(db, "edge_tts", "edge", caps=["TTS"], status="KNOWN")
        await add_key(db, path, "openai", [], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "TTS")
    assert [(t.provider_id, t.key_id) for t in route.targets] == [("edge_tts", None)]


@pytest.mark.asyncio
async def test_explicitly_incompatible_default_is_visible(routing_db):
    from app.services.ai_routing import build_route, RouteConfigurationError
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "tts-only", caps=["TTS"], status="KNOWN")
        await add_key(db, path, "openai", [model], "synthetic-private")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=model.id))
    async with sessions() as db:
        with pytest.raises(RouteConfigurationError, match="incompatible"):
            await build_route(db, "STT")


@pytest.mark.asyncio
async def test_retry_classification_fallback_and_secret_is_internal(routing_db):
    from app.services.ai_routing import build_route, invoke_route, RouteExhausted
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "openai", "one", caps=["STT"], status="KNOWN")
        second = await add_model(db, "openai", "two", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [first, second], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "STT")
        calls = []
        async def transport(target, secret):
            calls.append((target.remote_model_id, secret))
            if target.remote_model_id == "one":
                raise RuntimeError("auth synthetic-private")
            return "ok"
    assert await invoke_route(route, transport, sessions, path, max_attempts=2, timeout=0.1) == "ok"
    assert [c[0] for c in calls] == ["one", "two"]
    async def fail(target, secret):
        raise RuntimeError("quota synthetic-private")
    with pytest.raises(RouteExhausted) as exc:
        await invoke_route(route, fail, sessions, path, max_attempts=2, timeout=0.1)
    assert "synthetic-private" not in str(exc.value)


@pytest.mark.asyncio
async def test_accepted_async_job_pending_does_not_retry_or_fallback(routing_db):
    from app.services.ai_routing import RoutePending, build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "fal", "fal-ai/one", caps=["IMAGE_GENERATION"], status="KNOWN")
        second = await add_model(db, "fal", "fal-ai/two", caps=["IMAGE_GENERATION"], status="KNOWN")
        await add_key(db, path, "fal", [first, second], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "IMAGE_GENERATION")
    calls = []

    async def transport(target, secret):
        calls.append(target.remote_model_id)
        raise RoutePending("Image generation pending")

    with pytest.raises(RoutePending):
        await invoke_route(route, transport, sessions, path, max_attempts=2)
    assert calls == ["fal-ai/one"]


@pytest.mark.asyncio
async def test_canceled_submitted_job_is_terminal_pending(routing_db):
    from app.services.ai_routing import RoutePending, build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "fal", "fal-ai/one", caps=["IMAGE_GENERATION"], status="KNOWN")
        second = await add_model(db, "fal", "fal-ai/two", caps=["IMAGE_GENERATION"], status="KNOWN")
        await add_key(db, path, "fal", [first, second], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "IMAGE_GENERATION")
    calls = []

    async def transport(target, secret):
        calls.append(target.remote_model_id)
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            raise RoutePending("Image generation pending") from None

    with pytest.raises(RoutePending):
        await invoke_route(route, transport, sessions, path, timeout=0.01, max_attempts=2)
    assert calls == ["fal-ai/one"]


@pytest.mark.asyncio
async def test_concurrent_routes_do_not_mutate_targets(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "shared", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [model], "synthetic-secret")
    async with sessions() as db:
        route = await build_route(db, "STT")
        async def transport(target, secret):
            await asyncio.sleep(0)
            return (target.model_id, secret)
    results = await asyncio.gather(*(invoke_route(route, transport, sessions, path) for _ in range(2)))
    assert results == [(model.id, "synthetic-secret")] * 2


@pytest.mark.asyncio
async def test_public_catalog_model_uses_provider_key_without_claiming_entitlement(routing_db):
    from app.services.ai_routing import build_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "fal", "public-image", metadata={"category": "image"})
        key = await add_key(db, path, "fal", [], "synthetic-fal")
    async with sessions() as db:
        route = await build_route(db, "IMAGE_GENERATION")
    assert [(t.model_id, t.key_id, t.access_scope) for t in route.targets] == [
        (model.id, key.id, "catalog_unverified")]


@pytest.mark.asyncio
async def test_full_unknown_is_selectable_but_unsupported_adapter_moves_on(routing_db):
    from app.services.ai_routing import build_route, invoke_route, UnsupportedModalityError
    sessions, path = routing_db
    async with sessions.begin() as db:
        unknown = await add_model(db, "openai", "opaque")
        known = await add_model(db, "gemini", "vision", caps=["VISUAL_GENDER"], status="KNOWN")
        await add_key(db, path, "openai", [unknown], "synthetic-openai")
        await add_key(db, path, "gemini", [known], "synthetic-gemini")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual gender", capability="VISUAL_GENDER",
                                primary_provider_id="openai", model_id=unknown.id))
    async with sessions() as db:
        route = await build_route(db, "VISUAL_GENDER")
        assert route.targets[0].model_id == unknown.id
        seen = []
        async def transport(target, secret):
            seen.append(target.model_id)
            if target.model_id == unknown.id:
                raise UnsupportedModalityError("adapter unavailable")
            return "ok"
    assert await invoke_route(route, transport, sessions, path) == "ok"
    assert unknown.id in seen and known.id in seen


@pytest.mark.asyncio
async def test_configuration_error_is_visible_without_echoing_stored_text(routing_db):
    from app.services.ai_routing import build_route, RouteConfigurationError
    sessions, _ = routing_db
    async with sessions.begin() as db:
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="missing",
                                configuration_error="synthetic-private"))
    async with sessions() as db:
        with pytest.raises(RouteConfigurationError) as exc:
            await build_route(db, "STT")
    assert "needs review" in str(exc.value)
    assert "synthetic-private" not in str(exc.value)


@pytest.mark.asyncio
async def test_rate_retry_is_bounded_then_moves_to_next_model(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "openai", "one", caps=["STT"], status="KNOWN")
        second = await add_model(db, "openai", "two", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [first, second], "synthetic-private")
    calls, waits = [], []
    async def transport(target, secret):
        calls.append(target.remote_model_id)
        if target.remote_model_id == "one":
            error = RuntimeError("synthetic-private")
            error.status_code = 429
            raise error
        return "ok"
    async def sleep(delay):
        waits.append(delay)
    async with sessions() as db:
        route = await build_route(db, "STT")
    assert await invoke_route(route, transport, sessions, path, max_attempts=2, sleep=sleep) == "ok"
    assert calls == ["one", "one", "two"]
    assert waits == [0.25]


@pytest.mark.asyncio
async def test_preferred_key_hook_and_auth_falls_through_all_keys(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "one", caps=["STT"], status="KNOWN")
        first = await add_key(db, path, "openai", [model], "synthetic-first")
        second = await add_key(db, path, "openai", [model], "synthetic-second")
    async with sessions() as db:
        route = await build_route(db, "STT", preferred_key_ids=(second.id,))
        seen = []
        async def transport(target, secret):
            seen.append(target.key_id)
            if target.key_id == second.id:
                error = RuntimeError("secret hidden")
                error.status_code = 401
                raise error
            return "ok"
    assert await invoke_route(route, transport, sessions, path) == "ok"
    assert seen == [second.id, first.id]


@pytest.mark.asyncio
async def test_credential_session_closes_before_transport_and_stale_edge_is_skipped(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "speech", caps=["TTS"], status="KNOWN")
        edge = await add_model(db, "edge_tts", "edge", caps=["TTS"], status="KNOWN")
        await add_key(db, path, "openai", [model], "synthetic-private")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="openai", model_id=model.id))
    async with sessions() as db:
        route = await build_route(db, "TTS")
    seen = []
    async def transport(target, secret):
        assert sessions.kw["bind"].pool.checkedout() == 0
        seen.append(target.provider_id)
        return target.provider_id
    assert await invoke_route(route, transport, sessions, path) == "openai"
    async with sessions.begin() as db:
        await db.execute(delete(KeyModelAccess).where(KeyModelAccess.model_id == model.id))
    assert await invoke_route(route, transport, sessions, path) == "edge_tts"
    assert seen == ["openai", "edge_tts"]


@pytest.mark.asyncio
async def test_disabled_key_is_rechecked_before_reveal(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "speech", caps=["TTS"], status="KNOWN")
        await add_model(db, "edge_tts", "edge", caps=["TTS"], status="KNOWN")
        key = await add_key(db, path, "openai", [model], "synthetic-private")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="openai", model_id=model.id))
    async with sessions() as db:
        route = await build_route(db, "TTS")
    async with sessions.begin() as db:
        await (await CredentialService.open(db, path)).set_enabled(key.id, False)
    seen = []
    async def transport(target, secret):
        seen.append(target.provider_id)
        return target.provider_id
    assert await invoke_route(route, transport, sessions, path) == "edge_tts"
    assert seen == ["edge_tts"]


@pytest.mark.asyncio
async def test_disabled_provider_is_rechecked_before_transport(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        model = await add_model(db, "openai", "speech", caps=["TTS"], status="KNOWN")
        await add_model(db, "edge_tts", "edge", caps=["TTS"], status="KNOWN")
        await add_key(db, path, "openai", [model], "synthetic-private")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="openai", model_id=model.id))
    async with sessions() as db:
        route = await build_route(db, "TTS")
    async with sessions.begin() as db:
        (await db.get(Provider, "openai")).enabled = False
    seen = []
    async def transport(target, secret):
        seen.append(target.provider_id)
        return target.provider_id
    assert await invoke_route(route, transport, sessions, path) == "edge_tts"
    assert seen == ["edge_tts"]


@pytest.mark.asyncio
async def test_injected_timeout_budget_advances_to_next_target(routing_db):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "openai", "one", caps=["STT"], status="KNOWN")
        second = await add_model(db, "openai", "two", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [first, second], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "STT")
    waits = []
    async def timeout_hook(awaitable, seconds):
        if len(waits) < 2:
            awaitable.close()
            waits.append(seconds)
            raise asyncio.TimeoutError
        return await awaitable
    async def transport(target, secret):
        return target.remote_model_id
    async def no_sleep(delay):
        pass
    result = await invoke_route(route, transport, sessions, path, timeout=0.5,
                                wait_for=timeout_hook, sleep=no_sleep)
    assert result == "two" and waits == [0.5, 0.5]


@pytest.mark.asyncio
@pytest.mark.parametrize("status,code,attempts", [
    (401, "invalid_api_key", 1), (429, "insufficient_quota", 1),
    (404, "not_found", 1), (400, "unsupported_modality", 1),
    (503, "server_error", 2),
])
async def test_failure_budget_moves_to_next_model(routing_db, status, code, attempts):
    from app.services.ai_routing import build_route, invoke_route
    sessions, path = routing_db
    async with sessions.begin() as db:
        first = await add_model(db, "openai", "one", caps=["STT"], status="KNOWN")
        second = await add_model(db, "openai", "two", caps=["STT"], status="KNOWN")
        await add_key(db, path, "openai", [first, second], "synthetic-private")
    async with sessions() as db:
        route = await build_route(db, "STT")
    calls = []
    async def transport(target, secret):
        calls.append(target.remote_model_id)
        if target.remote_model_id == "one":
            error = RuntimeError("synthetic-private")
            error.status_code = status
            error.code = code
            raise error
        return "ok"
    async def no_sleep(delay):
        pass
    assert await invoke_route(route, transport, sessions, path, sleep=no_sleep) == "ok"
    assert calls == ["one"] * attempts + ["two"]


@pytest.mark.parametrize("code,status,expected", [
    ("invalid_api_key", 401, "auth"), ("insufficient_quota", 429, "quota"),
    ("rate_limit", 429, "rate_limit"), ("not_found", 404, "model_unavailable"),
    ("unsupported_modality", 400, "capability_mismatch"),
    ("server_error", 503, "provider_unavailable"),
])
def test_failure_classes_use_safe_codes(code, status, expected):
    from app.services.ai_routing import classify_failure
    error = RuntimeError("synthetic-secret")
    error.code = code
    error.status_code = status
    assert classify_failure(error) == expected


def test_http_response_failure_uses_status_without_echoing_response_body():
    from app.services.ai_routing import classify_failure
    class Response:
        status_code = 401
        text = "synthetic-private"
    error = RuntimeError("synthetic-private")
    error.response = Response()
    assert classify_failure(error) == "auth"
