"""
Unit tests for Settings Studio, AI Provider Management, Key Masking, and Gemini STT Policy.
"""

import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base
from app.services.settings_service import SettingsService
from app.services.key_manager import KeyManager, KeyEntry
from app.services.video_translator.translator_service import speech_to_text_and_detect_language


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_settings_seeding_and_crud(async_db: AsyncSession):
    # 1. Seed defaults
    await SettingsService.ensure_defaults_seeded(async_db)

    # 2. Get settings
    settings_data = await SettingsService.get_all_settings(async_db)
    assert "storage_provider" in settings_data
    assert settings_data["max_concurrency"] == "2"

    # 3. Update settings
    updated = await SettingsService.update_settings(async_db, {"max_concurrency": "4", "custom_key": "test_val"})
    assert updated["max_concurrency"] == "4"
    assert updated["custom_key"] == "test_val"


@pytest.mark.asyncio
async def test_ai_function_configs_and_eligibility(async_db: AsyncSession):
    await SettingsService.ensure_defaults_seeded(async_db)

    # List functions
    funcs = await SettingsService.get_function_configs(async_db)
    assert len(funcs) >= 5

    stt_fn = next(f for f in funcs if f["function_id"] == "stt")
    assert stt_fn["primary_provider_id"] == "gemini"
    assert stt_fn["fallback_enabled"] is False

    # Check eligible providers
    eligible = await SettingsService.get_eligible_providers_for_function(async_db, "stt")
    provider_ids = [p["id"] for p in eligible]
    assert "gemini" in provider_ids

    # Update STT function config
    updated = await SettingsService.update_function_config(
        async_db, "stt", {"model_id": "gemini-2.0-flash", "fallback_enabled": False}
    )
    assert updated["model_id"] == "gemini-2.0-flash"
    assert updated["fallback_enabled"] is False


@pytest.mark.asyncio
async def test_ai_models_and_custom_model(async_db: AsyncSession):
    await SettingsService.ensure_defaults_seeded(async_db)

    models = await SettingsService.get_models(async_db, provider_id="gemini")
    assert len(models) >= 1
    assert any(m["id"] == "gemini-2.0-flash" for m in models)

    # Add custom model
    new_model = await SettingsService.add_custom_model(
        async_db,
        {
            "id": "custom-gemini-v1",
            "provider_id": "gemini",
            "model_name": "Custom Fine-tuned Gemini",
            "capabilities": ["LLM", "TRANSLATION"],
        },
    )
    assert new_model["id"] == "custom-gemini-v1"
    assert new_model["is_custom"] is True

    # Update model
    updated_model = await SettingsService.update_model(
        async_db,
        "custom-gemini-v1",
        {
            "model_name": "Updated Gemini Fine-tuned Model",
            "capabilities": ["LLM", "TRANSLATION", "STT"],
        },
    )
    assert updated_model["model_name"] == "Updated Gemini Fine-tuned Model"
    assert "STT" in updated_model["capabilities"]

    # Delete model
    del_res = await SettingsService.delete_model(async_db, "custom-gemini-v1")
    assert del_res is True

    # Verify deleted
    all_gemini = await SettingsService.get_models(async_db, provider_id="gemini")
    assert not any(m["id"] == "custom-gemini-v1" for m in all_gemini)

    # Delete default system model gemini-2.0-flash
    del_sys_res = await SettingsService.delete_model(async_db, "gemini-2.0-flash")
    assert del_sys_res is True

    # Re-run ensure_defaults_seeded to verify it does NOT re-insert deleted model
    await SettingsService.ensure_defaults_seeded(async_db)
    models_after_seed = await SettingsService.get_models(async_db, provider_id="gemini")
    assert not any(m["id"] == "gemini-2.0-flash" for m in models_after_seed)



@pytest.mark.asyncio
async def test_social_accounts_crud(async_db: AsyncSession):
    # Add social account
    acc = await SettingsService.add_social_account(
        async_db,
        {
            "platform": "youtube",
            "account_name": "My Official Channel",
            "channel_id": "UC1234567890",
        },
    )
    assert acc["platform"] == "youtube"

    accs = await SettingsService.get_social_accounts(async_db)
    assert len(accs) == 1

    # Delete social account
    deleted = await SettingsService.delete_social_account(async_db, acc["id"])
    assert deleted is True

    accs_after = await SettingsService.get_social_accounts(async_db)
    assert len(accs_after) == 0


def test_key_masking():
    entry = KeyEntry(key_id="k1", provider_id="gemini", api_key="AIzaSyA1b2C3d4E5f6G7h8I9j0K")
    masked_g = entry.masked_key
    assert masked_g.startswith("AIza")
    assert " secrecy " not in masked_g
    assert "-***-" in masked_g

    # Ensure to_dict excludes raw api_key by default
    d = entry.to_dict(include_raw_key=False)
    assert "api_key" not in d
    assert "masked_key" in d


@pytest.mark.asyncio
async def test_gemini_stt_failure_policy_no_whisper_call(tmp_path: Path):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

    with patch("app.services.video_translator.translator_service.probe_duration_async", return_value=10.0), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_gemini", side_effect=RuntimeError("Gemini Quota Exceeded")), \
         patch("app.services.video_translator.translator_service.transcribe_audio_with_whisper") as mock_whisper:

        with pytest.raises(RuntimeError) as exc_info:
            await speech_to_text_and_detect_language(audio_file, job_id="TEST-VT-JOB")

        assert "STT FAILED" in str(exc_info.value)
        # Verify Whisper fallback was NOT called because fallback is disabled by default
        mock_whisper.assert_not_called()
