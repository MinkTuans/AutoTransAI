"""Unified DUB uses request-local catalog TTS and resumable clip identity."""

import asyncio
import json
import socket
from pathlib import Path

import httpx
import pytest
from sqlalchemy import delete, event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import APIKey, CatalogModel, Provider
from app.models.project import Project
from app.models.settings import AIFunctionConfig
from app.models.workflow_engine import CharacterVoiceProfile, SpeakerVoiceMapping, VoicePoolEntry
from app.providers.base import GenerationResult, VoiceInfo
from app.services.credential_service import CredentialService
from app.services.ai_routing import RouteConfigurationError
from app.workflow.stages.dub_stage import DubStage
from app.workflow.workflow_context import WorkflowContext


@pytest.fixture(autouse=True)
def block_provider_network(monkeypatch):
    """A missed provider stub must fail the test, never issue a live request."""
    def blocked(*_args, **_kwargs):
        raise AssertionError("Outbound network is disabled for Unified DUB tests")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(httpx.AsyncClient, "send", blocked)
    monkeypatch.setattr(httpx.Client, "send", blocked)


@pytest.fixture
async def catalog(tmp_path, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'dub.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(dub_module, "async_session_factory", sessions, raising=False)
    monkeypatch.setattr(dub_module, "get_settings", lambda: type("Cfg", (), {"DATA_DIR": tmp_path / "keys"})(), raising=False)
    async with sessions.begin() as db:
        db.add_all([
            Provider(id="elevenlabs", name="Eleven", provider_type="audio"),
            Provider(id="edge_tts", name="Edge", provider_type="audio"),
            Provider(id="google_cloud_tts", name="Google", provider_type="audio"),
        ])
        await db.flush()
        db.add_all([
            Project(id="project-a", title="A"),
            Project(id="project-b", title="B"),
            VoicePoolEntry(id="voice-a", provider="elevenlabs", language="vi-VN", gender="female",
                           voice_id="voice-a", display_name="Voice A"),
            VoicePoolEntry(id="voice-b", provider="elevenlabs", language="vi-VN", gender="female",
                           voice_id="voice-b", display_name="Voice B"),
            VoicePoolEntry(id="voice-edge", provider="edge_tts", language="vi-VN", gender="female",
                           voice_id="vi-VN-HoaiMyNeural", display_name="Hoai My"),
            VoicePoolEntry(id="voice-google", provider="google_cloud_tts", language="vi-VN", gender="female",
                           voice_id="vi-VN-Wavenet-A", display_name="Google"),
        ])
        one = CatalogModel(provider_id="elevenlabs", remote_model_id="model-one", source="discovered",
                           capability_status="KNOWN", capabilities=["TTS"])
        two = CatalogModel(provider_id="elevenlabs", remote_model_id="model-two", source="discovered",
                           capability_status="KNOWN", capabilities=["TTS"])
        edge = CatalogModel(provider_id="edge_tts", remote_model_id="edge-tts", source="system",
                            capability_status="KNOWN", capabilities=["TTS"])
        google = CatalogModel(provider_id="google_cloud_tts", remote_model_id="vi-VN-Wavenet-A",
                              source="manual", capability_status="KNOWN", capabilities=["TTS"])
        db.add_all([one, two, edge, google])
        await db.flush()
        await (await CredentialService.open(db, tmp_path / "keys")).create("elevenlabs", "synthetic-secret")
        db.add(AIFunctionConfig(function_id="tts", function_name="TTS", capability="TTS",
                                primary_provider_id="elevenlabs", model_id=one.id))
    yield sessions, tmp_path, one.id, two.id, edge.id
    await engine.dispose()


class Registry:
    def __init__(self, providers):
        self.providers = providers

    def get_audio(self, provider_id):
        return self.providers.get(provider_id)


def context(path: Path, project="project-a", speaker="Speaker 1"):
    path.write_bytes(b"video")
    return WorkflowContext(project_id=project, video_path=str(path), target_language="vi",
                           translated_segments=[{"id": "s1", "number": 1, "speaker_id": speaker,
                                                 "start_time": 0.0, "end_time": 1.0,
                                                 "translated_text": "Xin chào"}])


@pytest.mark.asyncio
async def test_unified_dub_uses_exact_default_then_same_provider_fallback_and_resume_cache(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, default_id, alternative_id, _ = catalog
    calls = []

    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key, voice_id))
            if route_target.remote_model_id == "model-one":
                return GenerationResult(success=False, error_code="HTTP_404",
                                        error_message="synthetic-secret")
            output_path.write_bytes(b"synthetic-audio")
            return GenerationResult(success=True, file_path=output_path)

    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven()}), raising=False)
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration, raising=False)
    async with sessions.begin() as db:
        db.add(SpeakerVoiceMapping(id="map", project_id="project-a", speaker_id="Speaker 1",
                                   voice_provider="elevenlabs", voice_id="voice-a"))
    ctx = context(path / "source.mp4")
    stage = DubStage()
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", ctx, db)
    await stage.execute_step("tts_generation", ctx, None)
    assert calls == [("model-one", "synthetic-secret", "voice-a"),
                     ("model-two", "synthetic-secret", "voice-a")]
    assert ctx.audio_segments_info[0]["tts_audio_duration"] == 1.0
    assert ctx.audio_segments_info[0]["catalog_model_id"] == alternative_id
    restored = WorkflowContext.from_dict(ctx.to_dict())
    await stage.execute_step("tts_generation", restored, None)
    assert len(calls) == 2
    assert restored.audio_segments_info == ctx.audio_segments_info
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "tts")).model_id = alternative_id
    await stage.execute_step("tts_generation", restored, None)
    assert len(calls) == 3
    assert calls[-1] == ("model-two", "synthetic-secret", "voice-a")
    assert "synthetic-secret" not in json.dumps(restored.to_dict())


