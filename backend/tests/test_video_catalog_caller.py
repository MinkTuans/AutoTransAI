"""Canonical video cutover with disposable catalog and request-local credentials."""

import asyncio
import socket
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import CatalogModel, KeyModelAccess, Project, Provider
from app.models.segment import Segment
from app.models.settings import AIFunctionConfig
from app.providers.base import GenerationResult
from app.core.exceptions import WorkflowError
from app.services.ai_routing import RoutePending, RoutePlan, build_route
from app.services.file_manager import get_segment_video_path
from app.services.credential_service import CredentialService
from app.services.preflight import run_preflight
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow import orchestrator as orchestrator_module


@pytest.fixture
async def video_case(tmp_path, monkeypatch):
    from app.services import file_manager

    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("network")))
    monkeypatch.setattr(file_manager.settings, "STORAGE_ROOT", tmp_path / "storage")
    monkeypatch.setattr(orchestrator_module.settings, "DATA_DIR", tmp_path / "data")
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'video.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as db:
        yield db, sessions, tmp_path
    await engine.dispose()


async def add_model(db, data_dir, provider, remote, key):
    if await db.get(Provider, provider) is None:
        db.add(Provider(id=provider, name=provider, provider_type="video"))
        await db.flush()
    model = CatalogModel(provider_id=provider, remote_model_id=remote,
                         source="manual", capability_status="KNOWN", capabilities=["VIDEO_GENERATION"])
    db.add(model)
    await db.flush()
    credential = await (await CredentialService.open(db, data_dir)).create(provider, key)
    await db.flush()
    db.add(KeyModelAccess(key_id=credential.id, model_id=model.id, provider_id=provider))
    await db.commit()
    return model


def configure(db, model):
    db.add(AIFunctionConfig(function_id="video_generation", function_name="Video",
                            capability="VIDEO_GENERATION", primary_provider_id=model.provider_id,
                            model_id=model.id))


@pytest.mark.asyncio
async def test_canonical_video_uses_exact_model_key_then_falls_back(video_case, monkeypatch):
    db, _sessions, path = video_case
    primary = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secret")
    await add_model(db, path / "data", "kling", "kling-v3", "kling-secret")
    configure(db, primary)
    project = Project(id="video-project", workflow_status="generating_video",
                      workflow_mode="audio_video", video_provider_id="stale-legacy")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = []

    class Adapter:
        def __init__(self, name):
            self.provider_id = name

        async def generate_video(self, _prompt, _duration, output, *, route_target, api_key):
            calls.append((self.provider_id, route_target.remote_model_id, api_key))
            if self.provider_id == "fal":
                raise ValueError("unsupported synthetic model")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"synthetic-video")
            return GenerationResult(True, file_path=output, provider_id=self.provider_id)

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda name: Adapter(name) if name in ("fal", "kling") else None)

    async def duration(_path):
        return 5.0

    monkeypatch.setattr(orchestrator_module, "probe_duration_async", duration)
    await orchestrator._generate_all_video()
    await db.refresh(segment)
    assert segment.video_status == "completed"
    assert Path(segment.video_file_path).read_bytes() == b"synthetic-video"
    assert calls == [("fal", "fal-ai/hunyuan-video", "fal-secret"),
                     ("kling", "kling-v3", "kling-secret")]


@pytest.mark.asyncio
async def test_legacy_video_hold_ignores_unrelated_catalog(video_case, monkeypatch):
    db, _sessions, path = video_case
    await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secret")
    db.add(AIFunctionConfig(function_id="video_generation", function_name="Video",
                            capability="VIDEO_GENERATION", primary_provider_id="kling",
                            model_id="kling-v1"))
    project = Project(id="legacy-project", workflow_status="generating_video",
                      workflow_mode="audio_video", video_provider_id="legacy")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = []

    class Legacy:
        provider_id = "legacy"

        async def generate_video(self, *_args):
            calls.append("legacy")
            return GenerationResult(False, error_message="legacy failure")

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda name: Legacy() if name == "legacy" else None)
    with pytest.raises(WorkflowError, match="segment.*failed video"):
        await orchestrator._generate_all_video()
    assert calls == ["legacy"]


