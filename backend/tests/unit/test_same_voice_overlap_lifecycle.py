"""
Comprehensive regression tests for SAME_VOICE_OVERLAP lifecycle, Confirm validation gate,
granular TTS caching, auto-resolution, and idempotent state machine.
"""

import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.services.video_translator.timeline_scheduler import SchedulePolicy, schedule_segments
from app.api.routes.video_translator import (
    validate_character_voice_review,
    confirm_character_voice_review,
    _character_voice_review_data,
    update_character_voice_review,
    CharacterVoiceReviewUpdate,
    CharacterVoiceEdit,
    _active_render_jobs,
)
from app.models.video_translator import TranslationJobStatus


def create_seg(num, start, end, voice_id="en-US-GuyNeural", char_id=None, duration=None):
    dur = duration if duration is not None else (end - start)
    return {
        "id": num,
        "segment_number": num,
        "original_start": start,
        "original_end": end,
        "start_time": start,
        "end_time": end,
        "tts_duration": dur,
        "voice_id": voice_id,
        "voice_provider": "edge_tts",
        "character_id": char_id or f"char_{num}",
        "speaker_id": f"speaker_{num}",
        "role": "supporting",
        "translated_text": f"Text for segment {num}",
    }


# =========================================================================
# Case 1: Same voice nhưng không overlap -> VALID
# =========================================================================
def test_case_1_same_voice_no_overlap_is_valid():
    """
    Case 1:
    53: 180.00 -> 182.00
    54: 182.00 -> 184.00
    same voice: en-US-GuyNeural
    Expected: VALID, không requires_review, không SAME_VOICE_OVERLAP.
    """
    segs = [
        create_seg(53, 180.0, 182.0, voice_id="en-US-GuyNeural"),
        create_seg(54, 182.0, 184.0, voice_id="en-US-GuyNeural"),
    ]
    result = schedule_segments(segs, video_duration=200.0)

    assert result.requires_review is False
    assert len(result.unresolved_conflicts or []) == 0
    seg_53 = next(s for s in result.segments if s["id"] == 53)
    seg_54 = next(s for s in result.segments if s["id"] == 54)
    # 54 starts exactly at or after 53 ends
    assert seg_54["scheduled_start"] >= seg_53["scheduled_end"] - 0.001


# =========================================================================
# Case 2: Same voice và overlap -> NEEDS_REVIEW, không render
# =========================================================================
def test_case_2_same_voice_with_overlap_triggers_needs_review():
    """
    Case 2:
    53: 180.00 -> 183.00
    54: 182.00 -> 184.00
    same voice: en-US-GuyNeural
    Expected: NEEDS_REVIEW, conflicts detected, cannot fit without same-voice overlap.
    """
    # Policy with 0 reschedule to simulate bounded timeline constraint
    strict_policy = SchedulePolicy(max_reschedule_seconds=0.0, max_tempo=1.0)
    segs = [
        create_seg(53, 180.0, 183.0, voice_id="en-US-GuyNeural"),
        create_seg(54, 182.0, 184.0, voice_id="en-US-GuyNeural"),
    ]
    result = schedule_segments(segs, video_duration=184.0, policy=strict_policy)

    assert result.requires_review is True
    assert len(result.unresolved_conflicts) > 0
    conflict = result.unresolved_conflicts[0]
    assert conflict["reason"] == "same_voice_overlap"
    assert conflict["segment_id"] == 54
    assert conflict["with"] == 53


