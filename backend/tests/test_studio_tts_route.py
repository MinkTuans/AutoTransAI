"""Studio TTS route selection and synthesis use synthetic catalog state only."""
import asyncio
from pathlib import Path

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.providers.base import GenerationResult
from app.services.ai_routing import RouteConfigurationError, RouteExhausted, RoutePlan, RouteTarget
from app.services.credential_service import CredentialService
from app.services.video_translator.studio_tts_routing import (
    cache_identity, cache_matches, generate_segment_audio, select_segment_route,
)


@pytest.mark.asyncio
async def test_render_segment_uses_canonical_target_and_cache_identity(tmp_path, monkeypatch):
    """Drive the real Studio Phase 2 entry until scheduling, with synthetic data."""
    from unittest.mock import AsyncMock
    from app.database import Base
    from app.models.settings import AIFunctionConfig
    from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
    from app.models.workflow_engine import VoicePoolEntry
    from app.api.routes import video_translator as studio
    from app.services.video_translator import timeline_scheduler

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'studio.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(studio, "async_session_factory", sessions)
    monkeypatch.setattr(studio.settings, "STORAGE_ROOT", tmp_path / "storage")
    monkeypatch.setattr(studio.settings, "DATA_DIR", tmp_path / "data")
    events = []
    monkeypatch.setattr(studio, "log_job_event", lambda *args: events.append(args))
    monkeypatch.setattr(studio, "start_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "stop_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "probe_duration_async", AsyncMock(return_value=1.0))
    calls = []
    failure_code = None

    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target=None, api_key=None):
            calls.append((route_target.remote_model_id if route_target else None, api_key, voice_id))
            if failure_code:
                return GenerationResult(success=False, error_code=failure_code,
                                        error_message="provider echoed request-key-3")
            output_path.write_bytes(b"synthetic audio")
            return GenerationResult(success=True, file_path=output_path)

    monkeypatch.setattr(studio, "get_registry", lambda: Registry({"elevenlabs": Eleven()}))

    class StopAtSchedule(Exception):
        pass

    monkeypatch.setattr(timeline_scheduler, "schedule_segments", lambda *args, **kwargs: (_ for _ in ()).throw(StopAtSchedule()))
    async with sessions.begin() as db:
        db.add(Provider(id="elevenlabs", name="elevenlabs", provider_type="audio"))
        db.add(VideoAsset(id="asset", file_path=str(tmp_path / "source.mp4"), duration=2.0))
        db.add(VideoTranslationJob(id="job", asset_id="asset", target_language="vi",
                                   audio_provider_id="elevenlabs", voice_id="eleven-voice"))
        db.add(VideoTranslationSegment(job_id="job", segment_number=1, start_time=0.0, end_time=1.0,
                                       original_text="Hello", translated_text="Xin chào",
                                       voice_provider="elevenlabs", voice_id="eleven-voice"))
        db.add(VoicePoolEntry(id="voice", provider="elevenlabs", language="vi-VN",
                              gender="female", voice_id="eleven-voice", display_name="Voice"))
        model = await add_model(db, tmp_path / "data", "catalog-model-v3", "request-key")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="elevenlabs", model_id=model.model_id))
    try:
        await studio.execute_job_render_pipeline("job")
        assert calls == [("catalog-model-v3", "request-key", "eleven-voice")]
        sidecar = tmp_path / "storage" / "translator" / "jobs" / "job" / "tts" / "seg_001.meta.json"
        import json
        metadata = json.loads(sidecar.read_text())
        assert metadata == cache_identity(model, "eleven-voice", "Xin chào", model.model_id)
        await studio.execute_job_render_pipeline("job")
        assert calls == [("catalog-model-v3", "request-key", "eleven-voice")]
        async with sessions.begin() as db:
            replacement = await add_model(db, tmp_path / "data", "catalog-model-v4", "request-key-2")
            config = await db.get(AIFunctionConfig, "tts")
            config.model_id = replacement.model_id
        await studio.execute_job_render_pipeline("job")
        assert calls[-1][0] == "catalog-model-v4"
        assert calls[-1][1] in ("request-key", "request-key-2")
        assert calls[-1][2] == "eleven-voice"
        assert len(calls) == 2
        async with sessions.begin() as db:
            unavailable = await add_model(db, tmp_path / "data", "catalog-model-v5", "request-key-3")
            (await db.get(AIFunctionConfig, "tts")).model_id = unavailable.model_id
        failure_code = "HTTP_401"
        await studio.execute_job_render_pipeline("job")
        async with sessions() as db:
            failed_job = await db.get(VideoTranslationJob, "job")
            assert failed_job.status == "failed"
            assert "auth" in failed_job.error_message
            assert "request-key" not in failed_job.error_message
        assert not sidecar.exists()
        assert "request-key" not in str(events)
        prior_calls = len(calls)
        async with sessions.begin() as db:
            (await db.get(AIFunctionConfig, "tts")).model_id = ""
        await studio.execute_job_render_pipeline("job")
        assert len(calls) == prior_calls
        async with sessions() as db:
            assert "default" in (await db.get(VideoTranslationJob, "job")).error_message
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_schedule_conflict_retry_uses_same_route_boundary(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    from app.database import Base
    from app.models.settings import AIFunctionConfig
    from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
    from app.models.workflow_engine import VoicePoolEntry
    from app.api.routes import video_translator as studio
    from app.services.video_translator import timeline_scheduler

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'retry.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(studio, "async_session_factory", sessions)
    monkeypatch.setattr(studio.settings, "STORAGE_ROOT", tmp_path / "storage")
    monkeypatch.setattr(studio.settings, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(studio, "log_job_event", lambda *args: None)
    monkeypatch.setattr(studio, "start_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "stop_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "probe_duration_async", AsyncMock(return_value=1.0))
    calls = []

    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target=None, api_key=None):
            calls.append((route_target.remote_model_id if route_target else None, api_key, voice_id))
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)

    monkeypatch.setattr(studio, "get_registry", lambda: Registry({"elevenlabs": Eleven()}))
    schedule_calls = 0

    def schedule(*args, **kwargs):
        nonlocal schedule_calls
        schedule_calls += 1
        if schedule_calls == 1:
            return SimpleNamespace(requires_review=True, unresolved_conflicts=[{"segment_id": 2, "with": 1}],
                                   segments=[])
        raise RuntimeError("stop after retry")

    monkeypatch.setattr(timeline_scheduler, "schedule_segments", schedule)
    async with sessions.begin() as db:
        db.add(Provider(id="elevenlabs", name="elevenlabs", provider_type="audio"))
        db.add(VideoAsset(id="asset", file_path=str(tmp_path / "source.mp4"), duration=3.0))
        db.add(VideoTranslationJob(id="job", asset_id="asset", target_language="vi",
                                   audio_provider_id="elevenlabs", voice_id="voice-a"))
        db.add_all(VideoTranslationSegment(id=n, job_id="job", segment_number=n, start_time=0.0,
                                           end_time=1.0, original_text="Hello", translated_text=f"Xin chào {n}",
                                           voice_provider="elevenlabs", voice_id="voice-a") for n in (1, 2))
        db.add_all(VoicePoolEntry(id=f"voice-{n}", provider="elevenlabs", language="vi-VN",
                                  gender="female", voice_id=f"voice-{n}", display_name=f"Voice {n}")
                   for n in ("a", "b"))
        model = await add_model(db, tmp_path / "data", "catalog-model", "request-key")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="elevenlabs", model_id=model.model_id))
    try:
        await studio.execute_job_render_pipeline("job")
        assert len(calls) == 3
        assert calls[-1] == ("catalog-model", "request-key", "voice-b")
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_uninitialized_catalog_keeps_legacy_tts_call(tmp_path, monkeypatch):
    from unittest.mock import AsyncMock
    from app.database import Base
    from app.models.video_translator import VideoAsset, VideoTranslationJob, VideoTranslationSegment
    from app.api.routes import video_translator as studio
    from app.services.video_translator import timeline_scheduler

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'legacy.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(studio, "async_session_factory", sessions)
    monkeypatch.setattr(studio.settings, "STORAGE_ROOT", tmp_path / "storage")
    monkeypatch.setattr(studio, "log_job_event", lambda *args: None)
    monkeypatch.setattr(studio, "start_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "stop_job_heartbeat", lambda *args: None)
    monkeypatch.setattr(studio, "probe_duration_async", AsyncMock(return_value=1.0))
    calls = []

    class LegacyEdge:
        async def generate_audio(self, text, voice_id, output_path):
            calls.append((text, voice_id))
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)

    monkeypatch.setattr(studio, "get_registry", lambda: Registry({"edge_tts": LegacyEdge()}))
    monkeypatch.setattr(timeline_scheduler, "schedule_segments", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("stop")))
    async with sessions.begin() as db:
        db.add(VideoAsset(id="asset", file_path=str(tmp_path / "source.mp4"), duration=2.0))
        db.add(VideoTranslationJob(id="job", asset_id="asset", target_language="vi",
                                   audio_provider_id="edge_tts", voice_id="vi-VN-HoaiMyNeural"))
        db.add(VideoTranslationSegment(job_id="job", segment_number=1, start_time=0.0, end_time=1.0,
                                       original_text="Hello", translated_text="Xin chào",
                                       voice_provider="edge_tts", voice_id="vi-VN-HoaiMyNeural"))
    try:
        await studio.execute_job_render_pipeline("job")
        assert calls == [("Xin chào", "vi-VN-HoaiMyNeural")]
    finally:
        await engine.dispose()