@pytest.mark.asyncio
async def test_post_download_probe_failure_retains_media_and_blocks_resubmission(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secret")
    configure(db, model)
    project = Project(id="probe-project", workflow_status="generating_video", workflow_mode="audio_video")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = 0

    class Adapter:
        provider_id = "fal"

        async def generate_video(self, _prompt, _duration, output, *, route_target, api_key):
            nonlocal calls
            calls += 1
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"delivered")
            return GenerationResult(True, file_path=output, provider_id="fal")

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _name: Adapter())

    async def bad_probe(_path):
        raise RuntimeError("private local diagnostics")

    monkeypatch.setattr(orchestrator_module, "probe_duration_async", bad_probe)
    from app.services.ai_routing import RoutePending
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    await db.refresh(segment)
    assert segment.video_status == "provider_pending"
    assert Path(segment.video_file_path).read_bytes() == b"delivered"
    assert "private" not in (segment.video_error_message or "")
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    assert calls == 1


@pytest.mark.asyncio
async def test_preflight_canonical_uses_catalog_without_live_video_probe(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secret")
    configure(db, model)

    class Adapter:
        max_duration_seconds = 10

        async def validate_configuration(self):
            raise AssertionError("live video probe")

    from app.services import preflight
    monkeypatch.setattr(preflight, "get_registry", lambda: type("Registry", (), {
        "get_audio": lambda *_: None, "get_video": lambda *_: Adapter(),
    })())
    monkeypatch.setattr(preflight, "is_ffmpeg_installed", lambda: True)
    monkeypatch.setattr(preflight, "check_storage_writable", lambda *_: True)
    monkeypatch.setattr(preflight, "get_disk_space_mb", lambda *_: 1000)
    result = await run_preflight("probe-project", "audio_video", None, "legacy", None, 1, db=db)
    video_checks = [check for check in result.checks if check.name.startswith("video_")]
    assert video_checks and all(check.passed for check in video_checks)


@pytest.mark.asyncio
async def test_invalid_explicit_video_default_never_uses_legacy_provider(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "secret")
    configure(db, model)
    config = await db.get(AIFunctionConfig, "video_generation")
    config.model_id = "missing-catalog-id"
    project = Project(id="invalid-project", workflow_status="generating_video",
                      workflow_mode="audio_video", video_provider_id="legacy")
    db.add(project)
    await db.commit()
    calls = []
    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda name: calls.append(name))
    with pytest.raises(WorkflowError, match="unavailable"):
        await orchestrator._generate_all_video()
    assert calls == []