async def _duration(_path):
    return 1.0


@pytest.mark.asyncio
async def test_unified_dub_preserves_explicit_voice_and_rejects_wrong_language(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, *_ = catalog
    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven()}), raising=False)
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration, raising=False)
    async with sessions.begin() as db:
        db.add(SpeakerVoiceMapping(id="map", project_id="project-a", speaker_id="Speaker 1",
                                   voice_provider="elevenlabs", voice_id="voice-b"))
    ctx = context(path / "source.mp4")
    stage = DubStage()
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", ctx, db)
    await stage.execute_step("tts_generation", ctx, None)
    assert ctx.audio_segments_info[0]["voice_id"] == "voice-b"
    ctx.target_language = "en"
    with pytest.raises(Exception, match="compatible TTS voice"):
        await stage.execute_step("tts_generation", ctx, None)


@pytest.mark.asyncio
async def test_unified_dub_failure_is_redacted_and_google_not_used(catalog, monkeypatch, caplog):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, *_ = catalog
    calls = []
    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append(route_target.provider_id)
            return GenerationResult(success=False, error_code="HTTP_429", error_message="synthetic-secret")
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven()}), raising=False)
    async with sessions.begin() as db:
        db.add(SpeakerVoiceMapping(id="map", project_id="project-a", speaker_id="Speaker 1",
                                   voice_provider="elevenlabs", voice_id="voice-a"))
    ctx = context(path / "source.mp4")
    stage = DubStage()
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", ctx, db)
    with pytest.raises(Exception, match="rate_limit") as error:
        await stage.execute_step("tts_generation", ctx, None)
    assert calls == ["elevenlabs"]
    assert "synthetic-secret" not in str(error.value) + caplog.text + json.dumps(ctx.to_dict())
    assert not ctx.audio_segments_info


@pytest.mark.asyncio
async def test_unified_edge_default_is_keyless_and_preserves_saved_voice(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "tts")).model_id = edge_id
        (await db.get(AIFunctionConfig, "tts")).primary_provider_id = "edge_tts"
        db.add(SpeakerVoiceMapping(id="edge-map", project_id="project-a", speaker_id="Speaker 1",
                                   character_id="edge-character", voice_provider="edge",
                                   voice_id="vi-VN-HoaiMyNeural"))
        db.add(CharacterVoiceProfile(id="edge-profile", project_id="project-a",
                                     character_id="edge-character", name="Speaker", gender="female",
                                     voice_provider="edge", voice_id="vi-VN-HoaiMyNeural",
                                     confirmed_by_user=True))
    calls = []
    class Edge:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key, voice_id))
            output_path.write_bytes(b"edge-audio")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    ctx = context(path / "edge.mp4")
    stage = DubStage()
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", ctx, db)
    assert ctx.speaker_voice_map["Speaker 1"]["provider"] == "edge_tts"
    assert ctx.speaker_voice_map["Speaker 1"]["confirmed_by_user"] is True
    await stage.execute_step("tts_generation", ctx, None)
    assert calls == [("edge-tts", None, "vi-VN-HoaiMyNeural")]