def target(provider, remote, key_id=None, model_id=None):
    return RouteTarget(model_id or f"id-{remote}", provider, remote, key_id, "TTS",
                       "catalog_unverified" if provider == "elevenlabs" else "listing_unverified")


def plan(*targets):
    return RoutePlan("TTS", targets, targets[0].model_id if targets else None)


def segment(provider="edge_tts", voice="vi-VN-HoaiMyNeural", *, confirmed=False, gender="female"):
    return {"voice_provider": provider, "voice_id": voice, "translated_text": "Xin chào",
            "confirmed_by_user": confirmed, "gender": gender}


def voice(provider, voice_id, language="vi-VN", gender="female"):
    return {"provider": provider, "voice_id": voice_id, "language": language, "gender": gender}


@pytest.mark.parametrize("pool,expected", [
    ([voice("edge_tts", "vi-VN-HoaiMyNeural"), voice("elevenlabs", "eleven-voice")],
     [("elevenlabs", "eleven-voice"), ("edge_tts", "vi-VN-HoaiMyNeural")]),
    ([voice("edge_tts", "vi-VN-HoaiMyNeural"), voice("elevenlabs", "english", "en-US")],
     [("edge_tts", "vi-VN-HoaiMyNeural")]),
    ([voice("edge_tts", "vi-VN-HoaiMyNeural"), voice("elevenlabs", "male", gender="male")],
     [("edge_tts", "vi-VN-HoaiMyNeural")]),
])
def test_route_selects_only_provider_language_gender_compatible_voices(pool, expected):
    route = plan(target("elevenlabs", "model-a", "key-a"), target("edge_tts", "edge-tts"))
    selected, voices = select_segment_route(route, segment(), pool, "vi")
    assert [(t.provider_id, voices[t]) for t in selected.targets] == expected


