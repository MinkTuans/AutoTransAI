"""Studio translation routing against an isolated catalog and synthetic keys."""
import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi import BackgroundTasks
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig
from app.models.video_translator import VideoAsset, VideoTranslationJob
from app.services.ai_routing import RouteConfigurationError
from app.services.credential_service import CredentialService
from app.services.video_translator import translator_service as service


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, CatalogRefreshRun, KeyModelAccess, AIFunctionConfig):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="llm") for p in ("openai", "gemini"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, provider, remote, secret, *, capabilities=("TRANSLATION",), metadata=None):
    model = CatalogModel(provider_id=provider, remote_model_id=remote, source="manual",
                         capability_status="KNOWN", capabilities=list(capabilities), discovery_metadata=metadata or {})
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create(provider, secret)
    await db.flush()
    db.add(KeyModelAccess(key_id=key.id, model_id=model.id, provider_id=provider))
    return model


def response(lines):
    return json.dumps({"lines": [{"n": n, "text": text} for n, text in lines], "names": []})


def segments(count=1):
    return [{"number": i + 1, "text": f"Hello {i}"} for i in range(count)]


@pytest.mark.asyncio
async def test_configured_model_and_key_reach_http_request(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "custom-full-v9", "synthetic-openai")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def post(client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json={"choices": [{"message": {"content": response([(1, "Xin chào")])}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    result = await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào"
    assert len(calls) == 1
    assert calls[0][1]["json"]["model"] == "custom-full-v9"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer synthetic-openai"


@pytest.mark.asyncio
async def test_exact_model_key_and_cross_provider_fallback(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "custom-full-v9", "synthetic-openai")
        await add_model(db, path, "gemini", "backup-v2", "synthetic-gemini")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    async def generate(prompt, *, route_target, api_key, **kwargs):
        calls.append((route_target.provider_id, route_target.remote_model_id, api_key))
        if route_target.provider_id == "openai":
            error = RuntimeError("secret provider detail")
            error.http_status = 404
            raise error
        return response([(1, "Xin chào")])

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, **kwargs):
            return await generate(prompt, **kwargs)

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào"
    assert calls[:2] == [("openai", "custom-full-v9", "synthetic-openai"),
                         ("gemini", "backup-v2", "synthetic-gemini")]


@pytest.mark.asyncio
async def test_invalid_default_cannot_escape_to_legacy(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        await add_model(db, path, "openai", "available", "synthetic-key")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id="missing"))
    with pytest.raises(RouteConfigurationError):
        await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)


@pytest.mark.asyncio
async def test_concurrent_jobs_keep_model_and_key_local(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "first-v1", "synthetic-one")
        second = await add_model(db, path, "openai", "second-v2", "synthetic-two")
        config = AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                  primary_provider_id="openai", model_id=first.id)
        db.add(config)
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    class LLM:
        provider_id = "openai"
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            if route_target.remote_model_id == "first-v1":
                entered.set()
                await release.wait()
            return response([(1, "Xin chào")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    one = asyncio.create_task(service.translate_transcript_segments(segments(), "en", "vi", job_id="one", sessions=sessions, data_dir=path))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        async with sessions.begin() as db:
            config = await db.get(AIFunctionConfig, "translation")
            config.model_id = second.id
        two = asyncio.create_task(service.translate_transcript_segments(segments(), "en", "vi", job_id="two", sessions=sessions, data_dir=path))
        await asyncio.wait_for(two, 5)
    finally:
        release.set()
        await asyncio.wait_for(one, 5)
    assert calls == [("first-v1", "synthetic-one"), ("second-v2", "synthetic-two")]


@pytest.mark.asyncio
async def test_same_provider_before_cross_provider_and_incompatible_skipped(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "a-first", "synthetic-one")
        await add_model(db, path, "openai", "b-second", "synthetic-two")
        await add_model(db, path, "openai", "c-tts-only", "synthetic-tts", capabilities=("TTS",))
        await add_model(db, path, "gemini", "d-third", "synthetic-three")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append(route_target.remote_model_id)
            if route_target.remote_model_id in ("a-first", "b-second"):
                error = RuntimeError("unavailable")
                error.http_status = 404
                raise error
            return response([(1, "Xin chào")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào"
    assert calls == ["a-first", "b-second", "d-third"]


@pytest.mark.asyncio
async def test_all_target_errors_hide_secret_and_provider_text(catalog, monkeypatch, caplog):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "only-model", "synthetic-secret-123")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=first.id))

    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, **kwargs):
            calls.append(prompt)
            error = RuntimeError("synthetic-secret-123 raw provider body")
            error.http_status = 401
            raise error

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    with pytest.raises(RuntimeError) as exc:
        await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert "synthetic-secret-123" not in str(exc.value) + caplog.text
    assert "raw provider body" not in str(exc.value) + caplog.text
    assert len(calls) == 2  # initial call plus one bounded single-item recovery