@pytest.mark.asyncio
async def test_unified_two_jobs_use_distinct_default_models_and_keys(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, second_id, _ = catalog
    entered, release = asyncio.Event(), asyncio.Event()
    calls = []
    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key, voice_id))
            if route_target.remote_model_id == "model-one":
                entered.set()
                await release.wait()
            output_path.write_bytes(b"audio")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    stage = DubStage()
    one = context(path / "one.mp4", "project-a")
    two = context(path / "two.mp4", "project-b")
    one.speaker_voice_map = {"Speaker 1": {"provider": "elevenlabs", "voice_id": "voice-a",
                                           "confirmed_by_user": True}}
    two.speaker_voice_map = {"Speaker 1": {"provider": "elevenlabs", "voice_id": "voice-b",
                                           "confirmed_by_user": True}}
    first = asyncio.create_task(stage.execute_step("tts_generation", one, None))
    try:
        await asyncio.wait_for(entered.wait(), 5)
        async with sessions.begin() as db:
            (await db.get(AIFunctionConfig, "tts")).model_id = second_id
        await asyncio.wait_for(stage.execute_step("tts_generation", two, None), 5)
    finally:
        release.set()
        await asyncio.wait_for(first, 5)
    assert calls == [("model-one", "synthetic-secret", "voice-a"),
                     ("model-two", "synthetic-secret", "voice-b")]
    assert one.audio_segments_info[0]["tts_audio_path"] != two.audio_segments_info[0]["tts_audio_path"]


@pytest.mark.asyncio
async def test_google_voice_without_access_bridge_cannot_be_default(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, *_ = catalog
    async with sessions.begin() as db:
        google = await db.scalar(select(CatalogModel).where(
            CatalogModel.provider_id == "google_cloud_tts"))
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = google.id
        config.primary_provider_id = "google_cloud_tts"
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({}))
    with pytest.raises(RouteConfigurationError, match="credential access"):
        await DubStage().execute_step("tts_generation", context(path / "google.mp4"), None)


@pytest.mark.asyncio
async def test_initialized_catalog_requires_default(catalog):
    sessions, path, *_ = catalog
    async with sessions.begin() as db:
        (await db.get(AIFunctionConfig, "tts")).model_id = ""
    with pytest.raises(RouteConfigurationError, match="default"):
        await DubStage().execute_step("tts_generation", context(path / "missing.mp4"), None)


@pytest.mark.asyncio
async def test_seeded_legacy_edge_default_retains_positional_call(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, *_ = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.primary_provider_id = "edge_tts"
        config.model_id = "edge-tts"
    calls = []
    class LegacyEdge:
        async def generate_audio(self, text, voice_id, output_path):
            calls.append((text, voice_id))
            output_path.write_bytes(b"legacy")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": LegacyEdge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    ctx = context(path / "legacy.mp4")
    await DubStage().execute_step("tts_generation", ctx, None)
    assert calls == [("Xin chào", "vi-VN-HoaiMyNeural")]
    assert "catalog_model_id" not in ctx.audio_segments_info[0]


async def test_imported_archival_tts_row_does_not_activate_unified_catalog(catalog):
    sessions, path, *_ = catalog
    async with sessions.begin() as db:
        await db.execute(delete(APIKey))
        await db.execute(delete(CatalogModel))
        db.add(CatalogModel(provider_id="elevenlabs", remote_model_id="archival-voice",
                            source="legacy_import", capability_status="FULL_UNKNOWN"))
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = "archival-voice"
    ctx = WorkflowContext(project_id="project-a", video_path=str(path / "legacy-import.mp4"),
                          translated_segments=[])
    assert await DubStage()._tts_generation(ctx) == {"tts_clips_generated": 0}


@pytest.mark.asyncio
async def test_confirmed_legacy_edge_profile_alias_still_matches_saved_speaker(catalog):
    sessions, _, *_ = catalog
    async with sessions.begin() as db:
        db.add(CharacterVoiceProfile(id="profile", project_id="project-a", character_id="character-a",
                                     name="Speaker", gender="female", voice_provider="edge",
                                     voice_id="vi-VN-HoaiMyNeural", confirmed_by_user=True))
        db.add(SpeakerVoiceMapping(id="mapping", project_id="project-a", speaker_id="Speaker 1",
                                   character_id="character-a", voice_provider="edge",
                                   voice_id="vi-VN-HoaiMyNeural"))
    ctx = WorkflowContext(project_id="project-a")
    async with sessions() as db:
        await DubStage().execute_step("speaker_to_voice_mapping", ctx, db)
    assert ctx.speaker_voice_map["Speaker 1"]["provider"] == "edge_tts"
    assert ctx.speaker_voice_map["Speaker 1"]["gender"] == "female"
    restored = WorkflowContext.from_dict(ctx.to_dict()).speaker_voice_map["Speaker 1"]
    assert restored["provider"] == "edge_tts"
    assert restored["voice_id"] == "vi-VN-HoaiMyNeural"
    assert restored["confirmed_by_user"] is True
    assert restored["gender"] == "female"


@pytest.mark.asyncio
async def test_unmapped_speaker_can_fallback_to_keyless_edge_without_reusing_eleven_voice(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    _, path, *_ = catalog
    calls = []
    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.provider_id, voice_id, api_key))
            return GenerationResult(success=False, error_code="HTTP_401")
    class Edge:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.provider_id, voice_id, api_key))
            output_path.write_bytes(b"edge")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven(), "edge_tts": Edge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    ctx = context(path / "unmapped.mp4")
    await DubStage().execute_step("tts_generation", ctx, None)
    assert calls == [("elevenlabs", "voice-a", "synthetic-secret"),
                     ("edge_tts", "vi-VN-HoaiMyNeural", None)]
    assert ctx.audio_segments_info[0]["voice_provider"] == "edge_tts"


