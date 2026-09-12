"""
Integration tests for Video Translator API routes and pipeline.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import init_db
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
        pytest.skip("test_with_audio.mp4 missing")
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
        assert job_data.get("project_id") is not None


@pytest.mark.anyio
async def test_workflow_start_with_invalid_project_id_returns_404():
    """Verify that calling workflow/start with 'default_project' returns 404, not 500."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/video-translator/projects/default_project/workflow/start", json={})
        assert res.status_code == 404
        data = res.json()
        assert data["detail"]["error"] == "PROJECT_NOT_FOUND"


@pytest.mark.anyio
async def test_create_job_auto_creates_project_and_starts_workflow(tmp_path):
    """Verify that creating a job auto-creates a real Project and workflow/start succeeds."""
    real_video = Path(__file__).parent.parent.parent / "test_with_audio.mp4"
    if not real_video.exists():
        pytest.skip("test_with_audio.mp4 missing")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Import
        with open(real_video, "rb") as f:
            imp_res = await client.post(
                "/api/video-translator/import",
                data={"source_type": "upload"},
                files={"file": ("test_sample.mp4", f, "video/mp4")},
            )
        assert imp_res.status_code == 200
        asset_id = imp_res.json()["data"]["asset_id"]

        # 2. Create Job
        job_res = await client.post(
            "/api/video-translator/jobs",
            json={"asset_id": asset_id, "target_language": "vi"},
        )
        assert job_res.status_code == 200
        project_id = job_res.json()["data"]["project_id"]
        assert project_id is not None
        assert project_id != "default_project"

        # 3. Start 6-Stage Workflow with real Project ID
        wf_res = await client.post(
            f"/api/video-translator/projects/{project_id}/workflow/start",
            json={"target_language": "vi"},
        )
        assert wf_res.status_code == 200
        assert wf_res.json()["success"] is True
        assert wf_res.json()["data"]["status"] == "running"

        # 4. Fetch Workflow Status
        st_res = await client.get(f"/api/video-translator/projects/{project_id}/workflow-status")
        assert st_res.status_code == 200
        st_data = st_res.json()["data"]
        assert st_data["execution_id"] is not None
        assert st_data["status"] in ["running", "completed"]


@pytest.mark.anyio
async def test_list_projects_pagination():
    """Verify GET /api/projects supports 8-items-per-page pagination metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Unpaginated request
        res1 = await client.get("/api/projects")
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["success"] is True
        assert isinstance(data1["data"], list)
        assert "total" in data1

        # Paginated request (8 per page)
        res2 = await client.get("/api/projects?page=1&page_size=8")
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["success"] is True
        assert len(data2["data"]) <= 8
        assert data2["page"] == 1
        assert data2["page_size"] == 8
        assert "total_pages" in data2


@pytest.mark.anyio
async def test_update_project_title_api():
    """Test POST /api/projects then PATCH /api/projects/{project_id} to rename a project."""
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

        # 1. Create a project
        create_res = await client.post("/api/projects", json={"title": "Test Title Before Edit", "description": "Test"})
        assert create_res.status_code == 200
        res_json = create_res.json()
        assert res_json["success"] is True
        created_data = res_json["data"]
        project_id = created_data["id"]
        assert created_data["title"] == "Test Title Before Edit"

        # 2. Update title via PATCH
        new_title = "Tên Dự Án Mới Update Test"
        patch_res = await client.patch(f"/api/projects/{project_id}", json={"title": new_title})
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["title"] == new_title


        # 3. Verify GET returns updated title
        get_res = await client.get(f"/api/projects/{project_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["title"] == new_title






