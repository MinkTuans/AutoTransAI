"""
Integration tests for Video Translator API routes and pipeline.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.video_translator import VideoAsset, VideoTranslationJob


@pytest.mark.anyio
async def test_check_url_api_ssrf_blocked():
    """Test 11 API: SSRF URL check endpoint blocks internal IP."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/video-translator/check-url", json={"url": "http://127.0.0.1/secret.mp4"})
        assert res.status_code == 400
        data = res.json()
        assert "detail" in data
        assert "❌" in data["detail"] or "SSRF" in data["detail"] or "chặn" in data["detail"]


@pytest.mark.anyio
async def test_check_url_api_invalid():
    """Test 4 API: Invalid URL format check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/video-translator/check-url", json={"url": "invalid_url_string"})
        assert res.status_code == 400


@pytest.mark.anyio
async def test_upload_local_video_and_pipeline_flow(tmp_path):
    """Test 1 & Test 12: Import uploaded video file and verify job pipeline creation."""
    real_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not real_video.exists():
        test_video = tmp_path / "test_sample.mp4"
        test_video.write_bytes(b"\x00" * 1024)
    else:
        test_video = real_video


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

        # 1. Import local video
        with open(test_video, "rb") as f:
            res = await client.post(
                "/api/video-translator/import",
                data={"source_type": "upload"},
                files={"file": ("test_sample.mp4", f, "video/mp4")},
            )
        assert res.status_code == 200
        data = res.json()["data"]
        asset_id = data["asset_id"]
        assert asset_id is not None

        # 2. Create Job
        job_res = await client.post(
            "/api/video-translator/jobs",
            json={
                "asset_id": asset_id,
                "target_language": "vi",
                "audio_provider_id": "edge_tts",
                "original_audio_mode": "mute",
            },
        )
        assert job_res.status_code == 200
        job_id = job_res.json()["data"]["job_id"]

        # 3. Fetch Job detail
        get_res = await client.get(f"/api/video-translator/jobs/{job_id}")
        assert get_res.status_code == 200
        job_data = get_res.json()["data"]
        assert job_data["job_id"] == job_id
        assert job_data["target_language"] == "vi"
