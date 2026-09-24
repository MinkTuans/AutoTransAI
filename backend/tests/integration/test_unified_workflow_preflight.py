"""Integration tests for Unified Workflow Pre-flight Check, Project Settings, and Glossary."""

import pytest
import pytest_asyncio
import importlib
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app import database
from app.models.project import Project
from app.services.settings_service import SettingsService


@pytest_asyncio.fixture
async def isolated_preflight_database(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'preflight.sqlite'}")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    patch = pytest.MonkeyPatch()
    patch.setattr(database, "engine", engine)
    patch.setattr(database, "async_session_factory", sessions)
    for name in ("app.services.file_manager", "app.services.storage_service",
                 "app.core.job_logger", "app.api.routes.projects",
                 "app.api.routes.video_translator"):
        module = importlib.import_module(name)
        patch.setattr(module.settings, "DATA_DIR", tmp_path / "data")
        patch.setattr(module.settings, "STORAGE_ROOT", tmp_path / "storage")
    try:
        await database.init_db()
        async with sessions() as session:
            await SettingsService.ensure_defaults_seeded(session)
        yield
    finally:
        patch.undo()
        await engine.dispose()


@pytest.mark.asyncio
async def test_preflight_and_project_settings_flow(isolated_preflight_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a real project via API
        create_res = await client.post("/api/projects", json={
            "title": "Dịch Phim Hoạt Hình Test",
            "description": "Dự án thử nghiệm Pre-flight",
            "workflow_mode": "video_translator",
            "settings_json": {
                "target_language": "vi",
                "audio_provider_id": "edge_tts",
                "llm_provider_id": "gemini",
                "voice_id": "vi-VN-HoaiMyNeural",
            }
        })
        assert create_res.status_code == 200
        proj_data = create_res.json()["data"]
        project_id = proj_data["project_id"]
        assert project_id is not None

        # 2. Get project settings
        get_settings_res = await client.get(f"/api/projects/{project_id}/settings")
        assert get_settings_res.status_code == 200
        assert get_settings_res.json()["data"]["llm_provider_id"] == "gemini"

        # 3. Update project settings
        update_settings_res = await client.post(f"/api/projects/{project_id}/settings", json={
            "watermark_enabled": True,
            "watermark_text": "© AutoTransAI Test",
        })
        assert update_settings_res.status_code == 200
        assert update_settings_res.json()["data"]["watermark_text"] == "© AutoTransAI Test"

        # 4. Run Preflight Check
        preflight_res = await client.post(f"/api/video-translator/projects/{project_id}/workflow/preflight", json={
            "video_url": "https://example.com/sample.mp4",
            "target_language": "vi",
            "audio_provider_id": "edge_tts",
            "llm_provider_id": "gemini",
            "voice_id": "vi-VN-HoaiMyNeural",
            "watermark_enabled": True,
            "watermark_type": "text",
            "watermark_text": "© AutoTransAI Test",
        })
        assert preflight_res.status_code == 200
        pf_data = preflight_res.json()["data"]
        assert "can_start" in pf_data
        assert "checks" in pf_data
        assert len(pf_data["checks"]) > 0

        # 5. Add directly to the single canonical Glossary.
        add_tm_res = await client.post(f"/api/video-translator/projects/{project_id}/glossary", json={
            "source_term": "青云城",
            "translated_term": "Thành Thanh Vân",
            "term_type": "location",
        })
        assert add_tm_res.status_code == 200

        # 6. Read the same Glossary used by translation.
        get_tm_res = await client.get(f"/api/video-translator/projects/{project_id}/glossary")
        assert get_tm_res.status_code == 200
        tm_list = get_tm_res.json()["data"]
        assert len(tm_list) == 1
        assert tm_list[0]["source_term"] == "青云城"
        assert tm_list[0]["translated_term"] == "Thành Thanh Vân"
