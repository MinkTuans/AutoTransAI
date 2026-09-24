"""Integration tests for Unified Workflow Pre-flight Check, Project Settings, and Glossary."""

import pytest
import pytest_asyncio
import importlib
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app import database
from app.models.project import Project
from app.models import APIKey, CatalogModel, KeyModelAccess, Provider
from app.models.settings import AIFunctionConfig, AIModel
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


@pytest.mark.asyncio
@pytest.mark.parametrize('key_enabled,translation_configured', [(True, True), (True, False), (False, True)])
async def test_preflight_uses_ready_canonical_stt_without_legacy_model(
    isolated_preflight_database, monkeypatch, key_enabled, translation_configured,
):
    from app.providers.llm.gemini_provider import GeminiLLMProvider
    from app.providers.audio.edge_tts_provider import EdgeTTSProvider
    from app.services import preflight

    async def forbid_legacy_env_probe(self):
        raise AssertionError('canonical STT preflight must not probe the .env key')

    async def tts_ready(self):
        return True

    monkeypatch.setattr(GeminiLLMProvider, 'validate_configuration', forbid_legacy_env_probe)
    monkeypatch.setattr(EdgeTTSProvider, 'validate_configuration', tts_ready)
    monkeypatch.setattr(preflight, 'is_ffmpeg_installed', lambda: True)
    monkeypatch.setattr(preflight, 'check_storage_writable', lambda project_id: True)
    model_id = '11111111-2222-4333-8444-555555555555'
    key_id = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'
    async with database.async_session_factory.begin() as db:
        await db.execute(delete(AIModel))
        db.add(Provider(id='gemini', name='Gemini', provider_type='llm'))
        await db.flush()
        db.add(CatalogModel(id=model_id, provider_id='gemini', remote_model_id='gemini-synthetic-stt',
                            source='discovered', capability_status='KNOWN', capabilities=['STT', 'TRANSLATION']))
        db.add(APIKey(id=key_id, provider_id='gemini', ciphertext='synthetic-only',
                      fingerprint='a' * 64, masked_key='****', enabled=key_enabled))
        config = await db.get(AIFunctionConfig, 'stt')
        config.primary_provider_id = 'gemini'
        config.model_id = model_id
        if translation_configured:
            translation = await db.get(AIFunctionConfig, 'translation')
            translation.primary_provider_id = 'gemini'
            translation.model_id = model_id
        await db.flush()
        db.add(KeyModelAccess(key_id=key_id, model_id=model_id, provider_id='gemini'))

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        created = await client.post('/api/projects', json={
            'title': 'Canonical STT preflight', 'workflow_mode': 'video_translator',
        })
        assert created.status_code == 200
        project_id = created.json()['data']['project_id']
        response = await client.post(
            f'/api/video-translator/projects/{project_id}/workflow/preflight',
            json={'video_url': 'https://example.invalid/video.mp4', 'llm_provider_id': 'gemini',
                  'audio_provider_id': 'edge_tts', 'voice_id': 'vi-VN-HoaiMyNeural'},
        )
    assert response.status_code == 200
    checks = {item['name']: item for item in response.json()['data']['checks']}
    assert checks['llm_provider_health']['passed'] is key_enabled
    assert checks['llm_provider_health']['required'] is True
    assert checks['llm_provider_health']['category'] == 'critical'
    assert checks['translation_route_available']['passed'] is (key_enabled and translation_configured)
    assert checks['translation_route_available']['required'] is True
    assert checks['translation_route_available']['category'] == 'critical'
    assert response.json()['data']['can_start'] is (key_enabled and translation_configured)
    assert ('translation_route_available' in {
        item['name'] for item in response.json()['data']['blocking_failures']
    }) is not (key_enabled and translation_configured)
    if key_enabled:
        assert 'gemini-synthetic-stt' in checks['llm_provider_health']['description']


@pytest.mark.asyncio
async def test_preflight_requires_stt_default_after_catalog_activation(isolated_preflight_database, monkeypatch):
    from app.providers.llm.gemini_provider import GeminiLLMProvider

    async def legacy_env_probe_would_pass(self):
        return True

    monkeypatch.setattr(GeminiLLMProvider, 'validate_configuration', legacy_env_probe_would_pass)
    async with database.async_session_factory.begin() as db:
        db.add(Provider(id='gemini', name='Gemini', provider_type='llm'))
        await db.flush()
        db.add(CatalogModel(id='11111111-2222-4333-8444-555555555555', provider_id='gemini',
                            remote_model_id='gemini-synthetic-stt', source='discovered',
                            capability_status='KNOWN', capabilities=['STT']))
        config = await db.get(AIFunctionConfig, 'stt')
        config.model_id = ''
        config.primary_provider_id = ''
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        created = await client.post('/api/projects', json={
            'title': 'Missing STT default', 'workflow_mode': 'video_translator',
        })
        assert created.status_code == 200
        project_id = created.json()['data']['project_id']
        response = await client.post(
            f'/api/video-translator/projects/{project_id}/workflow/preflight',
            json={'has_upload_file': True},
        )
    assert response.status_code == 200
    result = response.json()['data']
    check = next(item for item in result['checks'] if item['name'] == 'llm_provider_health')
    assert check['passed'] is False
    assert check['required'] is True
    assert check['category'] == 'critical'
    assert result['can_start'] is False