def test_confirmed_mapping_never_changes_provider_or_voice():
    route = plan(target("elevenlabs", "model-a", "key-a"), target("edge_tts", "edge-tts"))
    pool = [voice("elevenlabs", "eleven-voice"), voice("edge_tts", "vi-VN-HoaiMyNeural")]
    selected, voices = select_segment_route(route, segment(confirmed=True), pool, "vi")
    assert [(t.provider_id, voices[t]) for t in selected.targets] == [("edge_tts", "vi-VN-HoaiMyNeural")]


def test_no_compatible_voice_is_visible_configuration_error():
    route = plan(target("elevenlabs", "model-a", "key-a"), target("edge_tts", "edge-tts"))
    with pytest.raises(RouteConfigurationError, match="voice"):
        select_segment_route(route, segment(confirmed=True), [voice("elevenlabs", "english", "en-US")], "vi")


def test_google_catalog_target_is_not_used_until_voice_discovery_bridge_exists():
    route = plan(target("google_cloud_tts", "vi-VN-Neural2-A", "key-google"),
                 target("edge_tts", "edge-tts"))
    selected, voices = select_segment_route(route, segment(), [
        voice("google_cloud_tts", "vi-VN-Neural2-A"), voice("edge_tts", "vi-VN-HoaiMyNeural")], "vi")
    assert [(t.provider_id, voices[t]) for t in selected.targets] == [("edge_tts", "vi-VN-HoaiMyNeural")]


def test_cache_identity_requires_provider_model_key_voice_and_text():
    first = target("elevenlabs", "model-a", "key-a")
    second = target("elevenlabs", "model-b", "key-b")
    metadata = cache_identity(first, "eleven-voice", "Xin chào", first.model_id)
    route = plan(first)
    assert cache_matches(metadata, route, {first: "eleven-voice"}, "Xin chào")
    assert not cache_matches(metadata, plan(second), {second: "eleven-voice"}, "Xin chào")
    for changed in (
        target("edge_tts", "model-a", "key-a", first.model_id),
        target("elevenlabs", "model-other", "key-a", first.model_id),
        target("elevenlabs", "model-a", "key-other", first.model_id),
    ):
        assert not cache_matches(metadata, plan(changed), {changed: "eleven-voice"}, "Xin chào")
    assert not cache_matches(metadata, route, {first: "other-voice"}, "Xin chào")
    assert not cache_matches(metadata, route, {first: "eleven-voice"}, "Changed")
    assert not cache_matches({"voice_id": "eleven-voice", "translated_text": "Xin chào"}, route,
                             {first: "eleven-voice"}, "Xin chào")


