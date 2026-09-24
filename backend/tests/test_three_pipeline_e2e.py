"""Settings-to-caller smoke tests for the three historical pipelines."""

import json
import socket
from pathlib import Path

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.api.routes import ai_function_defaults, ai_keys
from app.database import Base
from app.main import app
from app.models import CatalogModel, Project, Provider
from app.models.segment import Segment
from app.models.settings import AIFunctionConfig
from app.models.workflow_engine import SpeakerVoiceMapping, VoicePoolEntry
from app.providers.base import GenerationResult
from app.providers.discovery.types import DiscoveredModel, DiscoveryResult
from app.services.model_refresh_service import ModelRefreshService
from app.services.video_translator import translator_service
from app.workflow import orchestrator as orchestrator_module
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.stages import dub_stage as dub_module
from app.workflow.stages.dub_stage import DubStage
from app.workflow.workflow_context import WorkflowContext


@pytest.fixture
async def flow(tmp_path, monkeypatch):
    def blocked(*_args, **_kwargs):
        raise AssertionError("Unexpected outbound network")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'flow.db'}")
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions.begin() as db:
        db.add_all(Provider(id=provider, name=provider, provider_type="test")
                   for provider in ("openai", "elevenlabs", "fal"))
        db.add_all(AIFunctionConfig(function_id=ident, function_name=ident, capability=capability,
                                    primary_provider_id="legacy", model_id="legacy-model")
                   for ident, capability in (("stt", "STT"), ("tts", "TTS"),
                                             ("video_generation", "VIDEO_GENERATION")))

    responses = {}

    async def discover(provider, secret):
        assert provider in ("openai", "elevenlabs", "fal")
        return responses[secret]

    def context():
        return ai_keys.KeyAPIContext(sessions, tmp_path / "keys",
                                     ModelRefreshService(sessions, tmp_path / "keys", discovery=discover))

    async def isolated_db():
        async with sessions() as db:
            yield db

    monkeypatch.setitem(app.dependency_overrides, ai_keys.get_key_api_context, context)
    monkeypatch.setitem(app.dependency_overrides, ai_function_defaults.get_function_sessions,
                        lambda: sessions)
    monkeypatch.setitem(app.dependency_overrides, get_db, isolated_db)
    monkeypatch.setattr(dub_module, "async_session_factory", sessions)
    monkeypatch.setattr(dub_module, "get_settings", lambda: type("Cfg", (), {"DATA_DIR": tmp_path / "keys"})())
    monkeypatch.setattr(orchestrator_module.settings, "DATA_DIR", tmp_path / "keys")
    from app.services import file_manager
    monkeypatch.setattr(file_manager.settings, "STORAGE_ROOT", tmp_path / "storage")
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, sessions, responses, tmp_path
    finally:
        await engine.dispose()


async def select_discovered_default(flow, provider, function_id, remote_model, secret, metadata=None):
    client, sessions, responses, _ = flow
    responses[secret] = DiscoveryResult("complete", (DiscoveredModel(remote_model, metadata=metadata or {}),),
                                        None, 1, "credential")
    added = await client.post(f"/api/ai/providers/{provider}/keys", json={"key": secret})
    assert added.status_code == 201, added.text
    assert added.json()["data"]["key"]["enabled"] is True
    assert secret not in added.text
    async with sessions() as db:
        model = await db.scalar(select(CatalogModel).where(CatalogModel.provider_id == provider))
        assert model.remote_model_id == remote_model
        model_id = model.id
    selected = await client.put(f"/api/ai/functions/{function_id}", json={"model_id": model_id})
    assert selected.status_code == 200, selected.text
    assert selected.json()["data"]["default_status"] == "ready"
    assert secret not in selected.text
    return model_id


