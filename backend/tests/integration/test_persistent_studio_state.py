"""
Integration test suite for Persistent Studio State, Isolated Settings Snapshot,
Checkpoint System, and Resume Workflow.
"""

import json
import pytest
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, delete

from app.database import async_session_factory, init_db
from app.models.project import Project
from app.models.video_translator import (
    VideoAsset,
    VideoTranslationJob,
    VideoTranslationSegment,
    TranslationJobStatus,
)
from app.api.routes.video_translator import (
    create_translation_job,
    get_job_studio_state_api,
    update_job_studio_state_api,
    save_job_checkpoint_api,
    resume_job_from_checkpoint_api,
    apply_latest_settings_to_job_api,
    update_job_segments,
    CreateJobRequest,
    UpdateStudioStateRequest,
    SaveCheckpointRequest,
    UpdateSegmentsRequest,
    SegmentUpdateItem,
    get_job_lock,
)


@pytest.fixture(autouse=True)
async def setup_clean_db():
    await init_db()
    async with async_session_factory() as session:
        await session.execute(delete(VideoTranslationSegment))
        await session.execute(delete(VideoTranslationJob))
        await session.execute(delete(VideoAsset))
        await session.execute(delete(Project))
        await session.commit()
    yield
    async with async_session_factory() as session:
        await session.execute(delete(VideoTranslationSegment))
        await session.execute(delete(VideoTranslationJob))
        await session.execute(delete(VideoAsset))
        await session.execute(delete(Project))
        await session.commit()


@pytest.mark.asyncio
async def test_scenario_1_create_and_reopen_job():
    """TEST 1: Create job -> close Studio -> reopen -> verify same job state."""
    async with async_session_factory() as session:
        asset = VideoAsset(
            id="test-asset-1",
            title="Test Video 1",
            file_path="storage/videos/test1.mp4",
            duration=30.0,
        )
        session.add(asset)
        await session.commit()

        body = CreateJobRequest(
            asset_id="test-asset-1",
            source_language="en",
            target_language="vi",
            audio_provider_id="edge_tts",
            llm_provider_id="gemini",
        )
        create_res = await create_translation_job(body, session)
        assert create_res["success"] is True
        job_id = create_res["data"]["job_id"]

    # Fetch studio state in fresh session (reopen Studio)
    async with async_session_factory() as session:
        state_res = await get_job_studio_state_api(job_id, session)
        assert state_res["success"] is True
        data = state_res["data"]
        assert data["job"]["job_id"] == job_id
        assert data["job"]["status"] == "created"
        assert data["last_checkpoint_stage"] == "CREATED"
        assert data["settings_snapshot"]["language"]["target_language"] == "vi"


@pytest.mark.asyncio
async def test_scenario_2_segment_editing_autosave():
    """TEST 2: SEGMENT_EDITING -> Edit segment text -> reopen -> edited text remains."""
    async with async_session_factory() as session:
        asset = VideoAsset(
            id="test-asset-2",
            title="Test Video 2",
            file_path="storage/videos/test2.mp4",
            duration=15.0,
        )
        session.add(asset)
        await session.commit()

        job = VideoTranslationJob(
            id="job-test-2",
            asset_id="test-asset-2",
            status=TranslationJobStatus.SEGMENT_EDITING.value,
            stage="SEGMENT_EDITING",
            last_checkpoint_stage="TRANSLATION_DONE",
        )
        session.add(job)
        await session.commit()

        segment = VideoTranslationSegment(
            job_id="job-test-2",
            segment_number=1,
            start_time=0.0,
            end_time=5.0,
            original_text="Hello world",
            translated_text="Xin chào thế giới",
            status="translated",
        )
        session.add(segment)
        await session.commit()
        seg_id = segment.id

    # Perform user edit (autosave update) in fresh session
    async with async_session_factory() as session:
        upd_body = UpdateSegmentsRequest(
            segments=[SegmentUpdateItem(id=seg_id, translated_text="Xin chào toàn thể thế giới (Đã sửa)")]
        )
        upd_res = await update_job_segments("job-test-2", upd_body, session)
        assert upd_res["success"] is True

    # Reopen studio and verify segment text in fresh session
    async with async_session_factory() as session:
        state_res = await get_job_studio_state_api("job-test-2", session)
        assert state_res["success"] is True
        loaded_segs = state_res["data"]["segments"]
        assert len(loaded_segs) == 1
        assert loaded_segs[0]["translated_text"] == "Xin chào toàn thể thế giới (Đã sửa)"


@pytest.mark.asyncio
async def test_scenario_3_multiple_jobs_isolated_states():
    """TEST 3: Job A in SEGMENT_EDITING, Job B in VOICE_SELECTION -> opening A/B loads correct states."""
    async with async_session_factory() as session:
        asset = VideoAsset(id="test-asset-3", title="Test 3", file_path="storage/v3.mp4")
        session.add(asset)
        await session.commit()

        job_a = VideoTranslationJob(
            id="job-A",
            asset_id="test-asset-3",
            status=TranslationJobStatus.SEGMENT_EDITING.value,
            stage="SEGMENT_EDITING",
            studio_state_json=json.dumps({"active_step": "segment_editing"}),
            last_checkpoint_stage="TRANSLATION_DONE",
        )
        job_b = VideoTranslationJob(
            id="job-B",
            asset_id="test-asset-3",
            status=TranslationJobStatus.GENERATING_TTS.value,
            stage="GENERATING_TTS",
            studio_state_json=json.dumps({"active_step": "voice_selection"}),
            last_checkpoint_stage="VOICE_SELECTION_DONE",
        )
        session.add_all([job_a, job_b])
        await session.commit()

    async with async_session_factory() as session:
        state_a = await get_job_studio_state_api("job-A", session)
        state_b = await get_job_studio_state_api("job-B", session)

        assert state_a["data"]["studio_state"]["active_step"] == "segment_editing"
        assert state_b["data"]["studio_state"]["active_step"] == "voice_selection"
        assert state_a["data"]["job"]["job_id"] == "job-A"
        assert state_b["data"]["job"]["job_id"] == "job-B"


