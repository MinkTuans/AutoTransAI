import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import json

from app.services.video_translator.visual_gender_service import (
    detect_speakers_gender,
    get_speaker_sample_timestamps,
    parse_gender_response,
    create_contact_sheet,
    VISUAL_GENDER_PROMPT,
)
from app.services.video_translator.character_mapping_service import map_and_persist
from app.models.workflow_engine import CharacterVoiceProfile
from app.database import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import pytest_asyncio


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
async def test_detect_speakers_gender_logic(tmp_path):
    """
    Standard test: 4 frames extracted per speaker, 1 contact sheet per speaker,
    and 1 Vision API call per speaker.
    """
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()

    segments = [
        {"speaker_id": "Speaker 1", "start_time": 0.0, "end_time": 2.0},
        {"speaker_id": "Speaker 1", "start_time": 5.0, "end_time": 10.0},
        {"speaker_id": "Speaker 2", "start_time": 12.0, "end_time": 14.0},
        {"speaker_id": "UNRESOLVED_0001", "start_time": 15.0, "end_time": 16.0},
    ]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    async def mock_detect(image_path, **kwargs):
        if "Speaker 1" in image_path:
            return "male"
        elif "Speaker 2" in image_path:
            return "female"
        return "unknown"

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract) as extract_mock:
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", side_effect=mock_detect) as detect_mock:
            results = await detect_speakers_gender(str(dummy_video), segments)

            assert "Speaker 1" in results
            assert results["Speaker 1"] == "male"
            assert "Speaker 2" in results
            assert results["Speaker 2"] == "female"
            assert "UNRESOLVED_0001" not in results

            # 4 frames extracted per valid speaker (Speaker 1: 4, Speaker 2: 4 -> total 8)
            assert len(extract_mock.call_args_list) == 8

            # Exactly ONE Vision API call per speaker (2 speakers -> 2 calls, NOT 8 calls)
            assert len(detect_mock.call_args_list) == 2


@pytest.mark.asyncio
async def test_detect_speakers_gender_missing_video():
    results = await detect_speakers_gender("invalid_path.mp4", [{"speaker_id": "Speaker 1"}])
    assert results == {}


# ── REQUIRED TEST CASES 1 THROUGH 12 ──────────────────────────────────────────

def test_case_5_vision_returns_female():
    """Case 5: Vision returns 'FEMALE' -> 'female'."""
    assert parse_gender_response("FEMALE") == "female"
    assert parse_gender_response("female") == "female"
    assert parse_gender_response("  FEMALE  \n") == "female"


def test_case_6_vision_returns_male():
    """Case 6: Vision returns 'MALE' -> 'male'."""
    assert parse_gender_response("MALE") == "male"
    assert parse_gender_response("male") == "male"
    assert parse_gender_response("  MALE  \n") == "male"


def test_case_7_female_male_substring_regression():
    """
    Case 7: Vision returns 'The character is FEMALE.' -> 'female'.
    Regression test: 'MALE' is a substring of 'FEMALE', parser must NEVER confuse them.
    """
    assert parse_gender_response("The character is FEMALE.") == "female"
    assert parse_gender_response("Gender: FEMALE") == "female"
    assert parse_gender_response("Result: female") == "female"
    assert parse_gender_response("The person is MALE.") == "male"
    assert parse_gender_response("Gender: MALE") == "male"
    # Vietnamese support
    assert parse_gender_response("Nhân vật NỮ") == "female"
    assert parse_gender_response("Nhân vật NAM") == "male"


@pytest.mark.asyncio
async def test_case_1_4_frames_male(tmp_path):
    """Case 1: 4 frames indicate male speaker -> result male."""
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()
    segments = [{"speaker_id": "Speaker 1", "start_time": 1.0, "end_time": 8.0}]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract):
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", return_value="male"):
            results = await detect_speakers_gender(str(dummy_video), segments)
            assert results["Speaker 1"] == "male"


