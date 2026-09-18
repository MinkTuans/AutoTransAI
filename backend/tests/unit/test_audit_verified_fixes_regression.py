"""
Unit regression tests for post-implementation verification audit fixes:
1. Target Language Injection
2. Independent Confirmation Gates
3. Confirmed Character Identity Persistence
4. Unicode Download Headers
5. Async File Copy
"""

import asyncio
import json
import uuid
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from app.models.workflow_engine import CharacterVoiceProfile, SpeakerVoiceMapping, VoicePoolEntry
from app.models.video_translator import VideoTranslationJob, VideoTranslationSegment, TranslationJobStatus
from app.services.video_translator.voice_assignment_service import assign_project_voices
from app.services.video_translator.character_mapping_service import map_and_persist
from app.services.video_source.service import VideoSourceService
from app.config import get_settings

settings = get_settings()


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


# ==============================================================================
# TEST 1 — Target Language Boundary
# ==============================================================================

@pytest.mark.asyncio
async def test_target_language_boundary_english_vs_vietnamese(async_db: AsyncSession):
    project_id = f"test-lang-{uuid.uuid4().hex[:8]}"

    # Setup pool entries
    async_db.add(VoicePoolEntry(id=str(uuid.uuid4()), provider="edge_tts", language="en-US", gender="male", voice_id="en-US-GuyNeural", display_name="Guy"))
    async_db.add(VoicePoolEntry(id=str(uuid.uuid4()), provider="edge_tts", language="en-US", gender="female", voice_id="en-US-AriaNeural", display_name="Aria"))
    async_db.add(VoicePoolEntry(id=str(uuid.uuid4()), provider="edge_tts", language="vi-VN", gender="male", voice_id="vi-VN-NamMinhNeural", display_name="NamMinh"))
    async_db.add(VoicePoolEntry(id=str(uuid.uuid4()), provider="edge_tts", language="vi-VN", gender="female", voice_id="vi-VN-HoaiMyNeural", display_name="HoaiMy"))
    await async_db.flush()

    segments = [
        {"character_id": "char-m", "original_start": 0.0, "original_end": 2.0, "speaker_id": "SPEAKER_00"},
        {"character_id": "char-f", "original_start": 3.0, "original_end": 5.0, "speaker_id": "SPEAKER_01"},
    ]
    # Add profiles for male & female
    async_db.add(CharacterVoiceProfile(id=str(uuid.uuid4()), project_id=project_id, character_id="char-m", name="Man", gender="male", role="main"))
    async_db.add(CharacterVoiceProfile(id=str(uuid.uuid4()), project_id=project_id, character_id="char-f", name="Woman", gender="female", role="main"))
    await async_db.flush()

    # 1. Test en-US assignment
    res_en = await assign_project_voices(async_db, project_id, segments, target_language="en-US")
    for cid, assign in res_en.assignments.items():
        v_id = assign["voice_id"]
        assert v_id.startswith("en-US-"), f"Expected en-US voice for {cid}, got {v_id}"
        assert not v_id.startswith("vi-VN-")

    # 2. Test vi-VN assignment
    res_vi = await assign_project_voices(async_db, project_id, segments, target_language="vi-VN")
    for cid, assign in res_vi.assignments.items():
        v_id = assign["voice_id"]
        assert v_id.startswith("vi-VN-"), f"Expected vi-VN voice for {cid}, got {v_id}"
        assert not v_id.startswith("en-US-")


# ==============================================================================
# TEST 2 — Independent Confirmation Gates
# ==============================================================================

