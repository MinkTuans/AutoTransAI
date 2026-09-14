"""Unit tests for leading/trailing filler detection and trim window."""

from app.services.video_translator.filler_detector import (
    parse_silencedetect_log,
    propose_content_window,
    merge_ai_cut_hints,
    build_trim_window_cmd,
    parse_ai_cut_json,
)


def test_parse_silencedetect_pairs_start_and_end():
    log = """
[silencedetect @ 0x1] silence_start: 420.12
[silencedetect @ 0x1] silence_end: 839.90 | silence_duration: 419.78
[silencedetect @ 0x1] silence_start: 12.0
[silencedetect @ 0x1] silence_end: 40.5 | silence_duration: 28.5
"""
    silences = parse_silencedetect_log(log)
    assert silences == [(12.0, 40.5), (420.12, 839.90)]


def test_trailing_silence_proposes_cut_before_dead_zone():
    # 14 min video, speech 0-420s, silence 420-840
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(0.0, 420.0)],
    )
    assert plan["applied"] is True
    assert plan["start_sec"] == 0.0
    assert 419.0 <= plan["end_sec"] <= 422.0
    assert plan["trailing_filler_sec"] >= 400


def test_leading_silence_proposes_cut_after_intro():
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(90.0, 840.0)],
    )
    assert plan["applied"] is True
    assert 88.0 <= plan["start_sec"] <= 91.0
    assert plan["end_sec"] == 840.0
    assert plan["leading_filler_sec"] >= 80


def test_leading_and_trailing_both_cut():
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(60.0, 420.0)],
    )
    assert plan["applied"] is True
    assert plan["start_sec"] >= 55
    assert plan["end_sec"] <= 425
    assert plan["end_sec"] - plan["start_sec"] >= 300


def test_leading_freeze_without_silence_still_cuts_intro():
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(0.0, 840.0)],
        still_intervals=[(0.0, 45.0)],
    )
    assert plan["applied"] is True
    assert plan["start_sec"] >= 40.0


def test_no_dead_zone_does_not_trim():
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(0.0, 830.0)],
    )
    assert plan["applied"] is False
    assert plan["start_sec"] == 0.0
    assert plan["end_sec"] == 840.0


def test_refuses_cut_when_keep_window_too_small():
    plan = propose_content_window(
        duration=840.0,
        speech_intervals=[(400.0, 430.0)],
        min_keep_ratio=0.40,
        min_keep_sec=60.0,
    )
    assert plan["applied"] is False
    assert plan["start_sec"] == 0.0
    assert plan["end_sec"] == 840.0


def test_ai_can_cancel_leading_cut_when_head_is_content():
    media = propose_content_window(
        duration=840.0,
        speech_intervals=[(90.0, 800.0)],
    )
    merged = merge_ai_cut_hints(media, {"head_is_filler": False, "tail_is_filler": True})
    assert merged["start_sec"] == 0.0
    assert merged["applied"] is True
    assert merged["end_sec"] < 840.0


def test_parse_ai_cut_json_reads_seconds():
    parsed = parse_ai_cut_json(
        '{"head_is_filler": true, "content_start": 55.5, "tail_is_filler": true, "content_end": 410}'
    )
    assert parsed["head_is_filler"] is True
    assert parsed["content_start"] == 55.5
    assert parsed["content_end"] == 410.0


def test_trim_window_cmd_uses_ss_and_duration():
    cmd = build_trim_window_cmd("/in.mp4", "/out.mp4", start_sec=60.0, end_sec=420.0)
    assert cmd[0] == "ffmpeg"
    assert "-ss" in cmd
    assert any(v.startswith("60") for v in cmd)
    assert "-t" in cmd
    assert "-c" in cmd and "copy" in cmd