@pytest.mark.asyncio
async def test_high_confidence_auto_mapping_can_fallback_but_confirmed_profile_stays_pinned(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, *_ = catalog
    async with sessions.begin() as db:
        db.add(SpeakerVoiceMapping(id="auto-map", project_id="project-a", speaker_id="Speaker 1",
                                   character_id="character-a", voice_provider="elevenlabs",
                                   voice_id="voice-a", confidence=0.99, needs_review=False))
    calls = []
    class Eleven:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.provider_id, voice_id))
            return GenerationResult(success=False, error_code="HTTP_404")
    class Edge:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.provider_id, voice_id))
            output_path.write_bytes(b"edge")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"elevenlabs": Eleven(), "edge_tts": Edge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    stage = DubStage()
    auto = context(path / "auto.mp4")
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", auto, db)
    assert auto.speaker_voice_map["Speaker 1"]["confirmed_by_user"] is False
    await stage.execute_step("tts_generation", auto, None)
    assert calls[-1] == ("edge_tts", "vi-VN-HoaiMyNeural")

    async with sessions.begin() as db:
        db.add(CharacterVoiceProfile(id="confirmed", project_id="project-a", character_id="character-a",
                                     name="Speaker", gender="female", voice_provider="elevenlabs",
                                     voice_id="voice-a", confirmed_by_user=True))
    confirmed = context(path / "confirmed.mp4")
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", confirmed, db)
    assert confirmed.speaker_voice_map["Speaker 1"]["confirmed_by_user"] is True
    prior = len(calls)
    with pytest.raises(Exception, match="model_unavailable"):
        await stage.execute_step("tts_generation", confirmed, None)
    assert all(provider == "elevenlabs" for provider, _ in calls[prior:])


