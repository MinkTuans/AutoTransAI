"""
Unit & Integration tests for Settings API, AI Function configurations, and Key Management.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app import config as app_config
from app import database
from app.services import key_manager
from app.services.key_manager import get_key_manager, KeyStatus
from app.services.settings_service import SettingsService


@pytest_asyncio.fixture(scope="module", autouse=True)
async def initialized_settings_database(tmp_path_factory):
    """Keep this legacy API module's writes out of every other test."""
    root = tmp_path_factory.mktemp("settings-api")
    engine = create_async_engine(f"sqlite+aiosqlite:///{root / 'settings.sqlite'}")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    patch = pytest.MonkeyPatch()
    patch.setattr(database, "engine", engine)
    patch.setattr(database, "async_session_factory", sessions)
    patch.setattr(key_manager, "STORAGE_FILE", root / "api_keys.json")
    patch.setattr(key_manager.KeyManager, "_instance", None)
    module_env = root / ".env"
    module_env.write_text("", encoding="utf-8")
    patch.setattr(app_config, "ENV_FILE_PATH", module_env)
    patch.setattr(key_manager, "settings", app_config.get_settings())
    try:
        await database.init_db()
        async with sessions() as session:
            await SettingsService.ensure_defaults_seeded(session)
        yield
    finally:
        patch.undo()
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_settings_defaults():
    """Verify system settings returns seeded defaults."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/settings")
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        data = json_data["data"]
        assert "storage_provider" in data
        assert "max_concurrency" in data
        assert "default_target_language" in data


@pytest.mark.asyncio
async def test_update_settings():
    """Verify updating system settings persists key-value changes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"settings": {"max_concurrency": "4", "default_target_language": "en"}}
        res = await client.put("/api/settings", json=payload)
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        assert json_data["data"]["max_concurrency"] == "4"
        assert json_data["data"]["default_target_language"] == "en"


@pytest.mark.asyncio
async def test_ai_functions_eligible_providers():
    """Verify AI function configuration returns eligible compatible providers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/settings/functions")
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        functions = json_data["data"]
        assert len(functions) >= 4

        # STT function check
        stt_fn = next(f for f in functions if f["function_id"] == "stt")
        assert stt_fn["capability"] == "STT"
        assert stt_fn["primary_provider_id"] == "gemini"


@pytest.mark.asyncio
async def test_update_ai_function():
    """Verify updating function primary provider and fallback toggle."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"primary_provider_id": "gemini", "fallback_enabled": False}
        res = await client.put("/api/settings/functions/stt", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["primary_provider_id"] == "gemini"
        assert data["fallback_enabled"] is False


@pytest.mark.asyncio
async def test_models_catalog_and_add_custom_model():
    """Verify models catalog listing and custom model addition."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get models
        res = await client.get("/api/settings/models")
        assert res.status_code == 200
        models = res.json()["data"]
        assert len(models) > 0

        # Add custom model
        custom_m = {
            "id": "test-custom-llm-model",
            "provider_id": "gemini",
            "model_name": "Test Custom Model",
            "capabilities": ["LLM", "TRANSLATION"],
        }
        res2 = await client.post("/api/settings/models", json=custom_m)
        assert res2.status_code == 200
        data2 = res2.json()["data"]
        assert data2["id"] == "test-custom-llm-model"
        assert data2["is_custom"] is True


@pytest.mark.asyncio
async def test_social_accounts_crud():
    """Verify social accounts CRUD endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        add_payload = {
            "platform": "youtube",
            "account_name": "Test YouTube Channel",
            "channel_id": "UC_TEST_12345",
        }
        res = await client.post("/api/settings/social-accounts", json=add_payload)
        assert res.status_code == 200
        acc_data = res.json()["data"]
        acc_id = acc_data["id"]
        assert acc_data["platform"] == "youtube"

        # List accounts
        res_list = await client.get("/api/settings/social-accounts")
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) >= 1

        # Delete account
        res_del = await client.delete(f"/api/settings/social-accounts/{acc_id}")
        assert res_del.status_code == 200


@pytest.mark.asyncio
async def test_key_masking_security():
    """Verify API keys are masked and raw secrets are never returned in list endpoints."""
    key_mgr = get_key_manager()
    added_info = await key_mgr.add_key("gemini", "AIzaSySecretTestKey123456789", priority=1)
    keys = await key_mgr.get_keys_for_provider("gemini")
    assert len(keys) > 0
    added_key_id = added_info.key_id if hasattr(added_info, "key_id") else added_info["key_id"]
    target_key = next((k for k in keys if (k.key_id if hasattr(k, "key_id") else k["key_id"]) == added_key_id), keys[-1])
    target_dict = target_key.to_dict() if hasattr(target_key, "to_dict") else target_key
    assert "api_key" not in target_dict or target_dict.get("api_key") != "AIzaSySecretTestKey123456789"
    assert "AIza" in target_dict["masked_key"]
    assert "***" in target_dict["masked_key"]
