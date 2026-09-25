import asyncio
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_active_studio_task_stops_before_project_files_are_deleted(monkeypatch):
    from app.api.routes import video_translator as studio

    entered = asyncio.Event()
    stopped = asyncio.Event()

    async def rendering():
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()

    task = asyncio.create_task(rendering())
    await entered.wait()
    studio._active_render_tasks["job-1"] = {task}
    monkeypatch.setattr(studio, "stop_job_heartbeat", lambda _job_id: None)
    session = AsyncMock()
    session.get.return_value = None

    assert await studio.quiesce_translation_job_for_deletion("job-1", session) is True
    assert task.done()
    assert stopped.is_set()
    studio._active_render_tasks.pop("job-1", None)
