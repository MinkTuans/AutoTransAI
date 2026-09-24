"""Studio STT routing with isolated catalog data and synthetic credentials."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import BackgroundTasks
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.models.video_translator import VideoAsset, VideoTranslationJob
from app.services.credential_service import CredentialService
from app.services.ai_routing import RouteConfigurationError, RouteExhausted, invoke_route as canonical_invoke_route
from app.services.video_translator import translator_service as service


@pytest.fixture
async def studio_catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("gemini", "openai", "edge_tts", "elevenlabs"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_target(db, path, provider, remote, secret, *, capabilities=("STT",)):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=list(capabilities))
    db.add(model)
    await db.flush()
    if secret:
        key = await (await CredentialService.open(db, path)).create(provider, secret)
        await db.flush()
        db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def mock_audio(monkeypatch, tmp_path):
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFF synthetic audio")
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=2.0))
    return audio


def response_for(url):
    if "generativelanguage" in url:
        return {"candidates": [{"content": {"parts": [{"text": '{"language":"English","segments":[{"start_time":0,"end_time":2,"text":"Hi"}]}'}]}}]}
    return {"language": "English", "segments": [{"start": 0, "end": 2, "text": "Hi"}]}


@pytest.mark.asyncio
async def test_studio_uses_configured_exact_model_key_with_false_legacy_fallback(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        chosen = await add_target(db, path, "openai", "speech-custom-v2", "request-openai")
        await add_target(db, path, "gemini", "gemini-backup", "request-gemini")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=chosen.id, fallback_enabled=False))
    audio = mock_audio(monkeypatch, tmp_path)
    calls = []

    async def post(client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json=response_for(url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "Hi"
    assert len(calls) == 1
    assert calls[0][1]["data"]["model"] == "speech-custom-v2"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer request-openai"


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [401, 404, 429])
async def test_studio_advances_from_failed_model_to_same_provider_then_other(studio_catalog, monkeypatch, tmp_path, status):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        first = await add_target(db, path, "openai", "a-first", "request-openai")
        await add_target(db, path, "openai", "b-second", "request-openai-2")
        await add_target(db, path, "gemini", "c-third", "request-gemini")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id, fallback_enabled=False))
    audio = mock_audio(monkeypatch, tmp_path)
    calls = []

    async def post(client, url, **kwargs):
        model = kwargs.get("data", {}).get("model") or url.split("/models/")[-1].split(":")[0]
        calls.append(model)
        return httpx.Response(status if model == "a-first" else 200, json=response_for(url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "Hi"
    assert calls == ["a-first", "b-second"]


@pytest.mark.asyncio
async def test_populated_invalid_default_never_uses_legacy(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        await add_target(db, path, "openai", "available", "request-key")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id="missing-default"))
    audio = mock_audio(monkeypatch, tmp_path)
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", AsyncMock())
    monkeypatch.setattr(service, "transcribe_audio_with_whisper", AsyncMock())
    with pytest.raises(RouteConfigurationError):
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    service.transcribe_audio_with_gemini.assert_not_awaited()
    service.transcribe_audio_with_whisper.assert_not_awaited()


@pytest.mark.asyncio
async def test_populated_catalog_without_stt_default_is_visible_error(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        await add_target(db, path, "openai", "available", "request-key")
    audio = mock_audio(monkeypatch, tmp_path)
    post = AsyncMock()
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(RouteConfigurationError, match="default"):
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    post.assert_not_awaited()


@pytest.mark.asyncio
async def test_studio_falls_back_to_other_provider_after_same_provider_models_fail(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        first = await add_target(db, path, "openai", "a-first", "request-one")
        await add_target(db, path, "openai", "b-second", "request-two")
        await add_target(db, path, "gemini", "c-third", "request-three")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id, fallback_enabled=False))
    audio = mock_audio(monkeypatch, tmp_path)
    calls = []

    async def post(client, url, **kwargs):
        model = kwargs.get("data", {}).get("model") or url.split("/models/")[-1].split(":")[0]
        calls.append(model)
        return httpx.Response(200 if model == "c-third" else 401, json=response_for(url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "Hi"
    assert calls == ["a-first", "b-second", "c-third"]


@pytest.mark.asyncio
async def test_all_studio_targets_fail_with_sanitized_error(studio_catalog, monkeypatch, tmp_path, caplog):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        first = await add_target(db, path, "openai", "a-first", "request-secret")
        await add_target(db, path, "gemini", "b-second", "other-secret")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id))
    audio = mock_audio(monkeypatch, tmp_path)

    async def post(client, url, **kwargs):
        return httpx.Response(401, text="provider echoed request-secret other-secret")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(RouteExhausted, match="AI route failed: auth, auth") as caught:
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert "request-secret" not in str(caught.value) + caplog.text
    assert "other-secret" not in str(caught.value) + caplog.text


@pytest.mark.asyncio
async def test_studio_rejects_tts_default_before_transport(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        wrong = await add_target(db, path, "openai", "tts-only", "request-key", capabilities=("TTS",))
        await add_target(db, path, "gemini", "speech", "request-two")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=wrong.id))
    audio = mock_audio(monkeypatch, tmp_path)
    post = AsyncMock()
    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(RouteConfigurationError, match="incompatible"):
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    post.assert_not_awaited()


@pytest.mark.asyncio
async def test_two_studio_jobs_keep_route_model_and_key_local(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        first = await add_target(db, path, "openai", "model-one", "key-one")
        second = await add_target(db, path, "openai", "model-two", "key-two")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=first.id))
    audio = mock_audio(monkeypatch, tmp_path)
    first_entered = asyncio.Event()
    resume_first = asyncio.Event()
    calls = []

    async def post(client, url, **kwargs):
        model = kwargs["data"]["model"]
        calls.append((model, kwargs["headers"]["Authorization"]))
        if model == "model-one":
            first_entered.set()
            await resume_first.wait()
        return httpx.Response(200, json=response_for(url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    job_one = asyncio.create_task(service.speech_to_text_and_detect_language(audio, job_id="one", sessions=sessions, data_dir=path))
    await asyncio.wait_for(first_entered.wait(), 5)
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "stt")).model_id = second.id
    job_two = asyncio.create_task(service.speech_to_text_and_detect_language(audio, job_id="two", sessions=sessions, data_dir=path))
    try:
        assert (await asyncio.wait_for(job_two, 5))[0][0]["text"] == "Hi"
    finally:
        resume_first.set()
    assert (await asyncio.wait_for(job_one, 5))[0][0]["text"] == "Hi"
    assert calls == [("model-one", "Bearer key-one"), ("model-two", "Bearer key-two")]


@pytest.mark.asyncio
async def test_empty_catalog_keeps_legacy_path(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    audio = mock_audio(monkeypatch, tmp_path)
    legacy = AsyncMock(return_value=([{"text": "legacy"}], "English"))
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(
        GEMINI_API_KEY="legacy-key", OPENAI_API_KEY="", DEFAULT_LLM_PROVIDER="gemini",
        ENABLE_OPENAI_FALLBACK=False,
    ))
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "legacy"


@pytest.mark.asyncio
async def test_edge_only_system_catalog_keeps_legacy_stt(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        db.add(CatalogModel(provider_id="edge_tts", remote_model_id="edge-tts", source="system",
                            capability_status="KNOWN", capabilities=["TTS"]))
    audio = mock_audio(monkeypatch, tmp_path)
    legacy = AsyncMock(return_value=([{"text": "legacy"}], "English"))
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(
        GEMINI_API_KEY="legacy-key", OPENAI_API_KEY="", DEFAULT_LLM_PROVIDER="gemini",
        ENABLE_OPENAI_FALLBACK=False,
    ))
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "legacy"


@pytest.mark.asyncio
async def test_other_keyless_system_catalog_keeps_legacy_stt(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        db.add(CatalogModel(provider_id="openai", remote_model_id="local-system-image", source="system",
                            capability_status="KNOWN", capabilities=["IMAGE_GENERATION"]))
    audio = mock_audio(monkeypatch, tmp_path)
    legacy = AsyncMock(return_value=([{"text": "legacy"}], "English"))
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(
        GEMINI_API_KEY="legacy-key", OPENAI_API_KEY="", DEFAULT_LLM_PROVIDER="gemini",
        ENABLE_OPENAI_FALLBACK=False,
    ))
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "legacy"


@pytest.mark.asyncio
async def test_unrelated_tts_catalog_and_key_keep_legacy_stt(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        await add_target(db, path, "elevenlabs", "voice-model", "tts-only-key", capabilities=("TTS",))
    audio = mock_audio(monkeypatch, tmp_path)
    legacy = AsyncMock(return_value=([{"text": "legacy"}], "English"))
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(
        GEMINI_API_KEY="legacy-key", OPENAI_API_KEY="", DEFAULT_LLM_PROVIDER="gemini",
        ENABLE_OPENAI_FALLBACK=False,
    ))
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "legacy"


@pytest.mark.asyncio
async def test_global_refresh_without_stt_state_keeps_legacy_stt(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        await add_target(db, path, "elevenlabs", "voice-model", "tts-only-key", capabilities=("TTS",))
        db.add(CatalogRefreshRun(mode="refresh", status="completed", summary={}))
    audio = mock_audio(monkeypatch, tmp_path)
    legacy = AsyncMock(return_value=([{"text": "legacy"}], "English"))
    monkeypatch.setattr(service, "transcribe_audio_with_gemini", legacy)
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(
        GEMINI_API_KEY="legacy-key", OPENAI_API_KEY="", DEFAULT_LLM_PROVIDER="gemini",
        ENABLE_OPENAI_FALLBACK=False,
    ))
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "legacy"


@pytest.mark.asyncio
async def test_studio_route_budget_allows_valid_call_past_thirty_seconds(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        selected = await add_target(db, path, "openai", "speech", "request-key")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=selected.id))
    audio = mock_audio(monkeypatch, tmp_path)
    calls = []

    async def post(client, url, **kwargs):
        calls.append(kwargs["data"]["model"])
        return httpx.Response(200, json=response_for(url))

    async def simulated_wait_for(operation, timeout):
        if timeout <= 31:
            operation.close()
            raise asyncio.TimeoutError()
        return await operation

    async def invoke_with_clock(route, transport, sessions, data_dir, **kwargs):
        return await canonical_invoke_route(route, transport, sessions, data_dir,
                                            wait_for=simulated_wait_for, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    monkeypatch.setattr(service, "invoke_route", invoke_with_clock)
    result = await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert result[0][0]["text"] == "Hi"
    assert calls == ["speech"]


@pytest.mark.asyncio
async def test_studio_route_budget_scales_with_chunks_and_has_cap(studio_catalog, monkeypatch, tmp_path):
    sessions, path = studio_catalog
    async with sessions.begin() as db:
        selected = await add_target(db, path, "openai", "speech", "request-key")
        db.add(AIFunctionConfig(function_id="stt", function_name="STT", capability="STT",
                                primary_provider_id="openai", model_id=selected.id))
    audio = mock_audio(monkeypatch, tmp_path)
    durations = iter((2.0, 181.0, 100000.0))
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(side_effect=lambda _: next(durations)))
    budgets = []

    async def record_budget(route, transport, sessions, data_dir, *, timeout):
        budgets.append(timeout)
        return ([{"text": "Hi"}], "English")

    monkeypatch.setattr(service, "invoke_route", record_budget)
    for _ in range(3):
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=path)
    assert budgets[0] > 180
    assert budgets[1] > budgets[0]
    assert budgets[2] == 21600.0


@pytest.mark.asyncio
async def test_missing_catalog_table_surfaces_migration_error(monkeypatch, tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'missing.db'}")
    sessions = async_sessionmaker(engine)
    audio = mock_audio(monkeypatch, tmp_path)
    with pytest.raises(OperationalError, match="no such table"):
        await service.speech_to_text_and_detect_language(audio, sessions=sessions, data_dir=tmp_path)
    await engine.dispose()


@pytest.mark.asyncio
async def test_studio_start_entry_passes_canonical_session_factory(monkeypatch, tmp_path):
    from app.api.routes import video_translator as studio

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'studio.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    asset_path = tmp_path / "source.mp4"
    asset_path.write_bytes(b"synthetic media")
    async with sessions.begin() as db:
        db.add(VideoAsset(id="asset-one", file_path=str(asset_path)))
        db.add(VideoTranslationJob(id="job-one", asset_id="asset-one",
                                   settings_snapshot_json='{"trim_filler_enabled": false, "copyright_check_enabled": false}'))
    monkeypatch.setattr(studio, "async_session_factory", sessions)
    monkeypatch.setattr(studio.settings, "STORAGE_ROOT", tmp_path)
    monkeypatch.setattr(studio, "log_job_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(studio, "start_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "stop_job_heartbeat", lambda *args: None)

    async def extract(video, audio, **kwargs):
        audio.parent.mkdir(parents=True, exist_ok=True)
        audio.write_bytes(b"RIFF synthetic audio")
        return 2.0

    monkeypatch.setattr(studio, "extract_audio_from_video", extract)
    captured = {}

    async def stt(audio, **kwargs):
        captured.update(kwargs)
        raise RuntimeError("stop after STT boundary")

    monkeypatch.setattr(studio, "speech_to_text_and_detect_language", stt)
    tasks = BackgroundTasks()
    async with sessions() as db:
        response = await studio.start_translation_pipeline("job-one", tasks, db)
    assert response["data"]["started"] is True
    await tasks()
    assert captured["job_id"] == "job-one"
    assert captured["sessions"] is sessions
    async with sessions() as db:
        assert (await db.get(VideoTranslationJob, "job-one")).status == "failed"
    await engine.dispose()
