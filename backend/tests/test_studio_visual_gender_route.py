"""Studio visual routing with synthetic credentials, images, and HTTP responses."""

import asyncio
from pathlib import Path

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import OperationalError

from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.services.ai_routing import RouteConfigurationError, RouteExhausted
from app.services.credential_service import CredentialService
from app.services.video_translator import visual_gender_service as service
from app.providers.vision.gemini_vision import GeminiVisionProvider
from app.providers.vision.openai_vision import OpenAIVisionProvider
from app.services.ai_routing import RouteTarget


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'vision.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("gemini", "openai", "anthropic", "edge_tts"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, provider, remote, secret, *, capabilities=("VISUAL_GENDER",)):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=list(capabilities))
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def fake_frames(monkeypatch, tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"synthetic video")

    async def extract(_video, _timestamp, output):
        Path(output).write_bytes(b"synthetic jpeg")

    async def sheet(_frames, output):
        output.write_bytes(b"synthetic jpeg")
        return output

    monkeypatch.setattr(service, "extract_speaker_keyframe", extract)
    monkeypatch.setattr(service, "create_contact_sheet", sheet)
    return str(video), [{"speaker_id": "S1", "start_time": 0, "end_time": 1}]


@pytest.mark.asyncio
async def test_exact_model_and_request_key_are_used_without_url_secret(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "gemini", "gemini-custom-vision", "vision-secret")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id=chosen.id))
    video, segments = fake_frames(monkeypatch, tmp_path)
    seen = []

    async def post(_client, url, **kwargs):
        seen.append((url, kwargs))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "FEMALE"}]}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    result = await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path)
    assert result == {"S1": "female"}
    assert len(seen) == 1
    assert "/models/gemini-custom-vision:generateContent" in seen[0][0]
    assert "vision-secret" not in seen[0][0]
    assert seen[0][1]["headers"]["x-goog-api-key"] == "vision-secret"
    assert not (path / "visual_gender_debug.txt").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [401, 429])
async def test_failed_default_advances_to_same_provider_then_cross_provider(catalog, monkeypatch, tmp_path, status):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "gemini", "a-primary", "key-one")
        await add_model(db, path, "gemini", "b-backup", "key-two")
        await add_model(db, path, "openai", "c-final", "key-three")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id=chosen.id, fallback_enabled=False))
    video, segments = fake_frames(monkeypatch, tmp_path)
    calls = []

    async def post(_client, url, **kwargs):
        model = kwargs.get("json", {}).get("model") or url.split("/models/")[-1].split(":")[0]
        calls.append(model)
        if model in ("a-primary", "b-backup"):
            return httpx.Response(status, text="provider echoed key-one key-two")
        return httpx.Response(200, json={"choices": [{"message": {"content": "MALE"}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "male"}
    assert calls == ["a-primary", "b-backup", "c-final"]


@pytest.mark.asyncio
async def test_incompatible_backup_is_skipped(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "gemini", "a-primary", "key-one")
        await add_model(db, path, "gemini", "b-text-only", "key-two", capabilities=("TRANSLATION",))
        await add_model(db, path, "openai", "c-vision", "key-three")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id=chosen.id))
    video, segments = fake_frames(monkeypatch, tmp_path)
    calls = []

    async def post(_client, url, **kwargs):
        model = kwargs.get("json", {}).get("model") or url.split("/models/")[-1].split(":")[0]
        calls.append(model)
        return (httpx.Response(401, text="denied") if model == "a-primary" else
                httpx.Response(200, json={"choices": [{"message": {"content": "MALE"}}]}))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "male"}
    assert calls == ["a-primary", "c-vision"]


@pytest.mark.asyncio
async def test_active_catalog_without_default_does_not_use_env(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "gemini", "a-primary", "key-one")
    video, segments = fake_frames(monkeypatch, tmp_path)
    monkeypatch.setattr(service.settings, "GEMINI_API_KEY", "legacy-key")
    with pytest.raises(RouteConfigurationError, match="default"):
        await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path)


@pytest.mark.asyncio
@pytest.mark.parametrize("catalog_shape", ["anthropic_discovered", "anthropic_system"])
async def test_non_gemini_catalog_never_escapes_to_legacy(catalog, monkeypatch, tmp_path, catalog_shape):
    sessions, path = catalog
    async with sessions.begin() as db:
        if catalog_shape == "anthropic_discovered":
            model = CatalogModel(provider_id="anthropic", remote_model_id="claude-vision",
                                 source="discovered", capability_status="FULL_UNKNOWN", capabilities=[])
        else:
            model = CatalogModel(provider_id="anthropic", remote_model_id="claude-system",
                                 source="system", capability_status="FULL_UNKNOWN", capabilities=[])
        db.add(model)
        await db.flush()
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="anthropic", model_id=model.id))
    video, segments = fake_frames(monkeypatch, tmp_path)
    monkeypatch.setattr(service.settings, "GEMINI_API_KEY", "legacy-secret")
    calls = []

    async def legacy(*args, **kwargs):
        calls.append(kwargs)
        return "male"

    monkeypatch.setattr(service, "detect_gender_from_image", legacy)
    with pytest.raises(RouteConfigurationError, match="credential access"):
        await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path)
    assert calls == []


@pytest.mark.asyncio
async def test_unrelated_key_only_keeps_legacy_migration_hold(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        await (await CredentialService.open(db, path)).create("anthropic", "anthropic-secret")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id="gemini-2.0-flash"))
    video, segments = fake_frames(monkeypatch, tmp_path)
    calls = []

    async def legacy(*args, **kwargs):
        calls.append(kwargs)
        return "male"

    monkeypatch.setattr(service, "detect_gender_from_image", legacy)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "male"}
    assert calls[0]["provider"] == "gemini"