@pytest.mark.asyncio
async def test_canonical_pending_is_terminal_and_safe(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "secret")
    await add_model(db, path / "data", "kling", "kling-v3", "other-secret")
    configure(db, model)
    project = Project(id="terminal-project", workflow_status="generating_video", workflow_mode="audio_video")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = []

    class Adapter:
        async def generate_video(self, _prompt, _duration, _output, *, route_target, api_key):
            calls.append((route_target.provider_id, api_key))
            raise RoutePending("private provider body")

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _name: Adapter())
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    await db.refresh(project)
    await db.refresh(segment)
    assert calls == [("fal", "secret")]
    assert project.workflow_status == segment.video_status == "provider_pending"
    assert "private" not in project.error_message
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_retired_explicit_default_fails_before_legacy_or_catalog_call(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "secret")
    configure(db, model)
    model.retired_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(Project(id="retired-project", workflow_status="generating_video",
                   workflow_mode="audio_video", video_provider_id="legacy"))
    await db.commit()
    calls = []
    orchestrator = WorkflowOrchestrator(db, "retired-project")
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda name: calls.append(name))
    with pytest.raises(WorkflowError, match="unavailable"):
        await orchestrator._generate_all_video()
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["copy", "mkdir", "cleanup", "commit"])
async def test_publish_failure_preserves_download_and_blocks_resubmission(video_case, monkeypatch, failure):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "secret")
    configure(db, model)
    project = Project(id="publish-project", workflow_status="generating_video", workflow_mode="audio_video")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = []

    class Adapter:
        async def generate_video(self, _prompt, _duration, output, *, route_target, api_key):
            calls.append((route_target.model_id, api_key))
            output.write_bytes(b"delivered")
            return GenerationResult(True, file_path=output)

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _name: Adapter())
    if failure == "copy":
        monkeypatch.setattr(orchestrator_module.shutil, "copyfile", lambda *_a: (_ for _ in ()).throw(OSError("private disk diagnostics")))
    elif failure == "mkdir":
        original_mkdir = Path.mkdir
        def broken_mkdir(self, *args, **kwargs):
            if calls and self == get_segment_video_path(project.id, 1).parent:
                raise OSError("private mkdir diagnostics")
            return original_mkdir(self, *args, **kwargs)
        monkeypatch.setattr(Path, "mkdir", broken_mkdir)
    elif failure == "cleanup":
        original_unlink = Path.unlink
        def broken_unlink(self, *args, **kwargs):
            if self.suffix == ".tmp":
                raise OSError("private cleanup diagnostics")
            return original_unlink(self, *args, **kwargs)
        monkeypatch.setattr(Path, "unlink", broken_unlink)
    else:
        original_commit = db.commit
        commits = 0
        async def broken_commit():
            nonlocal commits
            commits += 1
            if commits == 2:
                raise OSError("private commit diagnostics")
            await original_commit()
        monkeypatch.setattr(db, "commit", broken_commit)
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    await db.refresh(segment)
    assert Path(segment.video_file_path).read_bytes() == b"delivered"
    assert "private" not in segment.video_error_message
    with pytest.raises(RoutePending):
        await orchestrator._generate_all_video()
    assert calls == [(model.id, "secret")]


@pytest.mark.asyncio
async def test_two_concurrent_catalog_calls_keep_model_and_key_local(video_case, monkeypatch):
    db, sessions, path = video_case
    fal = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secret")
    kling = await add_model(db, path / "data", "kling", "kling-v3", "kling-secret")
    configure(db, fal)
    first = Project(id="concurrent-fal", workflow_status="generating_video", workflow_mode="audio_video")
    second = Project(id="concurrent-kling", workflow_status="generating_video", workflow_mode="audio_video")
    segments = [Segment(project_id=first.id, segment_number=1, text_content="fal prompt"),
                Segment(project_id=second.id, segment_number=1, text_content="kling prompt")]
    db.add_all([first, second, *segments])
    await db.commit()
    full = await build_route(db, "VIDEO_GENERATION")
    routes = [RoutePlan("VIDEO_GENERATION", (next(t for t in full.targets if t.model_id == model.id),), model.id)
              for model in (fal, kling)]
    calls = []

    class Adapter:
        def __init__(self, provider_id):
            self.provider_id = provider_id

        async def generate_video(self, prompt, _duration, output, *, route_target, api_key):
            await asyncio.sleep(0)
            calls.append((self.provider_id, route_target.model_id, api_key, prompt))
            output.write_bytes(prompt.encode())
            return GenerationResult(True, file_path=output)

    async with sessions() as other_db:
        callers = [WorkflowOrchestrator(db, first.id), WorkflowOrchestrator(other_db, second.id)]
        for caller in callers:
            monkeypatch.setattr(caller._registry, "get_video", lambda name: Adapter(name))
        outputs = await asyncio.gather(*(
            caller._generate_catalog_video(segment, route, get_segment_video_path(caller.project_id, 1))
            for caller, segment, route in zip(callers, segments, routes)
        ))
    assert {item[:3] for item in calls} == {("fal", fal.id, "fal-secret"),
                                               ("kling", kling.id, "kling-secret")}
    assert [item.file_path.read_bytes() for item in outputs] == [b"fal prompt", b"kling prompt"]