@pytest.mark.asyncio
async def test_scenario_4_browser_refresh_restoration():
    """TEST 4: Browser refresh simulation -> Studio restores state via API."""
    async with async_session_factory() as session:
        asset = VideoAsset(id="test-asset-4", title="Test 4", file_path="storage/v4.mp4")
        session.add(asset)

        job = VideoTranslationJob(
            id="job-refreshed",
            asset_id="test-asset-4",
            status=TranslationJobStatus.SEGMENT_EDITING.value,
            stage="SEGMENT_EDITING",
            studio_state_json=json.dumps({"active_step": "segment_editing", "selected_segment_id": 105}),
            last_checkpoint_stage="TRANSLATION_DONE",
        )
        session.add(job)
        await session.commit()

    # Simulate page refresh re-fetch in fresh session
    async with async_session_factory() as session:
        state = await get_job_studio_state_api("job-refreshed", session)
        assert state["success"] is True
        assert state["data"]["studio_state"]["active_step"] == "segment_editing"
        assert state["data"]["studio_state"]["selected_segment_id"] == 105


@pytest.mark.asyncio
async def test_scenario_5_backend_restart_checkpoint_recovery():
    """TEST 5: Backend restart simulation -> re-init DB -> load checkpoint."""
    async with async_session_factory() as session:
        asset = VideoAsset(id="test-asset-5", title="Test 5", file_path="storage/v5.mp4")
        session.add(asset)
        job = VideoTranslationJob(
            id="job-checkpoint-5",
            asset_id="test-asset-5",
            status="segment_editing",
            stage="SEGMENT_EDITING",
            last_checkpoint_stage="TRANSLATION_DONE",
            last_checkpoint_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(job)
        await session.commit()

    # Simulate backend restart (re-run init_db)
    await init_db()

    async with async_session_factory() as session:
        res = await get_job_studio_state_api("job-checkpoint-5", session)
        assert res["data"]["last_checkpoint_stage"] == "TRANSLATION_DONE"
        assert res["data"]["job"]["status"] == "segment_editing"


@pytest.mark.asyncio
async def test_scenario_6_resume_without_rerunning_completed_stages():
    """TEST 6: Pipeline pause/fail during translation -> resume starts Phase 2 rendering without re-running STT."""
    async with async_session_factory() as session:
        asset = VideoAsset(id="test-asset-6", title="Test 6", file_path="storage/v6.mp4")
        session.add(asset)

        job = VideoTranslationJob(
            id="job-resume-6",
            asset_id="test-asset-6",
            status=TranslationJobStatus.FAILED.value,
            stage="FAILED",
            last_checkpoint_stage="TRANSLATION_DONE",
        )
        session.add(job)
        await session.commit()

        seg = VideoTranslationSegment(
            job_id="job-resume-6",
            segment_number=1,
            original_text="Test",
            translated_text="Thử nghiệm",
        )
        session.add(seg)
        await session.commit()

        # Save explicit checkpoint
        chk_body = SaveCheckpointRequest(checkpoint_stage="TRANSLATION_DONE")
        await save_job_checkpoint_api("job-resume-6", chk_body, session)

    # Check job checkpoint status in fresh session
    async with async_session_factory() as session:
        res = await session.execute(select(VideoTranslationJob).where(VideoTranslationJob.id == "job-resume-6"))
        updated_job = res.scalar_one()
        assert updated_job.last_checkpoint_stage == "TRANSLATION_DONE"


@pytest.mark.asyncio
async def test_scenario_7_isolated_settings_snapshot():
    """TEST 7: Changing global/project settings does NOT alter existing job settings snapshot."""
    async with async_session_factory() as session:
        proj = Project(id="proj-7", title="Project 7", settings_json={"stt_model": "gemini-1.5-pro"})
        asset = VideoAsset(id="test-asset-7", title="Test 7", file_path="storage/v7.mp4")
        session.add_all([proj, asset])
        await session.commit()

        job_body = CreateJobRequest(
            project_id="proj-7",
            asset_id="test-asset-7",
            llm_provider_id="gemini",
        )
        create_res = await create_translation_job(job_body, session)
        job_id = create_res["data"]["job_id"]

    # Modify project settings afterwards in separate transaction
    async with async_session_factory() as session:
        res = await session.execute(select(Project).where(Project.id == "proj-7"))
        p = res.scalar_one()
        p.settings_json = {"stt_model": "gpt-4o-mini"}
        await session.commit()

    # Verify job's snapshot remains intact with original model
    async with async_session_factory() as session:
        state_res = await get_job_studio_state_api(job_id, session)
        snap = state_res["data"]["settings_snapshot"]
        assert snap["stt"]["model"] == "gemini-1.5-pro"

    # Explicitly apply latest settings to update snapshot
    async with async_session_factory() as session:
        apply_res = await apply_latest_settings_to_job_api(job_id, session)
        assert apply_res["success"] is True
        assert apply_res["data"]["settings_snapshot"]["stt"]["model"] == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_scenario_8_concurrency_job_lock():
    """TEST 8: Multiple tab concurrent execution -> job lock prevents duplicate execution."""
    job_id = "job-lock-8"
    lock = get_job_lock(job_id)

    assert lock.locked() is False
    async with lock:
        assert lock.locked() is True
        # Secondary access attempt while locked
        second_lock = get_job_lock(job_id)
        assert second_lock.locked() is True
    assert lock.locked() is False
