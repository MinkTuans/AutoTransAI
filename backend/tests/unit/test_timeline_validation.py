"""
Unit tests for timeline validation, segment deduplication, and video duration invariants.
"""

import pytest
from app.services.video_translator.translator_service import validate_and_clean_timeline_segments


def test_timeline_validation_normal_segments():
    raw = [
        {"number": 1, "start_time": 0.0, "end_time": 4.5, "text": "Hello"},
        {"number": 2, "start_time": 5.0, "end_time": 10.0, "text": "World"},
    ]
    cleaned = validate_and_clean_timeline_segments(raw, total_duration=2287.0, job_id="VT-TEST")
    assert len(cleaned) == 2
    assert cleaned[0]["end_time"] == 4.5
    assert cleaned[1]["end_time"] == 10.0


def test_timeline_validation_out_of_bounds_correction_40_06():
    """Verify segment extending to 40:06 (2406s) on 38:07 (2287s) video is corrected to total_duration."""
    raw = [
        {"number": 1, "start_time": 2100.0, "end_time": 2150.0, "text": "Dialogue near 35 min"},
        {"number": 2, "start_time": 2280.0, "end_time": 2406.0, "text": "Out of bounds dialogue"},
    ]
    cleaned = validate_and_clean_timeline_segments(raw, total_duration=2287.0, job_id="VT-TEST-4006")
    assert len(cleaned) == 2
    assert cleaned[1]["end_time"] <= 2287.0
    assert max(s["end_time"] for s in cleaned) <= 2287.0


def test_timeline_validation_deduplication():
    """Verify duplicate segments from chunk overlap (5s overlap window) are deduplicated."""
    raw = [
        {"number": 1, "start_time": 85.0, "end_time": 90.0, "text": "Sentence across chunk boundary"},
        {"number": 2, "start_time": 85.5, "end_time": 90.5, "text": "Sentence across chunk boundary"},
    ]
    cleaned = validate_and_clean_timeline_segments(raw, total_duration=200.0, job_id="VT-TEST-DUP")
    assert len(cleaned) == 1
    assert cleaned[0]["start_time"] == 85.0


def test_timeline_validation_empty_raises():
    with pytest.raises(ValueError, match="Không có phân đoạn hội thoại nào được nhận diện"):
        validate_and_clean_timeline_segments([], total_duration=100.0, job_id="VT-TEST-EMPTY")