@pytest.mark.asyncio
async def test_independent_confirmation_gates(async_db: AsyncSession):
    project_id = f"test-indep-{uuid.uuid4().hex[:8]}"
    job_id = f"job-indep-{uuid.uuid4().hex[:8]}"

    # Add unconfirmed profile
    async_db.add(CharacterVoiceProfile(
        id=str(uuid.uuid4()),
        project_id=project_id,
        character_id="char-1",
        name="Hero",
        gender="male",
        voice_provider="edge_tts",
        voice_id="vi-VN-NamMinhNeural",
        confirmed_by_user=False
    ))

    # Add Job with auto_confirm_translation=True, auto_confirm_voice=False
    job = VideoTranslationJob(
        id=job_id,
        project_id=project_id,
        asset_id="asset-1",
        status=TranslationJobStatus.SEGMENT_EDITING.value,
        stage="TRANSLATE",
        auto_confirm_translation=True,
        auto_confirm_voice=False,
        settings_snapshot_json=json.dumps({"auto_confirm_translation": True, "auto_confirm_voice": False})
    )
    async_db.add(job)

    async_db.add(VideoTranslationSegment(
        job_id=job_id,
        segment_number=1,
        start_time=0.0,
        end_time=2.0,
        original_text="Hello",
        translated_text="Xin chào",
        status="translated"
    ))
    await async_db.flush()

    from app.api.routes.video_translator import auto_confirm_and_start_render_if_needed

    with patch("app.api.routes.video_translator.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = async_db

        res = await auto_confirm_and_start_render_if_needed(job_id)
        # Translation confirmation should return False (meaning render pipeline was NOT started)
        assert res is False

        await async_db.refresh(job)
        # Job must be in NEEDS_REVIEW / CHARACTER_VOICE_REVIEW state
        assert job.status == TranslationJobStatus.NEEDS_REVIEW.value
        assert job.stage == "CHARACTER_VOICE_REVIEW"

        # Translation segment text MUST be auto-confirmed
        seg = (await async_db.execute(select(VideoTranslationSegment).where(VideoTranslationSegment.job_id == job_id))).scalar_one()
        assert seg.status == "confirmed"

    # Reverse direction: auto_confirm_translation=False, auto_confirm_voice=True
    job_id_rev = f"job-rev-{uuid.uuid4().hex[:8]}"
    job_rev = VideoTranslationJob(
        id=job_id_rev,
        project_id=project_id,
        asset_id="asset-1",
        status=TranslationJobStatus.SEGMENT_EDITING.value,
        stage="TRANSLATE",
        auto_confirm_translation=False,
        auto_confirm_voice=True,
        settings_snapshot_json=json.dumps({"auto_confirm_translation": False, "auto_confirm_voice": True})
    )
    async_db.add(job_rev)
    await async_db.flush()

    with patch("app.api.routes.video_translator.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__.return_value = async_db
        res_rev = await auto_confirm_and_start_render_if_needed(job_id_rev)
        assert res_rev is False
        await async_db.refresh(job_rev)
        # Should remain in SEGMENT_EDITING state awaiting manual text confirmation
        assert job_rev.status == TranslationJobStatus.SEGMENT_EDITING.value


# ==============================================================================
# TEST 3 — Confirmed Character Persistence
# ==============================================================================

@pytest.mark.asyncio
async def test_confirmed_character_identity_persistence(async_db: AsyncSession):
    project_id = f"test-persist-{uuid.uuid4().hex[:8]}"
    speaker_id = "SPEAKER_00"

    # Step 1: Initial mapping run
    mock_llm1 = AsyncMock()
    mock_llm1.generate_text.return_value = json.dumps({
        "characters": [
            {"character_id": "c-orig", "name": "Standard Hero", "gender": "male", "role": "main", "speaker_ids": [speaker_id], "confidence": 0.95}
        ]
    })
    segments1 = [{"speaker_id": speaker_id, "text": "Hello world", "translated_text": "Xin chào"}]

    res1 = await map_and_persist(async_db, project_id, segments1, mock_llm1)
    assigned_cid = res1.by_speaker[speaker_id]["character_id"]
    assert assigned_cid is not None

    # Step 2: Confirm profile in DB
    prof = (await async_db.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id, CharacterVoiceProfile.character_id == assigned_cid))).scalar_one()
    prof.confirmed_by_user = True
    prof.voice_provider = "edge_tts"
    prof.voice_id = "en-US-GuyNeural"
    prof.name = "User Confirmed Name"
    await async_db.flush()

    # Step 3: Second mapping run with different LLM naming ("Hero Variant V2")
    mock_llm2 = AsyncMock()
    mock_llm2.generate_text.return_value = json.dumps({
        "characters": [
            {"character_id": "different-llm-id", "name": "Hero Variant V2", "gender": "male", "role": "main", "speaker_ids": [speaker_id], "confidence": 0.99}
        ]
    })
    res2 = await map_and_persist(async_db, project_id, segments1, mock_llm2)

    # Step 4: Assert same character_id is reused and confirmed profile data is preserved intact
    reused_cid = res2.by_speaker[speaker_id]["character_id"]
    assert reused_cid == assigned_cid

    prof_after = (await async_db.execute(select(CharacterVoiceProfile).where(CharacterVoiceProfile.project_id == project_id, CharacterVoiceProfile.character_id == assigned_cid))).scalar_one()
    assert prof_after.confirmed_by_user is True
    assert prof_after.name == "User Confirmed Name"
    assert prof_after.voice_id == "en-US-GuyNeural"


# ==============================================================================
# TEST 4 — Unicode Download Headers
# ==============================================================================

def test_unicode_filename_download_endpoint():
    dummy_dir = settings.DATA_DIR
    dummy_dir.mkdir(parents=True, exist_ok=True)
    unicode_file = dummy_dir / "test_unicode_source.mp4"
    unicode_file.write_bytes(b"dummy video content 12345")

    client = TestClient(app)

    chinese_filename = "未日临先锋圣母_哔哩哔哩_bilibili.mp4"
    vietnamese_filename = "Bản_dịch_tiếng_Việt_gốc.mp4"

    # Test Chinese filename download
    resp_zh = client.get(f"/api/storage/download?path={unicode_file.name}&filename={chinese_filename}")
    assert resp_zh.status_code == 200
    assert len(resp_zh.content) > 0
    assert "content-disposition" in resp_zh.headers

    # Test Vietnamese filename download
    resp_vi = client.get(f"/api/storage/download?path={unicode_file.name}&filename={vietnamese_filename}")
    assert resp_vi.status_code == 200
    assert len(resp_vi.content) > 0

    unicode_file.unlink(missing_ok=True)


# ==============================================================================
# TEST 5 — Async File Copy
# ==============================================================================

@pytest.mark.asyncio
async def test_async_file_copy_non_blocking(tmp_path):
    src = tmp_path / "source.mp4"
    src.write_bytes(b"sample video bytes" * 100)
    dest_dir = tmp_path / "dest"

    service = VideoSourceService()

    with patch("app.services.video_source.service.get_video_metadata_async", new_callable=AsyncMock) as mock_meta:
        mock_meta.return_value = {
            "duration": 10.0,
            "width": 1920,
            "height": 1080,
            "format": "mp4",
            "has_audio": True,
        }
        res = await service.import_uploaded_file(src, "original_file.mp4", dest_dir)

        assert res["duration"] == 10.0
        copied_file = Path(res["local_path"])
        assert copied_file.exists()
        assert copied_file.stat().st_size == src.stat().st_size