@pytest.mark.asyncio
async def test_same_provider_alternative_precedes_cross_provider(video_case, monkeypatch):
    db, _sessions, path = video_case
    primary = await add_model(db, path / "data", "fal", "fal-ai/unsupported-video", "fal-secret")
    secondary = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "fal-secondary")
    await add_model(db, path / "data", "kling", "kling-v3", "kling-secret")
    configure(db, primary)
    project = Project(id="same-provider-project", workflow_status="generating_video", workflow_mode="audio_video")
    segment = Segment(project_id=project.id, segment_number=1, text_content="story")
    db.add_all([project, segment])
    await db.commit()
    calls = []

    class Adapter:
        async def generate_video(self, _prompt, _duration, output, *, route_target, api_key):
            calls.append((route_target.model_id, api_key))
            output.write_bytes(b"video")
            return GenerationResult(True, file_path=output)

    orchestrator = WorkflowOrchestrator(db, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _name: Adapter())
    async def duration(_path):
        return 5.0
    monkeypatch.setattr(orchestrator_module, "probe_duration_async", duration)
    await orchestrator._generate_all_video()
    assert len(calls) == 1 and calls[0][0] == secondary.id
    assert calls[0][1] in {"fal-secret", "fal-secondary"}


@pytest.mark.asyncio
async def test_preflight_rejects_only_unsupported_catalog_video_model(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/unsupported-video", "secret")
    configure(db, model)
    from app.services import preflight
    monkeypatch.setattr(preflight, "get_registry", lambda: type("Registry", (), {
        "get_audio": lambda *_: None, "get_video": lambda *_: object(),
    })())
    monkeypatch.setattr(preflight, "is_ffmpeg_installed", lambda: True)
    monkeypatch.setattr(preflight, "check_storage_writable", lambda *_: True)
    monkeypatch.setattr(preflight, "get_disk_space_mb", lambda *_: 1000)
    result = await run_preflight("unsupported", "audio_video", None, "legacy", None, 1, db=db)
    assert not result.can_start
    assert not next(c for c in result.checks if c.name == "video_provider_configured").passed


@pytest.mark.asyncio
async def test_precheck_endpoint_uses_catalog_instead_of_stale_video_provider(video_case, monkeypatch):
    db, _sessions, path = video_case
    model = await add_model(db, path / "data", "fal", "fal-ai/hunyuan-video", "secret")
    configure(db, model)
    project = Project(id="precheck-project", workflow_status="created", workflow_mode="audio_video",
                      audio_provider_id="audio", video_provider_id="stale", voice_id="voice")
    db.add_all([project, Segment(project_id=project.id, segment_number=1, text_content="story")])
    await db.commit()
    from app.services import preflight
    from app.api.routes.projects import precheck

    class Audio:
        async def validate_configuration(self):
            return True

    class Video:
        max_duration_seconds = 10

        async def validate_configuration(self):
            raise AssertionError("live video request")

    monkeypatch.setattr(preflight, "get_registry", lambda: type("Registry", (), {
        "get_audio": lambda _self, name: Audio() if name == "audio" else None,
        "get_video": lambda _self, name: Video() if name == "fal" else None,
    })())
    monkeypatch.setattr(preflight, "is_ffmpeg_installed", lambda: True)
    monkeypatch.setattr(preflight, "check_storage_writable", lambda *_: True)
    monkeypatch.setattr(preflight, "get_disk_space_mb", lambda *_: 1000)
    result = await precheck(project.id, db)
    assert result["data"]["can_start"]
    await db.refresh(project)
    assert project.workflow_status == "prechecked"