@pytest.mark.asyncio
async def test_clean_canonical_edge_catalog_validates_default_voice_without_pool_seed(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        await db.delete(await db.get(VoicePoolEntry, "voice-edge"))
    calls = []
    class Edge:
        async def get_voices(self):
            calls.append("lookup")
            return [VoiceInfo(id="vi-VN-HoaiMyNeural", name="Hoai My", language="vi-VN", gender="female")]
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((voice_id, api_key))
            output_path.write_bytes(b"edge")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    ctx = context(path / "fresh-edge.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True}}
    await DubStage().execute_step("tts_generation", ctx, None)
    assert calls == ["lookup", ("vi-VN-HoaiMyNeural", None)]
    assert ctx.audio_segments_info[0]["voice_provider"] == "edge_tts"


@pytest.mark.asyncio
async def test_explicitly_disabled_edge_voice_cannot_be_revalidated(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        (await db.get(VoicePoolEntry, "voice-edge")).enabled = False
    class Edge:
        async def get_voices(self):
            raise AssertionError("Disabled voice must not be looked up")
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    ctx = context(path / "disabled-edge.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True}}
    with pytest.raises(RouteConfigurationError, match="compatible TTS voice"):
        await DubStage().execute_step("tts_generation", ctx, None)


@pytest.mark.asyncio
@pytest.mark.parametrize("language,gender", [("en-US", "female"), ("vi-VN", "male")])
async def test_edge_voice_lookup_rejects_wrong_language_or_gender(catalog, monkeypatch, language, gender):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        await db.delete(await db.get(VoicePoolEntry, "voice-edge"))
    class Edge:
        async def get_voices(self):
            return [VoiceInfo(id="vi-VN-HoaiMyNeural", name="Hoai My", language=language, gender=gender)]
        async def generate_audio(self, *args, **kwargs):
            raise AssertionError("Ineligible voice must not synthesize")
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    ctx = context(path / f"wrong-{language}-{gender}.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True, "gender": "female"}}
    with pytest.raises(RouteConfigurationError, match="compatible TTS voice"):
        await DubStage().execute_step("tts_generation", ctx, None)


@pytest.mark.asyncio
async def test_unlisted_edge_voice_lookup_has_finite_timeout(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        await db.delete(await db.get(VoicePoolEntry, "voice-edge"))
    class Edge:
        async def get_voices(self):
            await asyncio.sleep(60)
            return []
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    ctx = context(path / "hung-edge.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True}}
    start = asyncio.get_running_loop().time()
    with pytest.raises(RouteConfigurationError, match="compatible TTS voice"):
        await DubStage().execute_step("tts_generation", ctx, None)
    assert asyncio.get_running_loop().time() - start < 7


@pytest.mark.asyncio
@pytest.mark.parametrize("canonical_row_present", [False, True])
async def test_legacy_disabled_edge_alias_overrides_live_or_canonical_voice(
    catalog, monkeypatch, canonical_row_present,
):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        if not canonical_row_present:
            await db.delete(await db.get(VoicePoolEntry, "voice-edge"))
        db.add(VoicePoolEntry(id="legacy-disabled", provider="edge", language="vi-VN", gender="female",
                              voice_id="vi-VN-HoaiMyNeural", display_name="Hoai My", enabled=False))
    calls = []
    class Edge:
        async def get_voices(self):
            calls.append("lookup")
            return [VoiceInfo(id="vi-VN-HoaiMyNeural", name="Hoai My", language="vi-VN", gender="female")]
        async def generate_audio(self, *args, **kwargs):
            calls.append("synthesize")
            raise AssertionError("A disabled alias must prevent synthesis")
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    ctx = context(path / f"legacy-disabled-{canonical_row_present}.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True}}
    with pytest.raises(RouteConfigurationError, match="compatible TTS voice"):
        await DubStage().execute_step("tts_generation", ctx, None)
    assert calls == []


@pytest.mark.asyncio
async def test_legacy_enabled_edge_alias_is_eligible_without_live_lookup(catalog, monkeypatch):
    import app.workflow.stages.dub_stage as dub_module

    sessions, path, _, _, edge_id = catalog
    async with sessions.begin() as db:
        config = await db.get(AIFunctionConfig, "tts")
        config.model_id = edge_id
        config.primary_provider_id = "edge_tts"
        await db.delete(await db.get(VoicePoolEntry, "voice-edge"))
        db.add(VoicePoolEntry(id="legacy-enabled", provider="edge", language="vi-VN", gender="female",
                              voice_id="vi-VN-HoaiMyNeural", display_name="Hoai My", enabled=True))
    calls = []
    class Edge:
        async def get_voices(self):
            calls.append("lookup")
            return []
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append("synthesize")
            output_path.write_bytes(b"edge")
            return GenerationResult(success=True, file_path=output_path)
    monkeypatch.setattr(dub_module, "get_registry", lambda: Registry({"edge_tts": Edge()}))
    monkeypatch.setattr(dub_module, "probe_duration_async", _duration)
    ctx = context(path / "legacy-enabled.mp4")
    ctx.speaker_voice_map = {"Speaker 1": {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural",
                                           "confirmed_by_user": True}}
    await DubStage().execute_step("tts_generation", ctx, None)
    assert calls == ["synthesize"]
