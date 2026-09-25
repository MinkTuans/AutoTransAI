"""
Unit tests for Character Voice Review API validation rules:
- Authoritative backend validation of TTS provider registration
- Voice existence and provider matching
- Target language compatibility
- Character gender compatibility
- Rejection (HTTP 400) on invalid updates
- Validation endpoint reporting issues on invalid mappings
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.api.routes.video_translator import (
    validate_voice_assignment,
    validate_character_voice_review,
    update_character_voice_review,
    CharacterVoiceReviewUpdate,
    CharacterVoiceEdit,
)
from app.models.video_translator import TranslationJobStatus


# =========================================================================
# Unit tests for validate_voice_assignment()
# =========================================================================

@pytest.mark.asyncio
async def test_validate_voice_assignment_valid_edge_tts():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="vi-VN-HoaiMyNeural",
        target_language="vi",
        character_gender="female",
    )
    assert err is None


@pytest.mark.asyncio
async def test_validate_voice_assignment_valid_edge_tts_male():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="vi-VN-NamMinhNeural",
        target_language="vi",
        character_gender="male",
    )
    assert err is None


@pytest.mark.asyncio
async def test_validate_voice_assignment_invalid_provider():
    err = await validate_voice_assignment(
        provider_id="non_existent_provider_xyz",
        voice_id="vi-VN-HoaiMyNeural",
        target_language="vi",
        character_gender="female",
    )
    assert err is not None
    assert err["reason"] == "invalid_provider"
    assert "non_existent_provider_xyz" in err["message"]


@pytest.mark.asyncio
async def test_validate_voice_assignment_invalid_voice():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="completely-invalid-voice-id",
        target_language="vi",
        character_gender="female",
    )
    assert err is not None
    assert err["reason"] == "invalid_voice"
    assert "completely-invalid-voice-id" in err["message"]


@pytest.mark.asyncio
async def test_validate_voice_assignment_language_mismatch():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="vi-VN-HoaiMyNeural",
        target_language="en",
        character_gender="female",
    )
    assert err is not None
    assert err["reason"] == "target_language_mismatch"


@pytest.mark.asyncio
async def test_validate_voice_assignment_gender_mismatch():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="vi-VN-HoaiMyNeural",
        target_language="vi",
        character_gender="male",
    )
    assert err is not None
    assert err["reason"] == "gender_mismatch"


@pytest.mark.asyncio
async def test_validate_voice_assignment_gender_unresolved():
    err = await validate_voice_assignment(
        provider_id="edge_tts",
        voice_id="vi-VN-HoaiMyNeural",
        target_language="vi",
        character_gender="unknown",
    )
    assert err is not None
    assert err["reason"] == "gender_unresolved"


@pytest.mark.asyncio
async def test_validate_voice_assignment_google_cloud_tts():
    err = await validate_voice_assignment(
        provider_id="google_cloud_tts",
        voice_id="vi-VN-Standard-A",
        target_language="vi",
        character_gender="female",
    )
    assert err is None


@pytest.mark.asyncio
async def test_validate_voice_assignment_elevenlabs():
    err = await validate_voice_assignment(
        provider_id="elevenlabs",
        voice_id="21m00Tcm4TlvDq8ikWAM",
        target_language="en",
        character_gender="female",
    )
    assert err is None


# =========================================================================
# Integration / API route tests for update_character_voice_review
# =========================================================================

@pytest.mark.asyncio
async def test_update_review_rejects_invalid_provider():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-val-001"
    mock_job.target_language = "vi"
    mock_job.project_id = "proj-001"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value

    mock_exec = MagicMock()
    mock_exec.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_exec

    payload = CharacterVoiceReviewUpdate(
        mappings=[
            CharacterVoiceEdit(
                segment_id=1,
                speaker_id="spk_1",
                character_id="c1",
                gender="female",
                voice_provider="fake_provider_tts",
                voice_id="vi-VN-HoaiMyNeural",
            )
        ]
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_character_voice_review(mock_job.id, payload, mock_session)
    assert exc_info.value.status_code == 400
    assert "fake_provider_tts" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_review_rejects_gender_mismatch():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-val-002"
    mock_job.target_language = "vi"
    mock_job.project_id = "proj-002"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value

    mock_exec = MagicMock()
    mock_exec.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_exec

    # User tries to assign female voice HoaiMy to male character
    payload = CharacterVoiceReviewUpdate(
        mappings=[
            CharacterVoiceEdit(
                segment_id=1,
                speaker_id="spk_1",
                character_id="c1",
                gender="male",
                voice_provider="edge_tts",
                voice_id="vi-VN-HoaiMyNeural",
            )
        ]
    )
    with pytest.raises(HTTPException) as exc_info:
        await update_character_voice_review(mock_job.id, payload, mock_session)
    assert exc_info.value.status_code == 400
    assert "gender_mismatch" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_review_accepts_valid_mapping():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-val-003"
    mock_job.target_language = "vi"
    mock_job.project_id = "proj-003"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value

    mock_exec = MagicMock()
    mock_exec.scalar_one_or_none.return_value = mock_job
    mock_exec.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_exec

    payload = CharacterVoiceReviewUpdate(
        mappings=[
            CharacterVoiceEdit(
                segment_id=1,
                speaker_id="spk_1",
                character_id="c1",
                gender="female",
                voice_provider="edge_tts",
                voice_id="vi-VN-HoaiMyNeural",
            )
        ]
    )
    with patch("app.api.routes.video_translator._character_voice_review_data", return_value={"job_id": mock_job.id, "segments": []}):
        res = await update_character_voice_review(mock_job.id, payload, mock_session)
        assert res["success"] is True


# =========================================================================
# Integration / API route tests for validate_character_voice_review
# =========================================================================

@pytest.mark.asyncio
async def test_validate_review_detects_gender_and_language_issues():
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-val-004"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value

    # Segment with language mismatch
    review_data = {
        "job_id": mock_job.id,
        "target_language": "vi",
        "status": "needs_review",
        "segments": [
            {
                "id": 1,
                "segment_number": 1,
                "character_id": "c1",
                "character_name": "Nhân vật 1",
                "gender": "female",
                "voice_provider": "edge_tts",
                "voice_id": "en-US-AriaNeural",
                "original_start": 0.0,
                "original_end": 2.0,
                "tts_duration": 2.0,
            }
        ],
    }

    with patch("app.api.routes.video_translator._character_voice_review_data", return_value=review_data):
        res = await validate_character_voice_review(mock_job.id, mock_session)
        assert res["data"]["passed"] is False
        assert len(res["data"]["issues"]) > 0
        assert res["data"]["issues"][0]["reason"] == "target_language_mismatch"


@pytest.mark.asyncio
async def test_validate_review_accepts_selected_openrouter_voice_with_session():
    from app.models import CatalogModel
    from app.models.settings import AIFunctionConfig

    session = AsyncMock()
    async def get(cls, key):
        if cls is AIFunctionConfig:
            return AIFunctionConfig(function_id="tts", primary_provider_id="openrouter",
                                    model_id="catalog-id")
        if cls is CatalogModel:
            return CatalogModel(id="catalog-id", provider_id="openrouter", source="discovered",
                                enabled=True, remote_model_id="openai/tts-model",
                                discovery_metadata={"supported_voices": ["alloy"],
                                                    "architecture": {"input_modalities": ["text"],
                                                                     "output_modalities": ["speech"]}})
    session.get.side_effect = get
    review_data = {"job_id": "job", "target_language": "en-US", "status": "needs_review",
                   "segments": [{"id": 1, "segment_number": 1, "character_id": "c1",
                                 "gender": "female", "voice_provider": "openrouter",
                                 "voice_id": "alloy", "original_start": 0.0,
                                 "original_end": 2.0, "tts_duration": 2.0}]}
    with patch("app.api.routes.video_translator._character_voice_review_data", return_value=review_data):
        result = await validate_character_voice_review("job", session)
    assert result["data"]["passed"] is True
    assert result["data"]["issues"] == []