@pytest.mark.asyncio
async def test_studio_settings_discovery_picker_to_mocked_stt(flow, monkeypatch):
    _, sessions, _, path = flow
    secret = "synthetic-studio-secret"
    await select_discovered_default(flow, "openai", "stt", "speech-custom-v2", secret)
    audio = path / "speech.wav"
    audio.write_bytes(b"RIFF synthetic audio")
    async def duration(_path):
        return 2.0
    monkeypatch.setattr(translator_service, "probe_duration_async", duration)
    calls = []

    async def post(_client, url, **kwargs):
        calls.append((url, kwargs["data"]["model"], kwargs["headers"]["Authorization"]))
        return httpx.Response(200, json={"language": "English", "segments": [
            {"start": 0, "end": 2, "text": "Hi"}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    segments, language = await translator_service.speech_to_text_and_detect_language(
        audio, sessions=sessions, data_dir=path / "keys")
    assert segments[0]["text"] == "Hi" and language == "English"
    assert calls == [(calls[0][0], "speech-custom-v2", f"Bearer {secret}")]


@pytest.mark.asyncio
async def test_unified_settings_discovery_picker_to_mocked_dub(flow, monkeypatch):
    _, sessions, _, path = flow
    secret = "synthetic-unified-secret"
    model_id = await select_discovered_default(flow, "elevenlabs", "tts", "voice-model-custom", secret,
                                               {"can_do_text_to_speech": True})
    async with sessions.begin() as db:
        db.add_all([Project(id="unified-project", title="Unified"),
                    VoicePoolEntry(id="voice-one", provider="elevenlabs", language="vi-VN",
                                   gender="female", voice_id="voice-one", display_name="Voice One"),
                    SpeakerVoiceMapping(id="voice-map", project_id="unified-project", speaker_id="Speaker 1",
                                        voice_provider="elevenlabs", voice_id="voice-one")])
    calls = []

    class Adapter:
        async def generate_audio(self, text, voice_id, output_path, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key, voice_id))
            output_path.write_bytes(b"synthetic-audio")
            return GenerationResult(success=True, file_path=output_path)

    monkeypatch.setattr(dub_module, "get_registry", lambda: type("Registry", (), {
        "get_audio": lambda _self, provider: Adapter() if provider == "elevenlabs" else None})())
    async def duration(_path):
        return 1.0
    monkeypatch.setattr(dub_module, "probe_duration_async", duration)
    video = path / "unified.mp4"
    video.write_bytes(b"synthetic-video")
    context = WorkflowContext(project_id="unified-project", video_path=str(video), target_language="vi",
                              translated_segments=[{"id": "s1", "number": 1, "speaker_id": "Speaker 1",
                                                    "start_time": 0.0, "end_time": 1.0,
                                                    "translated_text": "Xin chào"}])
    stage = DubStage()
    async with sessions() as db:
        await stage.execute_step("speaker_to_voice_mapping", context, db)
    await stage.execute_step("tts_generation", context, None)
    assert calls == [("voice-model-custom", secret, "voice-one")]
    assert context.audio_segments_info[0]["catalog_model_id"] == model_id
    assert secret not in json.dumps(context.to_dict())


@pytest.mark.asyncio
async def test_legacy_project_settings_discovery_picker_to_mocked_video(flow, monkeypatch):
    _, sessions, _, path = flow
    secret = "synthetic-legacy-secret"
    remote = "fal-ai/hunyuan-video"
    await select_discovered_default(flow, "fal", "video_generation", remote, secret,
                                    {"category": "video"})
    async with sessions.begin() as db:
        project = Project(id="legacy-project", workflow_status="prechecked",
                          workflow_mode="audio_video")
        db.add_all([project, Segment(project_id=project.id, segment_number=1, text_content="story")])
    calls = []

    class Adapter:
        provider_id = "fal"

        async def generate_video(self, _prompt, _duration, output, *, route_target, api_key):
            calls.append((route_target.remote_model_id, api_key))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"synthetic-video")
            return GenerationResult(True, file_path=output, provider_id="fal")

    async def duration(_path):
        return 5.0
    monkeypatch.setattr(orchestrator_module, "probe_duration_async", duration)
    async with sessions() as db:
        orchestrator = WorkflowOrchestrator(db, "legacy-project")
        monkeypatch.setattr(orchestrator._registry, "get_video", lambda provider: Adapter() if provider == "fal" else None)
        async def completed_non_ai_stage():
            return None
        monkeypatch.setattr(orchestrator, "_generate_all_audio", completed_non_ai_stage)
        monkeypatch.setattr(orchestrator, "_sync_all_segments", completed_non_ai_stage)
        monkeypatch.setattr(orchestrator, "_merge_final", completed_non_ai_stage)
        await orchestrator.run()
        segment = await db.scalar(select(Segment).where(Segment.project_id == "legacy-project"))
        assert segment.video_status == "completed"
        assert Path(segment.video_file_path).read_bytes() == b"synthetic-video"
        assert (await db.get(Project, "legacy-project")).workflow_status == "completed"
    assert calls == [(remote, secret)]