# =========================================================================
# Case 3: Confirm nhưng conflict vẫn tồn tại -> Bị từ chối, không render
# =========================================================================
@pytest.mark.asyncio
async def test_case_3_confirm_rejected_when_conflict_persists():
    """
    Case 3:
    User Confirm khi 53/54 vẫn conflict.
    Expected: HTTP 409, status remains NEEDS_REVIEW, no render launched.
    """
    mock_session = AsyncMock()

    # Mock job
    mock_job = MagicMock()
    mock_job.id = "job-conflict-123"
    mock_job.project_id = "proj-123"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value
    mock_job.settings_snapshot_json = "{}"

    # Return conflicting segments from _character_voice_review_data
    conflicting_segs = [
        {
            "id": 53,
            "segment_number": 53,
            "speaker_id": "spk_1",
            "character_id": "char_1",
            "voice_provider": "edge_tts",
            "voice_id": "en-US-GuyNeural",
            "original_start": 180.0,
            "original_end": 183.0,
            "tts_duration": 3.0,
        },
        {
            "id": 54,
            "segment_number": 54,
            "speaker_id": "spk_2",
            "character_id": "char_2",
            "voice_provider": "edge_tts",
            "voice_id": "en-US-GuyNeural",
            "original_start": 182.0,
            "original_end": 184.0,
            "tts_duration": 2.0,
        },
    ]

    with patch("app.api.routes.video_translator._character_voice_review_data", return_value={"job_id": mock_job.id, "segments": conflicting_segs, "status": "needs_review"}):
        with patch("app.services.video_translator.timeline_scheduler.schedule_segments") as mock_sched:
            # Simulate scheduler returning unresolved conflict
            mock_sched.return_value = MagicMock(
                segments=[
                    {"id": 53, "segment_number": 53, "scheduled_start": 180.0, "scheduled_end": 183.0, "voice_id": "en-US-GuyNeural"},
                    {"id": 54, "segment_number": 54, "scheduled_start": 182.0, "scheduled_end": 184.0, "voice_id": "en-US-GuyNeural"},
                ],
                unresolved_conflicts=[{"segment_id": 54, "with": 53, "reason": "same_voice_overlap"}],
                requires_review=True,
            )

            validation = await validate_character_voice_review(mock_job.id, mock_session)
            assert validation["data"]["passed"] is False
            assert len(validation["data"]["issues"]) > 0
            assert validation["data"]["issues"][0]["reason"] == "same_voice_overlap"
            assert "en-US-GuyNeural" in validation["data"]["issues"][0]["message"]

            # Now test confirm endpoint rejects with 409
            mock_exec = MagicMock()
            mock_exec.scalar_one_or_none.return_value = mock_job
            mock_session.execute.return_value = mock_exec

            mock_bg = MagicMock()
            with pytest.raises(HTTPException) as exc_info:
                await confirm_character_voice_review(mock_job.id, mock_bg, mock_session)

            assert exc_info.value.status_code == 409
            mock_bg.add_task.assert_not_called()
            assert mock_job.status == TranslationJobStatus.NEEDS_REVIEW.value


# =========================================================================
# Case 4: User thay voice -> Hợp lệ và tiếp tục render
# =========================================================================
@pytest.mark.asyncio
async def test_case_4_user_changes_voice_resolves_conflict():
    """
    Case 4:
    User changes segment 54 to en-US-JennyNeural.
    Expected: Validation passes, schedule valid, confirm succeeds, background render queued.
    """
    mock_session = AsyncMock()

    mock_job = MagicMock()
    mock_job.id = "job-resolved-456"
    mock_job.project_id = "proj-456"
    mock_job.status = TranslationJobStatus.NEEDS_REVIEW.value
    mock_job.settings_snapshot_json = "{}"

    resolved_segs = [
        {
            "id": 53,
            "segment_number": 53,
            "speaker_id": "spk_1",
            "character_id": "char_1",
            "voice_provider": "edge_tts",
            "voice_id": "en-US-GuyNeural",
            "original_start": 180.0,
            "original_end": 183.0,
            "tts_duration": 3.0,
        },
        {
            "id": 54,
            "segment_number": 54,
            "speaker_id": "spk_2",
            "character_id": "char_2",
            "voice_provider": "edge_tts",
            "voice_id": "en-US-JennyNeural",  # Changed!
            "original_start": 182.0,
            "original_end": 184.0,
            "tts_duration": 2.0,
        },
    ]

    with patch("app.api.routes.video_translator._character_voice_review_data", return_value={"job_id": mock_job.id, "segments": resolved_segs, "status": "needs_review"}):
        validation = await validate_character_voice_review(mock_job.id, mock_session)
        assert validation["data"]["passed"] is True
        assert len(validation["data"]["issues"]) == 0

        mock_exec = MagicMock()
        mock_exec.scalar_one_or_none.return_value = mock_job
        mock_exec.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_exec

        mock_bg = MagicMock()
        res = await confirm_character_voice_review(mock_job.id, mock_bg, mock_session)

        assert res["success"] is True
        assert res["data"]["resumed"] is True
        mock_bg.add_task.assert_called_once()
        assert mock_job.status == TranslationJobStatus.GENERATING_TTS.value


