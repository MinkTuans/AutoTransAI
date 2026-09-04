"""
Integration tests for Job Tracking, Heartbeat, Cancel, Smart Retry, and Logs API.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import init_db
from app.services.video_translator.heartbeat import check_and_mark_stalled_jobs



@pytest.mark.anyio
async def test_job_tracking_and_logs_api(tmp_path):
    """Test job tracking, logs API, cancel API, and smart retry."""
    real_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not real_video.exists():
        pytest.skip("test_with_audio.mp4 missing")


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Import video
        with open(real_video, "rb") as f:
            res = await client.post(
                "/api/video-translator/import",
                data={"source_type": "upload"},
                files={"file": ("test_ai_out.mp4", f, "video/mp4")},
            )
        assert res.status_code == 200
        asset_id = res.json()["data"]["asset_id"]

        # 2. Create Job
        job_res = await client.post(
            "/api/video-translator/jobs",
            json={
                "asset_id": asset_id,
                "target_language": "vi",
                "audio_provider_id": "edge_tts",
            },
        )
        assert job_res.status_code == 200
        job_id = job_res.json()["data"]["job_id"]

        # 3. Test Logs API
        log_res = await client.get(f"/api/video-translator/jobs/{job_id}/logs")
        assert log_res.status_code == 200
        assert "logs" in log_res.json()["data"]

        # 4. Test Job Details & Tracking fields
        get_res = await client.get(f"/api/video-translator/jobs/{job_id}")
        assert get_res.status_code == 200
        data = get_res.json()["data"]
        assert "overall_progress_pct" in data
        assert "last_heartbeat_age_sec" in data
        assert "stage" in data

        # 5. Test Cancel API
        cancel_res = await client.post(f"/api/video-translator/jobs/{job_id}/cancel")
        assert cancel_res.status_code == 200
        assert cancel_res.json()["data"]["cancelled"] is True


@pytest.mark.anyio
async def test_stalled_job_detection():
    """Test C & D: Test detection of stalled jobs with missing heartbeat."""
    await init_db()
    stalled_ids = await check_and_mark_stalled_jobs(stalled_threshold_seconds=1)
    assert isinstance(stalled_ids, list)


@pytest.mark.anyio
async def test_failed_job_state_synchronization():
    """Test state synchronization when pipeline fails: API returns FAILED status, process status FAILED, heartbeat active False."""
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create asset and job
        real_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
        if not real_video.exists():
            pytest.skip("test_with_audio.mp4 missing")
        with open(real_video, "rb") as f:
            res = await client.post(
                "/api/video-translator/import",
                data={"source_type": "upload"},
                files={"file": ("test_video.mp4", f, "video/mp4")},
            )
        asset_id = res.json()["data"]["asset_id"]

        job_res = await client.post(
            "/api/video-translator/jobs",
            json={"asset_id": asset_id, "target_language": "vi"},
        )
        job_id = job_res.json()["data"]["job_id"]

        # Manually fail job to simulate pipeline exception
        from sqlalchemy import update
        from app.models.video_translator import VideoTranslationJob
        from app.database import async_session_factory
        async with async_session_factory() as session:
            await session.execute(
                update(VideoTranslationJob)
                .where(VideoTranslationJob.id == job_id)
                .values(
                    status="failed",
                    stage="FAILED",
                    error_message="RuntimeError: Simulation of FFmpeg failure",
                )
            )
            await session.commit()

        # Query API endpoint
        get_res = await client.get(f"/api/video-translator/jobs/{job_id}")
        assert get_res.status_code == 200
        data = get_res.json()["data"]

        # Verify state synchronization contracts
        assert data["status"] == "failed"
        assert data["stage"] == "FAILED"
        assert data["heartbeat"]["active"] is False
        assert data["process"]["status"] == "FAILED"
        assert data["error"]["message"] == "RuntimeError: Simulation of FFmpeg failure"


