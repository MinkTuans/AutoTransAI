"""Unit tests for the Unified 6-Stage Workflow Engine."""

import pytest
import asyncio
import uuid
from app.models.workflow_engine import (
    WorkflowExecution,
    WorkflowStageExecution,
    WorkflowEngineStatus,
    WorkflowStageStatus,
    ProjectGlossary,
)
from app.workflow.workflow_context import WorkflowContext
from app.workflow.workflow_registry import WorkflowRegistry
from app.workflow.workflow_engine import WorkflowEngine
from app.workflow.stages.publish_stage import PublishStage
from app.workflow.stages.produce_stage import ProduceStage
from app.workflow.stages.translate_stage import TranslateStage
from app.workflow.stages.ingest_stage import IngestStage


@pytest.mark.asyncio
async def test_workflow_registry_stages():
    registry = WorkflowRegistry()
    stages = registry.list_stages()
    assert stages == ["INGEST", "ANALYZE", "TRANSLATE", "DUB", "PRODUCE", "PUBLISH"]

    for stage_name in stages:
        inst = registry.get_stage(stage_name)
        assert hasattr(inst, "STEPS")
        assert len(inst.STEPS) > 0


@pytest.mark.asyncio
async def test_workflow_context_serialization():
    ctx = WorkflowContext(project_id="test_p1")
    ctx.video_path = "/path/to/video.mp4"
    ctx.duration = 120.5
    ctx.glossary = [{"source_term": "张三", "translated_term": "Trương Tam"}]

    data = ctx.to_dict()
    assert data["project_id"] == "test_p1"
    assert data["duration"] == 120.5

    hydrated = WorkflowContext.from_dict(data)
    assert hydrated.project_id == "test_p1"
    assert hydrated.duration == 120.5


def test_ingest_trims_filler_after_audio_extract():
    steps = IngestStage.STEPS
    assert "trim_filler" in steps
    assert steps.index("trim_filler") > steps.index("extract_audio")


def test_ingest_copyright_check_after_trim():
    steps = IngestStage.STEPS
    assert "copyright_check" in steps
    assert steps.index("copyright_check") > steps.index("trim_filler")


@pytest.mark.asyncio
async def test_trim_filler_skipped_when_disabled():
    stage = IngestStage()
    ctx = WorkflowContext(project_id="p-trim-off")
    ctx.settings_snapshot = {"trim_filler_enabled": False}
    ctx.video_path = "/tmp/missing.mp4"
    ctx.duration = 100.0
    res = await stage._trim_filler(ctx)
    assert res["applied"] is False
    assert res["reason"] == "disabled"


@pytest.mark.asyncio
async def test_copyright_check_skipped_when_disabled():
    stage = IngestStage()
    ctx = WorkflowContext(project_id="p-cc-off")
    ctx.settings_snapshot = {"copyright_check_enabled": False}
    res = await stage._copyright_check(ctx)
    assert res["level"] == "skipped"
    assert res["enabled"] is False


def test_produce_generates_thumbnail_after_final_video():
    """Auto thumbnail must run in PRODUCE after the final video QC step."""
    steps = ProduceStage.STEPS
    assert "generate_ai_thumbnail" in steps
    assert steps.index("generate_ai_thumbnail") > steps.index("final_video_qc")


@pytest.mark.asyncio
async def test_generate_ai_thumbnail_skipped_when_disabled():
    stage = ProduceStage()
    ctx = WorkflowContext(project_id="p-thumb")
    ctx.thumbnail_enabled = False
    res = await stage._generate_ai_thumbnail(ctx)
    assert res["generated"] is False
    assert ctx.thumbnail_url is None


@pytest.mark.asyncio
async def test_generate_thumbnail_uses_library_file(tmp_path):
    from app.config import get_settings
    settings = get_settings()
    img = settings.STORAGE_ROOT / "projects" / "p-lib" / "default_thumbnails" / "cover.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 200)
    stage = ProduceStage()
    ctx = WorkflowContext(project_id="p-lib")
    ctx.thumbnail_enabled = True
    ctx.thumbnail_source = "library"
    ctx.thumbnail_library_path = str(img)
    res = await stage._generate_ai_thumbnail(ctx)
    assert res["generated"] is True
    assert res["source"] == "library"
    assert ctx.thumbnail_url and "default_thumbnails" in ctx.thumbnail_url


@pytest.mark.asyncio
async def test_publish_stage_blocked_without_oauth():
    stage = PublishStage()
    ctx = WorkflowContext(project_id="test_pub")
    res = await stage._publish_youtube(ctx, db=None)

    assert ctx.publication_status == "PUBLISHING_BLOCKED"
    assert res["status"] == "PUBLISHING_BLOCKED"
    assert "YouTube OAuth credentials are not configured" in res["reason"]


@pytest.mark.asyncio
async def test_translate_stage_qc():
    stage = TranslateStage()
    ctx = WorkflowContext(project_id="test_trans")
    ctx.source_segments = [{"id": 1, "text": "Hello"}]
    ctx.translated_segments = [{"id": 1, "translated_text": "Xin chào"}]

    qc = await stage.run_qc(ctx)
    assert qc["passed"] is True
    assert qc["stage"] == "TRANSLATE"


@pytest.mark.asyncio
async def test_workflow_engine_start_and_pause():
    from app.database import async_session_factory, init_db
    from app.models.project import Project
    await init_db()

    async with async_session_factory() as session:
        project_id = str(uuid.uuid4())
        project = Project(id=project_id, title="Test Project")
        session.add(project)
        await session.commit()

        engine = WorkflowEngine()

        wf_exec = await engine.start_workflow(project_id, session)
        assert wf_exec is not None
        assert wf_exec.project_id == project_id
        assert wf_exec.status == WorkflowEngineStatus.RUNNING.value

        paused = await engine.pause_workflow(project_id, session)
        assert paused is True

    from app.database import engine as db_engine
    await db_engine.dispose()