@pytest.fixture
async def catalog(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'tts.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        for model in (Provider, APIKey, CatalogModel, KeyModelAccess):
            await conn.run_sync(model.__table__.create)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=p, name=p, provider_type="audio") for p in ("elevenlabs", "edge_tts"))
    yield sessions, tmp_path
    await engine.dispose()


async def add_model(db, path, remote, secret):
    model = CatalogModel(provider_id="elevenlabs", remote_model_id=remote, source="discovered",
                         capability_status="KNOWN", capabilities=["TTS"])
    db.add(model)
    await db.flush()
    key = await (await CredentialService.open(db, path)).create("elevenlabs", secret)
    await db.flush()
    return target("elevenlabs", remote, key.id, model.id)


class Registry:
    def __init__(self, providers):
        self.providers = providers

    def get_audio(self, provider_id):
        return self.providers.get(provider_id)


@pytest.mark.asyncio
async def test_concurrent_jobs_keep_model_key_and_voice_local(catalog):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "model-a", "request-key-a")
        second = await add_model(db, path, "model-b", "request-key-b")
    calls = []

    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            await asyncio.sleep(0)
            calls.append((route_target.remote_model_id, api_key, voice_id))
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path, provider_id="elevenlabs")

    registry = Registry({"elevenlabs": Eleven()})
    results = await asyncio.gather(*(
        generate_segment_audio(plan(t), {t: v}, "words", path / f"{n}.wav", sessions, path, registry)
        for n, t, v in ((1, first, "voice-a"), (2, second, "voice-b"))
    ))
    assert sorted(calls) == [("model-a", "request-key-a", "voice-a"),
                             ("model-b", "request-key-b", "voice-b")]
    assert [result.voice_id for result in results] == ["voice-a", "voice-b"]


@pytest.mark.asyncio
@pytest.mark.parametrize("code,expected", [("HTTP_401", "auth"), ("HTTP_429", "rate_limit"),
                                            ("TTS_TIMEOUT", "timeout")])
async def test_failed_generation_result_is_classified_and_falls_back(catalog, code, expected):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "model-a", "request-key-a")
        second = await add_model(db, path, "model-b", "request-key-b")
    calls = []

    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key, voice_id))
            if route_target.remote_model_id == "model-a":
                return GenerationResult(success=False, error_code=code,
                                        error_message="provider echoed request-key-a")
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)

    result = await generate_segment_audio(plan(first, second), {first: "voice-a", second: "voice-b"},
                                          "words", path / "fallback.wav", sessions, path,
                                          Registry({"elevenlabs": Eleven()}))
    assert result.target == second
    assert calls == ([("model-a", "request-key-a", "voice-a"),
                      ("model-a", "request-key-a", "voice-a"),
                      ("model-b", "request-key-b", "voice-b")]
                     if code in ("HTTP_429", "TTS_TIMEOUT") else
                     [("model-a", "request-key-a", "voice-a"),
                      ("model-b", "request-key-b", "voice-b")])


@pytest.mark.asyncio
async def test_all_failed_results_return_redacted_route_error(catalog, caplog):
    sessions, path = catalog
    async with sessions.begin() as db:
        first = await add_model(db, path, "model-a", "request-key-a")

    class Eleven:
        async def generate_audio(self, *args, **kwargs):
            return GenerationResult(success=False, error_code="HTTP_401",
                                    error_message="provider echoed request-key-a")

    with pytest.raises(RouteExhausted, match="auth") as error:
        await generate_segment_audio(plan(first), {first: "voice-a"}, "words", path / "fail.wav",
                                     sessions, path, Registry({"elevenlabs": Eleven()}))
    assert "request-key-a" not in str(error.value) + caplog.text


@pytest.mark.asyncio
async def test_edge_target_forwards_no_key(catalog):
    sessions, path = catalog
    async with sessions.begin() as db:
        model = CatalogModel(provider_id="edge_tts", remote_model_id="edge-tts", source="system",
                             capability_status="KNOWN", capabilities=["TTS"])
        db.add(model)
        await db.flush()
        edge = target("edge_tts", "edge-tts", model_id=model.id)
    calls = []

    class Edge:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.provider_id, api_key, voice_id))
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)

    await generate_segment_audio(plan(edge), {edge: "vi-VN-HoaiMyNeural"}, "words", path / "edge.wav",
                                 sessions, path, Registry({"edge_tts": Edge()}))
    assert calls == [("edge_tts", None, "vi-VN-HoaiMyNeural")]