@pytest.mark.asyncio
async def test_anthropic_catalog_default_with_access_fails_as_unsupported_not_gemini(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "anthropic", "claude-vision", "anthropic-secret")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="anthropic", model_id=selected.id))
    video, segments = fake_frames(monkeypatch, tmp_path)
    monkeypatch.setattr(service.settings, "GEMINI_API_KEY", "legacy-secret")
    calls = []

    async def post(_client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, text="should not call")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(RouteExhausted, match="capability_mismatch"):
        await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path)
    assert calls == []


@pytest.mark.asyncio
async def test_keyless_edge_only_catalog_keeps_uninitialized_legacy_path(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        db.add(CatalogModel(provider_id="edge_tts", remote_model_id="edge-tts", source="system",
                            capability_status="KNOWN", capabilities=["TTS"]))
    video, segments = fake_frames(monkeypatch, tmp_path)
    calls = []

    async def legacy(*args, **kwargs):
        calls.append(kwargs)
        return "male"

    monkeypatch.setattr(service, "detect_gender_from_image", legacy)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "male"}
    assert calls[0]["provider"] == "gemini"


@pytest.mark.asyncio
async def test_all_targets_fail_without_secret_in_error_or_log(catalog, monkeypatch, tmp_path, caplog):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "gemini", "a-primary", "key-one")
        await add_model(db, path, "openai", "b-backup", "key-two")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id=chosen.id))
    video, segments = fake_frames(monkeypatch, tmp_path)

    async def post(_client, _url, **_kwargs):
        return httpx.Response(401, text="provider echoed key-one and key-two")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(RouteExhausted) as caught:
        await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path)
    assert "key-one" not in str(caught.value) + caplog.text
    assert "key-two" not in str(caught.value) + caplog.text
    assert not (path / "visual_gender_debug.txt").exists()


@pytest.mark.asyncio
async def test_timeout_advances_to_compatible_backup(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "gemini", "a-primary", "key-one")
        await add_model(db, path, "openai", "b-backup", "key-two")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="gemini", model_id=chosen.id))
    video, segments = fake_frames(monkeypatch, tmp_path)
    calls = []

    async def post(_client, url, **kwargs):
        calls.append(url)
        if "generativelanguage" in url:
            raise asyncio.TimeoutError()
        return httpx.Response(200, json={"choices": [{"message": {"content": "FEMALE"}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "female"}
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_concurrent_vision_calls_keep_request_keys_and_models_isolated(monkeypatch, tmp_path):
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"synthetic jpeg")
    requests = []

    async def post(_client, url, **kwargs):
        requests.append((url, kwargs))
        await asyncio.sleep(0)
        if "generativelanguage" in url:
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "MALE"}]}}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "FEMALE"}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    gemini = GeminiVisionProvider()
    openai = OpenAIVisionProvider()
    targets = [RouteTarget("g", "gemini", "gemini-job-a", "key-a", "VISUAL_GENDER"),
               RouteTarget("o", "openai", "openai-job-b", "key-b", "VISUAL_GENDER")]
    results = await asyncio.gather(
        gemini.analyze_image(image, "Classify", route_target=targets[0], api_key="secret-a"),
        openai.analyze_image(image, "Classify", route_target=targets[1], api_key="secret-b"),
    )
    assert results == ["MALE", "FEMALE"]
    google_call = next(item for item in requests if "generativelanguage" in item[0])
    openai_call = next(item for item in requests if "api.openai" in item[0])
    assert "gemini-job-a" in google_call[0] and "secret-a" not in google_call[0]
    assert google_call[1]["headers"]["x-goog-api-key"] == "secret-a"
    assert openai_call[1]["json"]["model"] == "openai-job-b"
    assert openai_call[1]["headers"]["Authorization"] == "Bearer secret-b"


@pytest.mark.asyncio
async def test_provider_failure_does_not_log_response_body_or_key(monkeypatch, tmp_path, caplog):
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"synthetic jpeg")

    async def post(_client, _url, **_kwargs):
        return httpx.Response(401, text="provider echoed super-secret media-derived text")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    providers = [(GeminiVisionProvider(), "gemini"), (OpenAIVisionProvider(), "openai")]
    for adapter, provider in providers:
        target = RouteTarget("m", provider, "exact-model", "k", "VISUAL_GENDER")
        with pytest.raises(RuntimeError) as caught:
            await adapter.analyze_image(image, "Classify", route_target=target, api_key="super-secret")
        assert getattr(caught.value, "status_code", None) == 401
        assert "super-secret" not in str(caught.value) + caplog.text
        assert "media-derived" not in str(caught.value) + caplog.text


@pytest.mark.asyncio
async def test_missing_canonical_schema_is_migration_error_not_env_fallback(monkeypatch, tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'unmigrated.db'}")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    video, segments = fake_frames(monkeypatch, tmp_path)
    monkeypatch.setattr(service.settings, "GEMINI_API_KEY", "legacy-secret")
    try:
        with pytest.raises(OperationalError):
            await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=tmp_path)
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_inconclusive_visual_result_remains_unknown(catalog, monkeypatch, tmp_path):
    sessions, path = catalog
    async with sessions.begin() as db:
        chosen = await add_model(db, path, "openai", "vision-unknown", "synthetic-key")
        db.add(AIFunctionConfig(function_id="visual_gender", function_name="Visual Gender", capability="VISUAL_GENDER",
                                primary_provider_id="openai", model_id=chosen.id))
    video, segments = fake_frames(monkeypatch, tmp_path)

    async def post(_client, _url, **_kwargs):
        return httpx.Response(200, json={"choices": [{"message": {"content": "I cannot determine"}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    assert await service.detect_speakers_gender(video, segments, sessions=sessions, data_dir=path) == {"S1": "unknown"}