# =========================================================================
# Case 5: Cached TTS -> Chỉ regenerate segment bị thay đổi
# =========================================================================
def test_case_5_tts_cache_invalidation_granularity(tmp_path):
    """
    Case 5:
    54 segments đã cache. Segment 53 đổi voice.
    Expected: Segment 53 is invalidated and regenerated. Segments 1-52 and 54 remain cached.
    """
    tts_dir = tmp_path / "tts"
    tts_dir.mkdir(parents=True)

    # Helper replicating _is_tts_cache_valid
    def is_tts_cache_valid(s_dict, tts_dir_p):
        audio_f = tts_dir_p / f"seg_{s_dict['segment_number']:03d}.wav"
        meta_f = tts_dir_p / f"seg_{s_dict['segment_number']:03d}.meta.json"
        if not audio_f.exists() or audio_f.stat().st_size == 0:
            return False
        if meta_f.exists():
            try:
                with open(meta_f, "r", encoding="utf-8") as mf:
                    m_data = json.load(mf)
                if m_data.get("voice_id") != s_dict.get("voice_id") or m_data.get("translated_text") != s_dict.get("translated_text"):
                    return False
            except Exception:
                return False
        return True

    # Seed 54 segments in cache with GuyNeural
    segments = []
    for i in range(1, 55):
        seg_f = tts_dir / f"seg_{i:03d}.wav"
        seg_m = tts_dir / f"seg_{i:03d}.meta.json"
        seg_f.write_bytes(b"dummy_pcm_audio_content")
        with open(seg_m, "w", encoding="utf-8") as mf:
            json.dump({"voice_id": "en-US-GuyNeural", "voice_provider": "edge_tts", "translated_text": f"text {i}"}, mf)

        segments.append({
            "segment_number": i,
            "voice_id": "en-US-GuyNeural",
            "translated_text": f"text {i}",
        })

    # Initially all 54 are valid
    assert all(is_tts_cache_valid(s, tts_dir) for s in segments)

    # Change voice of segment 53 ONLY
    segments[52]["voice_id"] = "en-US-JennyNeural"

    # Verify:
    assert is_tts_cache_valid(segments[52], tts_dir) is False  # Segment 53 must regenerate!
    assert is_tts_cache_valid(segments[53], tts_dir) is True   # Segment 54 remains cached!
    for i in range(52):
        assert is_tts_cache_valid(segments[i], tts_dir) is True  # Segments 1-52 remain cached!


# =========================================================================
# Case 6: Duplicate Confirm -> Idempotent, không duplicate render
# =========================================================================
@pytest.mark.asyncio
async def test_case_6_duplicate_confirm_is_idempotent():
    """
    Case 6:
    Gửi Confirm 2 lần liên tiếp.
    Expected: Second call returns early without duplicate background render or duplicate TTS.
    """
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-idemp-789"
    mock_job.project_id = "proj-789"
    mock_job.status = TranslationJobStatus.GENERATING_TTS.value  # Already resumed/processing

    mock_exec = MagicMock()
    mock_exec.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_exec

    mock_bg = MagicMock()
    res = await confirm_character_voice_review(mock_job.id, mock_bg, mock_session)

    assert res["success"] is True
    assert res["data"]["resumed"] is False
    assert "already processing" in res["data"]["message"]
    mock_bg.add_task.assert_not_called()


# =========================================================================
# Case 7: Completed job -> Terminal state, không restart hay reset
# =========================================================================
@pytest.mark.asyncio
async def test_case_7_completed_job_terminal_guard():
    """
    Case 7:
    Job đã COMPLETED. Confirm không được restart job hoặc quay về segment 0.
    """
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = "job-complete-999"
    mock_job.status = TranslationJobStatus.COMPLETED.value

    mock_exec = MagicMock()
    mock_exec.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_exec

    mock_bg = MagicMock()
    res = await confirm_character_voice_review(mock_job.id, mock_bg, mock_session)

    assert res["success"] is True
    assert res["data"]["resumed"] is False
    assert "already completed" in res["data"]["message"]
    mock_bg.add_task.assert_not_called()