@pytest.mark.asyncio
async def test_long_transcript_respects_smallest_fallback_context(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "large", "synthetic-one", metadata={"max_input_tokens": 8000})
        await add_model(db, path, "gemini", "small", "synthetic-two", metadata={"inputTokenLimit": 2600})
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, **kwargs):
            calls.append((route_target.remote_model_id, len(prompt.encode("utf-8"))))
            if route_target.remote_model_id == "large":
                error = RuntimeError("unavailable")
                error.http_status = 404
                raise error
            lines = json.loads(prompt.split("JSON gốc:\n")[-1])
            ids = [line["n"] for line in lines["lines"]]
            return response([(n, "Bản dịch") for n in ids])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(
        [{"number": i + 1, "text": "Hello world " * 8} for i in range(30)],
        "en", "vi", sessions=sessions, data_dir=path)
    assert len(result) == 30
    assert len(calls) > 2
    assert max(size for _, size in calls) <= 2088


@pytest.mark.asyncio
async def test_tiny_unicode_context_rejects_before_provider_call(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "gemini", "tiny", "synthetic-key", metadata={"inputTokenLimit": 600})
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="gemini", model_id=selected.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, **kwargs):
            calls.append(prompt)
            return response([(1, "Bản dịch")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    with pytest.raises(RuntimeError, match="context budget"):
        await service.translate_transcript_segments([{"number": 1, "text": "你好" * 100}],
                                                    "zh", "vi", sessions=sessions, data_dir=path)
    assert calls == []


@pytest.mark.asyncio
async def test_missing_id_recovery_and_echo_correction_use_same_route(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "openai", "exact-v7", "synthetic-key")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=first.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            if len(calls) == 1:
                return response([(1, "Xin chào"), (2, "Hello 1"), (3, "Bản dịch 2"), (4, "Bản dịch 3")])
            if len(calls) == 2:
                return response([(5, "Bản dịch 4")])
            return response([(2, "Bản dịch 1")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(5), "en", "vi", sessions=sessions, data_dir=path)
    assert [seg["translated_text"] for seg in result] == [
        "Xin chào", "Bản dịch 1", "Bản dịch 2", "Bản dịch 3", "Bản dịch 4"]
    assert calls == [("exact-v7", "synthetic-key")] * 3


@pytest.mark.asyncio
async def test_glossary_retry_uses_same_route(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "gemini", "glossary-v3", "synthetic-key")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="gemini", model_id=first.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            return response([(1, "Xin chào thế giới" if len(calls) == 2 else "Chào thế giới")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(
        [{"number": 1, "text": "Hello world"}], "en", "vi",
        glossary={"Hello": "Xin chào"}, sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào thế giới"
    assert calls == [("glossary-v3", "synthetic-key")] * 2


@pytest.mark.asyncio
async def test_full_unknown_model_can_translate(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "unknown-v1", "synthetic-key", capabilities=())
        selected.capability_status = "FULL_UNKNOWN"
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            assert (route_target.remote_model_id, api_key) == ("unknown-v1", "synthetic-key")
            return response([(1, "Xin chào")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào"


@pytest.mark.asyncio
async def test_subbatch_recovery_is_route_local_and_bounded(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "split-v1", "synthetic-key")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            return "not JSON" if len(calls) == 1 else response([(len(calls) - 1, f"Bản dịch {len(calls)}")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(2), "en", "vi", sessions=sessions, data_dir=path)
    assert [seg["translated_text"] for seg in result] == ["Bản dịch 2", "Bản dịch 3"]
    assert calls == [("split-v1", "synthetic-key")] * 3


@pytest.mark.asyncio
async def test_concurrent_legacy_jobs_keep_resolved_model_local(monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    class LLM:
        provider_id = "openai"
        provider_name = "test"
        async def generate_text(self, prompt, *, model=None, **kwargs):
            calls.append(model)
            if len(calls) == 1:
                entered.set()
                await release.wait()
                return "invalid JSON"
            return response([(1, "Xin chào")])

    llm = LLM()
    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: llm)
    one = asyncio.create_task(service.translate_transcript_segments(segments(), "en", "vi",
                                                                   translation_model_id="legacy-first"))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        two = asyncio.create_task(service.translate_transcript_segments(segments(), "en", "vi",
                                                                       translation_model_id="legacy-second"))
        await asyncio.wait_for(two, 5)
    finally:
        release.set()
        await asyncio.wait_for(one, 5)
    assert calls == ["legacy-first", "legacy-second", "legacy-first"]


@pytest.mark.asyncio
async def test_studio_background_entry_forwards_catalog_sessions_to_translation(monkeypatch, tmp_path):
    from app.api.routes import video_translator as studio
    from app.models import Project
    from app.services.video_translator import character_mapping_service, visual_gender_service
    from app.services import terminology_extractor

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'studio.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    asset_path = tmp_path / "source.mp4"
    asset_path.write_bytes(b"synthetic media")
    async with sessions.begin() as db:
        db.add(Project(id="project-one", title="Synthetic"))
        db.add(VideoAsset(id="asset-one", file_path=str(asset_path)))
        db.add(VideoTranslationJob(id="job-one", asset_id="asset-one", project_id="project-one",
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

    async def stt(audio, **kwargs):
        return ([{"number": 1, "text": "Hello", "speaker_id": "S1", "start_time": 0, "end_time": 1}], "en")

    mapping_kwargs = {}

    async def mapping(*args, **kwargs):
        mapping_kwargs.update(kwargs)
        return SimpleNamespace(by_speaker={"S1": {
            "character_id": "confirmed-id", "name": "User Confirmed Name",
            "role": "main", "gender": "female", "confidence": 0.95,
        }})

    captured = {}
    term_kwargs = {}
    visual_kwargs = {}

    async def visual(*args, **kwargs):
        visual_kwargs.update(kwargs)
        return {}

    async def translate(*args, **kwargs):
        captured.update(kwargs)
        captured["segments"] = args[0]
        raise RuntimeError("stop after translation boundary")

    async def extract_terms(*args, **kwargs):
        term_kwargs.update(kwargs)
        return 0

    monkeypatch.setattr(studio, "extract_audio_from_video", extract)
    monkeypatch.setattr(studio, "speech_to_text_and_detect_language", stt)
    monkeypatch.setattr(character_mapping_service, "map_and_persist", mapping)
    monkeypatch.setattr(visual_gender_service, "detect_speakers_gender", visual)
    monkeypatch.setattr(studio, "translate_transcript_segments", translate)
    monkeypatch.setattr(terminology_extractor, "extract_and_persist_from_segments", extract_terms)
    tasks = BackgroundTasks()
    try:
        async with sessions() as db:
            response = await studio.start_translation_pipeline("job-one", tasks, db)
        assert response["data"]["started"] is True
        await tasks()
        assert captured["job_id"] == "job-one"
        assert captured["sessions"] is sessions
        assert captured["segments"][0]["speaker_name"] == "User Confirmed Name"
        assert captured["segments"][0]["role"] == "main"
        assert mapping_kwargs["sessions"] is sessions
        assert visual_kwargs["sessions"] is sessions
        assert term_kwargs["sessions"] is sessions
    finally:
        await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_output", ["not JSON", response([]), response([(1, "Hello 0")])])
async def test_semantically_bad_default_advances_to_backup(catalog, monkeypatch, bad_output):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "a-default", "synthetic-primary")
        await add_model(db, path, "openai", "b-backup", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append((route_target.remote_model_id, api_key))
            return bad_output if route_target.remote_model_id == "a-default" else response([(1, "Xin chào")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào"
    expected = ([("a-default", "synthetic-primary"), ("b-backup", "synthetic-backup")]
                if bad_output == "not JSON" else
                [("a-default", "synthetic-primary"), ("a-default", "synthetic-primary"),
                 ("b-backup", "synthetic-backup")])
    assert calls == expected


@pytest.mark.asyncio
async def test_glossary_correction_advances_to_backup_after_bad_default(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "gemini", "a-default", "synthetic-primary")
        await add_model(db, path, "gemini", "b-backup", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="gemini", model_id=selected.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append(route_target.remote_model_id)
            text = "Chào thế giới" if route_target.remote_model_id == "a-default" else "Xin chào thế giới"
            return response([(1, text)])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(
        [{"number": 1, "text": "Hello world"}], "en", "vi",
        glossary={"Hello": "Xin chào"}, sessions=sessions, data_dir=path)
    assert result[0]["translated_text"] == "Xin chào thế giới"
    assert calls == ["a-default", "a-default", "b-backup"]


@pytest.mark.asyncio
async def test_malformed_model_output_cannot_leak_secret(catalog, monkeypatch, caplog):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "only", "synthetic-secret-123")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, **kwargs):
            return "synthetic-secret-123 invalid provider body"

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    with pytest.raises(RuntimeError) as exc:
        await service.translate_transcript_segments(segments(), "en", "vi", sessions=sessions, data_dir=path)
    assert "synthetic-secret-123" not in str(exc.value) + caplog.text
    assert "invalid provider body" not in str(exc.value) + caplog.text


@pytest.mark.asyncio
async def test_targeted_missing_id_recovery_uses_backup_after_default_repeats_partial(catalog, monkeypatch):
    sessions, path = catalog
    async with sessions.begin() as db:
        selected = await add_model(db, path, "openai", "a-default", "synthetic-primary")
        await add_model(db, path, "openai", "b-backup", "synthetic-backup")
        db.add(AIFunctionConfig(function_id="translation", function_name="Translation", capability="TRANSLATION",
                                primary_provider_id="openai", model_id=selected.id))
    calls = []

    class LLM:
        provider_name = "test"
        async def generate_text(self, prompt, *, route_target, api_key, **kwargs):
            calls.append(route_target.remote_model_id)
            if route_target.remote_model_id == "a-default":
                return response([(n, f"Bản dịch {n}") for n in range(1, 5)])
            return response([(5, "Bản dịch 5")])

    monkeypatch.setattr(service.get_registry(), "get_llm", lambda provider: LLM())
    result = await service.translate_transcript_segments(segments(5), "en", "vi", sessions=sessions, data_dir=path)
    assert [seg["translated_text"] for seg in result] == [f"Bản dịch {n}" for n in range(1, 6)]
    assert calls == ["a-default", "a-default", "b-backup"]
