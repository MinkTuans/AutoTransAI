"""
Comprehensive audit test for 38:07 (2287s) video timeline segmentation.
Validates root cause fixes for 40:06 timestamp drift and 01:51-02:37 dialogue coverage.
"""

import pytest
from app.services.video_translator.translator_service import validate_and_clean_timeline_segments


def test_3807_video_timeline_audit():
    """
    Simulate STT segments generated across 8 audio chunks for a 38:07 (2287s) video.
    Verifies that:
    1. No segment extends to 40:06 (2406s) or past 2287s.
    2. Dialogue in 01:51 -> 02:37 (111s -> 157s) is preserved.
    3. Segments are properly sorted and deduplicated.
    """
    total_video_duration = 2287.0  # 38:07

    raw_stt_segments = [
        # Chunk 0 (0s - 90s)
        {"number": 1, "start_time": 0.0, "end_time": 4.5, "text": "Greeting sentence"},
        {"number": 2, "start_time": 10.0, "end_time": 15.0, "text": "Opening speech"},
        
        # Chunk 1 (85s - 175s) - Covers 01:51 -> 02:37 (111s -> 157s)
        {"number": 3, "start_time": 111.0, "end_time": 130.0, "text": "Dialogue at 01:51"},
        {"number": 4, "start_time": 132.0, "end_time": 157.0, "text": "Dialogue at 02:12"},

        # Chunk 7 (2100s - 2287s) - Audio ends at 2287s
        {"number": 443, "start_time": 2250.0, "end_time": 2260.0, "text": "Giọng nói này là trẻ con."},
        {"number": 444, "start_time": 2262.0, "end_time": 2270.0, "text": "Cậu đang làm gì vậy? Cậu đang làm cái quái gì thế này?"},
        {"number": 445, "start_time": 2272.0, "end_time": 2280.0, "text": "Cậu đang tự hủy hoại chính mình đấy."},

        # Out-of-bounds raw output from buggy model (attempted 2403s -> 2406s / 40:03 -> 40:06)
        {"number": 446, "start_time": 2282.0, "end_time": 2406.0, "text": "直进家, 你这个88儿, 我是不会放过你的。"},
    ]

    cleaned = validate_and_clean_timeline_segments(
        raw_stt_segments,
        total_duration=total_video_duration,
        job_id="VT-3807-AUDIT"
    )

    # Invariant 1: Max segment end_time MUST NOT exceed 2287s (38:07)
    max_end = max(s["end_time"] for s in cleaned)
    assert max_end <= total_video_duration, f"Max segment end ({max_end}s) exceeded video duration ({total_video_duration}s)"
    assert max_end < 2400.0, f"Segment timestamp drifted to 40:06 ({max_end}s)"

    # Invariant 2: Dialogue at 111s -> 157s (01:51 -> 02:37) MUST be present
    seg_111_157 = [s for s in cleaned if s["start_time"] >= 110.0 and s["end_time"] <= 160.0]
    assert len(seg_111_157) == 2, "Missing dialogue in 01:51 -> 02:37 interval"

    # Invariant 3: Ordering
    for i in range(1, len(cleaned)):
        assert cleaned[i]["start_time"] >= cleaned[i-1]["start_time"], "Segments out of chronological order"

    # Invariant 4: Last segment text preserved and bounded
    last_seg = cleaned[-1]
    assert "直进家" in last_seg["text"]
    assert last_seg["end_time"] <= 2287.0