@pytest.mark.asyncio
async def test_case_2_4_frames_female(tmp_path):
    """Case 2: 4 frames indicate female speaker -> result female."""
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()
    segments = [{"speaker_id": "Speaker 2", "start_time": 1.0, "end_time": 8.0}]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract):
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", return_value="female"):
            results = await detect_speakers_gender(str(dummy_video), segments)
            assert results["Speaker 2"] == "female"


def test_case_3_and_4_prompt_selection_rules():
    """
    Cases 3 & 4: Ensure the Vision prompt enforces selecting consistent speaker
    over bystanders and secondary characters.
    """
    assert "Identify the character/person who appears most consistently across the four frames" in VISUAL_GENDER_PROMPT
    assert "Do NOT choose a background character, bystander, secondary character" in VISUAL_GENDER_PROMPT
    assert "Prefer the character who appears to be speaking, talking, lip-moving" in VISUAL_GENDER_PROMPT
    assert "DO NOT return UNKNOWN" in VISUAL_GENDER_PROMPT


@pytest.mark.asyncio
async def test_case_8_vision_api_error_fallback(tmp_path):
    """Case 8: Vision API error -> graceful fallback to unknown without crashing other speakers."""
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()
    segments = [
        {"speaker_id": "Speaker 1", "start_time": 1.0, "end_time": 5.0},
        {"speaker_id": "Speaker 2", "start_time": 6.0, "end_time": 10.0},
    ]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    async def mock_detect(image_path, **kwargs):
        if "Speaker 1" in image_path:
            raise RuntimeError("HTTP 500 Vision API Down")
        return "female"

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract):
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", side_effect=mock_detect):
            results = await detect_speakers_gender(str(dummy_video), segments)
            # Speaker 1 errored -> unknown
            assert results["Speaker 1"] == "unknown"
            # Speaker 2 succeeded -> female
            assert results["Speaker 2"] == "female"


@pytest.mark.asyncio
async def test_case_9_invalid_vision_response_fallback(tmp_path):
    """Case 9: Vision returns unparseable text -> result unknown."""
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()
    segments = [{"speaker_id": "Speaker 1", "start_time": 1.0, "end_time": 5.0}]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract):
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", return_value="I cannot determine the gender"):
            results = await detect_speakers_gender(str(dummy_video), segments)
            assert results["Speaker 1"] == "unknown"


@pytest.mark.asyncio
async def test_case_10_manual_user_override_priority(async_db):
    """
    Case 10: Manual user override has highest priority!
    Visual = female, User override = male -> final = male.
    """
    import uuid
    project_id = f"test_proj_{uuid.uuid4().hex[:8]}"
    speaker_id = "Speaker 1"

    # Step 1: Pre-populate profile with manual user confirmation as male
    char_id = f"char-{uuid.uuid4().hex[:8]}"
    prof = CharacterVoiceProfile(
        id=str(uuid.uuid4()),
        project_id=project_id,
        character_id=char_id,
        name="User Confirmed Character",
        gender="male",
        role="main",
        confirmed_by_user=True,  # MANUAL USER OVERRIDE
    )
    async_db.add(prof)
    await async_db.flush()

    # Step 2: Dialogue LLM suggests male, but Visual AI detected female
    mock_llm = AsyncMock()
    mock_llm.generate_text.return_value = json.dumps({
        "characters": [
            {"character_id": char_id, "name": "Hero", "gender": "unknown", "role": "main", "speaker_ids": [speaker_id], "confidence": 0.9}
        ]
    })
    segments = [{"speaker_id": speaker_id, "text": "Hello world"}]
    visual_genders = {speaker_id: "female"}  # Visual AI says female

    # Step 3: Run map_and_persist
    res = await map_and_persist(
        async_db,
        project_id,
        segments,
        mock_llm,
        visual_genders=visual_genders,
    )

    # Step 4: Decision must preserve the user manual override ("male"), NOT visual ("female")
    decision = res.by_speaker[speaker_id]
    assert decision["gender"] == "male"

    # Step 5: DB profile must remain intact
    updated_prof = (await async_db.execute(
        select_profile(project_id, char_id)
    )).scalar_one()
    assert updated_prof.gender == "male"
    assert updated_prof.confirmed_by_user is True


