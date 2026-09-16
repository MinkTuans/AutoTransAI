from app.services.video_translator.timeline_scheduler import SchedulePolicy, schedule_segments


def seg(n, start, end, duration, voice, role="supporting"):
    return {"id": n, "original_start": start, "original_end": end, "tts_duration": duration, "voice_id": voice, "role": role}


def test_small_overlap_with_different_voices_is_kept():
    result = schedule_segments([seg(1, 0, 2, 2, "a"), seg(2, 1.8, 3, 1.2, "b")], 5)
    assert result.segments[1]["schedule_action"] == "kept_small_overlap"
    assert result.requires_review is False


def test_small_overlap_with_same_voice_is_serialized():
    result = schedule_segments([seg(1, 0, 2, 2, "a"), seg(2, 1.8, 3, 1.2, "a")], 5)
    assert result.segments[1]["scheduled_start"] >= result.segments[0]["scheduled_end"]
    assert result.segments[1]["schedule_action"] == "serialized_same_voice"


def test_three_speakers_never_overlap_when_voice_is_shared():
    result = schedule_segments([seg(1, 0, 2, 2, "a"), seg(2, 1, 3, 2, "b"), seg(3, 1.5, 3, 1.5, "a")], 8)
    first, _, third = result.segments
    assert first["scheduled_end"] <= third["scheduled_start"] or third["scheduled_end"] <= first["scheduled_start"]


def test_short_tts_keeps_original_start_and_actual_end():
    result = schedule_segments([seg(1, 2, 5, 1, "a")], 8)
    assert (result.segments[0]["scheduled_start"], result.segments[0]["scheduled_end"]) == (2, 3)


def test_no_bounded_slot_reports_cannot_fit():
    policy = SchedulePolicy(max_reschedule_seconds=0.1, max_tempo=1.0)
    result = schedule_segments([seg(1, 0, 3, 3, "a"), seg(2, 0, 3, 3, "a")], 3, policy)
    assert result.requires_review is True
    assert result.segments[1]["schedule_action"] == "cannot_fit"


def test_same_voice_reschedule_does_not_create_a_new_overlap():
    result = schedule_segments([
        seg(1, 0.0, 1.0, 1.0, "a"),
        seg(2, 0.8, 0.9, 0.3, "a"),
        seg(3, 1.2, 2.2, 1.0, "a"),
    ], 5)
    ordered = sorted(result.segments, key=lambda item: item["scheduled_start"])
    assert all(left["scheduled_end"] <= right["scheduled_start"] for left, right in zip(ordered, ordered[1:]))
