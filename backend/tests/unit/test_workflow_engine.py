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
from app.workflow.stages.translate_stage import TranslateStage


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


