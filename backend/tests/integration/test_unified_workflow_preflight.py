"""Integration tests for Unified Workflow Pre-flight Check, Project Settings, and Glossary."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import async_session_factory, init_db
from app.models.project import Project


@pytest.mark.asyncio
async def test_preflight_and_project_settings_flow():
    await init_db()
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
