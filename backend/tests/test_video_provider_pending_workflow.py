"""An accepted video task must remain pending until a person reconciles it."""

import asyncio

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.api.routes.projects import resume_workflow
from app.models.project import Project
from app.models.segment import Segment
from app.services.ai_routing import RoutePending
from app.services.manifest import read_manifest
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.state_machine import can_transition, is_resumable_state


@pytest.fixture
async def pending_case(tmp_path, monkeypatch):
    from app.services import file_manager

    monkeypatch.setattr(file_manager.settings, "STORAGE_ROOT", tmp_path)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'pending.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        project = Project(id="pending-project", workflow_status="prechecked",
                          workflow_mode="audio_video", video_provider_id="fake")
        segment = Segment(project_id=project.id, segment_number=1, text_content="test")
        session.add_all([project, segment])
        await session.commit()
        yield session, project, segment
    await engine.dispose()


@pytest.mark.asyncio
async def test_pending_video_persists_and_blocks_repeat_submission(pending_case, monkeypatch):
    session, project, segment = pending_case
    calls = 0

    class Provider:
        provider_id = "fake"

        async def generate_video(self, *_args):
            nonlocal calls
            calls += 1
            raise RoutePending("private-upstream-detail")

    orchestrator = WorkflowOrchestrator(session, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _id: Provider())
    orchestrator._generate_all_audio = lambda: asyncio.sleep(0)
    queue = asyncio.Queue()
    orchestrator.set_progress_queue(queue)

    await orchestrator.run()
    await session.refresh(project)
    await session.refresh(segment)
    assert calls == 1
    assert project.workflow_status == "provider_pending"
    assert segment.video_status == "provider_pending"
    assert project.error_message == segment.video_error_message
    assert "private-upstream-detail" not in project.error_message
    assert "manual" in project.error_message.lower()
    manifest = read_manifest(project.id)
    assert manifest["workflow_status"] == "provider_pending"
    assert manifest["segments"][0]["video_status"] == "provider_pending"
    assert manifest["segments"][0]["video_error"] == project.error_message
    events = []
    while not queue.empty():
        events.append(queue.get_nowait())
    assert any(event["type"] == "status_change" and event["status"] == "provider_pending"
               and event["message"] == project.error_message for event in events)
    assert not is_resumable_state(project.workflow_status)
    assert not can_transition(project.workflow_status, "prechecked")

    await orchestrator.run()
    with pytest.raises(RoutePending):
        await orchestrator._generate_segment_video(segment, Provider())
    assert calls == 1
    assert project.workflow_status == "provider_pending"
    with pytest.raises(HTTPException) as rejected:
        await resume_workflow(project.id, BackgroundTasks(), session)
    assert rejected.value.status_code == 400
    assert project.workflow_status == "provider_pending"


@pytest.mark.asyncio
async def test_other_video_error_still_fails(pending_case, monkeypatch):
    session, project, segment = pending_case

    class Provider:
        provider_id = "fake"

        async def generate_video(self, *_args):
            raise ValueError("synthetic failure")

    orchestrator = WorkflowOrchestrator(session, project.id)
    monkeypatch.setattr(orchestrator._registry, "get_video", lambda _id: Provider())
    orchestrator._generate_all_audio = lambda: asyncio.sleep(0)
    await orchestrator.run()
    await session.refresh(project)
    await session.refresh(segment)
    assert project.workflow_status == "failed"
    assert segment.video_status == "failed"
