"""Bounded post-TTS scheduling that preserves the source conversation rhythm."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SchedulePolicy:
    small_overlap_seconds: float = 0.25
    max_reschedule_seconds: float = 3.0
    max_tempo: float = 1.85
    ducking_gain: float = 0.45


@dataclass
class ScheduleResult:
    segments: list[dict[str, Any]]
    requires_review: bool = False
    unresolved_conflicts: list[dict[str, Any]] | None = None


def _overlap(left: dict[str, Any], right_start: float, right_end: float) -> float:
    l_start = float(left.get("scheduled_start", 0.0))
    l_end = float(left.get("scheduled_end", 0.0))
    if right_end <= right_start:
        return 0.05 if (l_start <= right_start < l_end) else 0.0
    return max(0.0, min(l_end, right_end) - max(l_start, right_start))


def schedule_segments(segments: list[dict[str, Any]], video_duration: float, policy: SchedulePolicy | None = None) -> ScheduleResult:
    policy = policy or SchedulePolicy()
    scheduled: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    for source in sorted(segments, key=lambda item: (float(item.get("original_start", 0)), int(item.get("id", 0)))):
        item = dict(source)
        original_start = float(item.get("original_start", 0.0))
        original_end = float(item.get("original_end", original_start))
        raw_duration = max(0.0, float(item.get("tts_duration", 0.0)))
        slot = max(0.1, original_end - original_start)
        tempo = min(policy.max_tempo, max(1.0, raw_duration / slot)) if raw_duration > slot else 1.0
        duration = raw_duration / tempo if tempo else raw_duration
        start = original_start
        end = start + duration
        action = "compressed" if tempo > 1.0 else "kept_original"
        overlap_ids: list[int] = []

        intersecting = [prior for prior in scheduled if _overlap(prior, start, end) > 0]
        for prior in intersecting:
            overlap_ids.append(prior["id"])
            overlap = _overlap(prior, start, end)
            if prior.get("voice_id") != item.get("voice_id"):
                if overlap <= policy.small_overlap_seconds:
                    action = "kept_small_overlap"
                elif item.get("role") == "supporting":
                    action = "ducked_supporting"
                    item["gain"] = policy.ducking_gain
                continue

            candidate = float(prior["scheduled_end"])
            displacement = candidate - original_start
            if displacement <= policy.max_reschedule_seconds and candidate + duration <= video_duration:
                start, end = candidate, candidate + duration
                action = "serialized_same_voice" if tempo == 1.0 else "compressed_and_rescheduled"
            elif policy.max_reschedule_seconds > 0.0 and candidate < video_duration:
                start = candidate
                avail = max(0.2, video_duration - start)
                if duration > avail:
                    tempo = min(2.5, max(tempo, raw_duration / avail))
                    duration = max(0.1, raw_duration / tempo)
                end = min(video_duration, start + duration)
                action = "serialized_same_voice"
            else:
                action = "cannot_fit"
                conflicts.append({"segment_id": item.get("id"), "with": prior.get("id"), "reason": "same_voice_overlap"})
                break

        item.update({
            "scheduled_start": round(start, 3),
            "scheduled_end": round(end, 3),
            "tempo": round(tempo, 4),
            "gain": item.get("gain", 1.0),
            "overlap_with": overlap_ids,
            "schedule_action": action,
        })
        scheduled.append(item)

    return ScheduleResult(scheduled, bool(conflicts), conflicts)