def select_profile(project_id, char_id):
    from sqlalchemy import select
    return select(CharacterVoiceProfile).where(
        CharacterVoiceProfile.project_id == project_id,
        CharacterVoiceProfile.character_id == char_id,
    )


def test_case_11_insufficient_frames_or_single_short_segment():
    """Case 11: Speaker with single short segment -> graceful timestamp distribution."""
    # 0.4 second segment
    segments = [{"speaker_id": "Speaker 1", "start_time": 10.0, "end_time": 10.4}]
    ts = get_speaker_sample_timestamps(segments, "Speaker 1")
    assert len(ts) == 4
    # All 4 timestamps must be within [10.0, 10.4]
    for t in ts:
        assert 10.0 <= t <= 10.4
    # Check increasing order
    assert ts[0] <= ts[1] <= ts[2] <= ts[3]


@pytest.mark.asyncio
async def test_case_12_very_short_video_no_crash(tmp_path):
    """Case 12: Very short video (under 1s) -> does not crash."""
    dummy_video = tmp_path / "very_short.mp4"
    dummy_video.touch()
    segments = [{"speaker_id": "Speaker 1", "start_time": 0.0, "end_time": 0.5}]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract):
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", return_value="male"):
            results = await detect_speakers_gender(str(dummy_video), segments)
            assert results["Speaker 1"] == "male"


def test_caching_behavior():
    """Verify that cached speakers are not re-queried."""
    cache = {"Speaker 1": {"gender": "female", "source": "vision"}}
    segments = [{"speaker_id": "Speaker 1", "start_time": 0.0, "end_time": 5.0}]
    
    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(
            detect_speakers_gender("non_existent_path.mp4", segments, cache=cache)
        )
        assert results.get("Speaker 1") == "female"
    finally:
        loop.close()


@pytest.mark.asyncio
async def test_create_contact_sheet_ffmpeg_real(tmp_path):
    """Verify real FFmpeg command creates a 2x2 contact sheet from real image frames."""
    import subprocess
    # Generate 4 small distinct color test frames using FFmpeg
    colors = ["red", "green", "blue", "yellow"]
    img_paths = []
    for idx, col in enumerate(colors):
        p = tmp_path / f"frame_{idx}.jpg"
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={col}:s=320x240:d=0.1", "-frames:v", "1", str(p)]
        res = subprocess.run(cmd, capture_output=True)
        assert res.returncode == 0
        assert p.is_file() and p.stat().st_size > 0
        img_paths.append(p)

    output_sheet = tmp_path / "contact_sheet.jpg"
    await create_contact_sheet(img_paths, output_sheet)

    assert output_sheet.is_file()
    assert output_sheet.stat().st_size > 1000


@pytest.mark.asyncio
async def test_request_count_is_one_per_speaker(tmp_path):
    """
    Verify performance requirement:
    N speakers x 1 Vision API request (NOT N x 4 requests).
    5 speakers -> exactly 5 Vision API calls, 20 frame extractions.
    """
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()

    segments = []
    for i in range(5):
        spk = f"Speaker_{i+1}"
        segments.append({"speaker_id": spk, "start_time": float(i * 10), "end_time": float(i * 10 + 5)})

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch()

    detect_calls = []

    async def mock_detect(image_path, **kwargs):
        detect_calls.append(image_path)
        return "male"

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract) as extract_mock:
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", side_effect=mock_detect):
            results = await detect_speakers_gender(str(dummy_video), segments)

            # 5 speakers -> 5 * 4 = 20 frame extractions
            assert len(extract_mock.call_args_list) == 20

            # 5 speakers -> EXACTLY 5 Vision API calls (1 per speaker, NOT 20)
            assert len(detect_calls) == 5
            assert len(results) == 5
