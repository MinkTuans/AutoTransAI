"""
Integration tests for Auto-Confirm Translation execution and 6-Stage Workflow status synchronization.
"""

import asyncio
import uuid
import importlib
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock

from app.main import app
import app.database as database
from app.models.video_translator import VideoTranslationJob, TranslationJobStatus, VideoAsset


@pytest_asyncio.fixture
async def isolated_runtime(tmp_path, monkeypatch):
    sessions = async_sessionmaker(create_async_engine(
        f"sqlite+aiosqlite:///{tmp_path / 'workflow.sqlite'}"), expire_on_commit=False)
    project_routes = importlib.import_module('app.api.routes.projects')
    translator_routes = importlib.import_module('app.api.routes.video_translator')
    file_manager = importlib.import_module('app.services.file_manager')
    storage_service = importlib.import_module('app.services.storage_service')
    job_logger = importlib.import_module('app.core.job_logger')
    heartbeat = importlib.import_module('app.services.video_translator.heartbeat')
    monkeypatch.setattr(database, 'engine', sessions.kw['bind'])
    for module in (database, project_routes, translator_routes, heartbeat):
        monkeypatch.setattr(module, 'async_session_factory', sessions)
    for module in (database, project_routes, translator_routes,
                   file_manager, storage_service, job_logger):
        monkeypatch.setattr(module.settings, 'DATA_DIR', tmp_path / 'data')
        monkeypatch.setattr(module.settings, 'STORAGE_ROOT', tmp_path / 'storage')
    render = AsyncMock()
    monkeypatch.setattr(translator_routes, 'execute_job_render_pipeline', render)

    async def get_test_session():
        async with sessions() as session:
            yield session

    monkeypatch.setitem(app.dependency_overrides, database.get_session, get_test_session)
    try:
        await database.init_db()
        yield sessions, render
    finally:
        await sessions.kw['bind'].dispose()


@pytest.mark.anyio
async def test_auto_confirm_translation_on_and_off(isolated_runtime):
    """Test Auto-Confirm Translation ON vs OFF state behavior and 6-stage status sync."""
    sessions, render = isolated_runtime

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create project
        proj_res = await client.post(
            "/api/projects",
            json={
                "title": "Test Auto Confirm Proj",
                "workflow_mode": "video_translator",
                "settings_json": {"auto_confirm_translation": True},
            },
        )
        assert proj_res.status_code == 200
        proj_data = proj_res.json()["data"]
        project_id = proj_data["project_id"]

        # 2. Create VideoAsset directly in DB
        asset_id = str(uuid.uuid4())[:8]
        now_dt = datetime.now(timezone.utc).replace(tzinfo=None)
        async with sessions() as session:
            asset = VideoAsset(
                id=asset_id,
                title="Test Video Asset",
                source_type="upload",
                file_path="storage/test.mp4",
                duration=60.0,
                created_at=now_dt,
            )
            session.add(asset)
            await session.commit()

        # 3. Create Job with auto_confirm_translation = True
        job_res = await client.post(
            "/api/video-translator/jobs",
            json={
                "project_id": project_id,
                "asset_id": asset_id,
                "target_language": "vi",
                "auto_confirm_translation": True,
                "auto_confirm_voice": True,
            },
        )
        assert job_res.status_code == 200
        job_id = job_res.json()["data"]["job_id"]

        # 4. Verify initial stage & status
        job_get = await client.get(f"/api/video-translator/jobs/{job_id}")
        assert job_get.status_code == 200
        jdata = job_get.json()["data"]
        assert jdata["auto_confirm_translation"] is True
        assert jdata["stage"] == "QUEUED"

        # 5. Test Workflow Status API sync (Single Source of Truth)
        wf_res = await client.get(f"/api/video-translator/projects/{project_id}/workflow-status")
        assert wf_res.status_code == 200
        wfdata = wf_res.json()["data"]
        assert "stages" in wfdata
        assert len(wfdata["stages"]) == 6
        assert wfdata["current_stage"] in ["INGEST", "ANALYZE", "TRANSLATE", "DUB", "PRODUCE", "PUBLISH"]

        # 6. Test Auto-Confirm OFF mode state mapping
        async with sessions() as session:
            await session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.SEGMENT_EDITING.value,
                    stage="TRANSLATE",
                    auto_confirm_translation=False,
                    current_step="Bản dịch đã hoàn tất (Chờ xác nhận thủ công)",
                )
            )
            await session.commit()

        wf_off_res = await client.get(f"/api/video-translator/projects/{project_id}/workflow-status")
        assert wf_off_res.status_code == 200
        wfdata_off = wf_off_res.json()["data"]
        assert wfdata_off["current_stage"] == "TRANSLATE"
        translate_stage = next(s for s in wfdata_off["stages"] if s["name"] == "TRANSLATE")
        assert translate_stage["status"] == "needs_review"

        # 7. Test Auto-Confirm ON mode transition state mapping (DUB stage)
        async with sessions() as session:
            await session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.GENERATING_TTS.value,
                    stage="DUB",
                    auto_confirm_translation=True,
                    current_step="Bản dịch đã hoàn tất. Tự động chuyển sang Phase 2 (TTS & Dubbing)...",
                )
            )
            await session.commit()

        wf_on_res = await client.get(f"/api/video-translator/projects/{project_id}/workflow-status")
        assert wf_on_res.status_code == 200
        wfdata_on = wf_on_res.json()["data"]
        assert wfdata_on["current_stage"] == "DUB"
        ingest_stage = next(s for s in wfdata_on["stages"] if s["name"] == "INGEST")
        analyze_stage = next(s for s in wfdata_on["stages"] if s["name"] == "ANALYZE")
        translate_stage_on = next(s for s in wfdata_on["stages"] if s["name"] == "TRANSLATE")
        dub_stage = next(s for s in wfdata_on["stages"] if s["name"] == "DUB")

        assert ingest_stage["status"] == "passed"
        assert analyze_stage["status"] == "passed"
        assert translate_stage_on["status"] == "passed"
        assert dub_stage["status"] == "running"

        # 8. Test Backend Auto-Confirm Helper Execution & Idempotency
        from app.api.routes.video_translator import auto_confirm_and_start_render_if_needed, VideoTranslationSegment
        async with sessions() as session:
            await session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status=TranslationJobStatus.SEGMENT_EDITING.value,
                    stage="TRANSLATE",
                    auto_confirm_translation=True,
                    current_step="Bản dịch đã hoàn tất (Chờ xác nhận thủ công)",
                )
            )
            seg = VideoTranslationSegment(
                job_id=job_id,
                segment_number=1,
                start_time=0.0,
                end_time=5.0,
                original_text="Hello world",
                translated_text="Xin chào thế giới",
                status="translated",
            )

            session.add(seg)
            await session.commit()

        # Trigger auto-confirm helper
        confirmed = await auto_confirm_and_start_render_if_needed(job_id)
        assert confirmed is True
        await asyncio.sleep(0)
        render.assert_awaited_once_with(job_id)

        # Check DB state
        async with sessions() as session:
            jres = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == job_id))
            updated_job = jres.scalar_one()
            assert updated_job.status == TranslationJobStatus.GENERATING_TTS.value
            assert updated_job.stage == "DUB"

            sres = await session.execute(select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == job_id))
            updated_seg = sres.scalars().first()
            assert updated_seg.status == "confirmed"

        # Test idempotency (calling again returns False, no duplicate trigger)
        second_confirmed = await auto_confirm_and_start_render_if_needed(job_id)
        assert second_confirmed is False
        render.assert_awaited_once_with(job_id)
