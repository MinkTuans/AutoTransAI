"""Detect leading/trailing filler (ads, endcards) and propose a keep-window for INGEST trim."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

_SILENCE_START = re.compile(r"silence_start:\s*([0-9.]+)")
_SILENCE_END = re.compile(r"silence_end:\s*([0-9.]+)")


def parse_silencedetect_log(stderr: str, duration: Optional[float] = None) -> list[tuple[float, float]]:
    """Parse ffmpeg silencedetect stderr into (start, end) silence intervals."""
    starts: list[float] = []
    pairs: list[tuple[float, float]] = []
    for line in (stderr or "").splitlines():
        m_start = _SILENCE_START.search(line)
        if m_start:
            starts.append(float(m_start.group(1)))
            continue
        m_end = _SILENCE_END.search(line)
        if m_end and starts:
            start = starts.pop(0)
            end = float(m_end.group(1))
            if end > start:
                pairs.append((start, end))
    if starts and duration is not None:
        dangling = starts[-1]
        if dangling < float(duration):
            pairs.append((dangling, float(duration)))
    pairs.sort(key=lambda p: p[0])
    return pairs


def speech_intervals_from_silence(
    duration: float, silences: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """Invert silence intervals into speech/content intervals within [0, duration]."""
    if duration <= 0:
        return []
    cursor = 0.0
    speech: list[tuple[float, float]] = []
    for s, e in sorted(silences):
        s = max(0.0, min(duration, s))
        e = max(0.0, min(duration, e))
        if s > cursor + 0.05:
            speech.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < duration - 0.05:
        speech.append((cursor, duration))
    return speech


def _in_interval(t: float, intervals: list[tuple[float, float]]) -> bool:
    for a, b in intervals:
        if a <= t < b:
            return True
    return False


def propose_content_window(
    duration: float,
    *,
    speech_intervals: Optional[list[tuple[float, float]]] = None,
    still_intervals: Optional[list[tuple[float, float]]] = None,
    min_keep_ratio: float = 0.40,
    min_keep_sec: float = 60.0,
    dead_zone_sec: float = 20.0,
    edge_pad_sec: float = 0.4,
    min_speech_run_sec: float = 1.0,
) -> dict[str, Any]:
    """Propose [start_sec, end_sec] keep-window. Only trims head/tail dead zones."""
    duration = float(duration or 0.0)
    plan = {
        "applied": False,
        "start_sec": 0.0,
        "end_sec": duration,
        "original_duration": duration,
        "leading_filler_sec": 0.0,
        "trailing_filler_sec": 0.0,
        "reason": "no_cut",
    }
    if duration <= 0:
        plan["reason"] = "invalid_duration"
        return plan

    speech = [(float(a), float(b)) for a, b in (speech_intervals or []) if b > a]
    still = [(float(a), float(b)) for a, b in (still_intervals or []) if b > a]
    if not speech and not still:
        plan["reason"] = "no_signals"
        return plan

    start_sec = 0.0
    if speech:
        first = next((a for a, b in speech if (b - a) >= min_speech_run_sec), None)
        if first is not None and first >= dead_zone_sec:
            start_sec = max(0.0, first - edge_pad_sec)
        elif still and first is not None and first >= 8.0:
            covered = still[0][0] <= 0.5 and still[0][1] >= first * 0.8
            if covered:
                start_sec = max(0.0, first - edge_pad_sec)

    head_freeze_end = next((b for a, b in still if a <= 1.0 and (b - a) >= 8.0), None)
    if head_freeze_end:
        start_sec = max(start_sec, min(head_freeze_end, duration * 0.3))

    end_sec = duration
    if speech:
        last = next((b for a, b in reversed(speech) if (b - a) >= min_speech_run_sec), None)
        if last is not None and (duration - last) >= dead_zone_sec:
            end_sec = min(duration, last + edge_pad_sec)

    tail_freeze_start = next((a for a, b in reversed(still) if b >= duration - 1.0 and (b - a) >= dead_zone_sec), None)
    if tail_freeze_start is not None:
        end_sec = min(end_sec, max(tail_freeze_start, duration * 0.4))

    start_sec = min(start_sec, duration)
    end_sec = max(end_sec, start_sec)
    keep = end_sec - start_sec
    if keep < min_keep_sec or keep < (min_keep_ratio * duration):
        plan["reason"] = "keep_window_too_small"
        return plan

    applied = start_sec > 0.5 or (duration - end_sec) > 0.5
    plan.update(
        {
            "applied": applied,
            "start_sec": round(start_sec, 2),
            "end_sec": round(end_sec, 2),
            "leading_filler_sec": round(start_sec, 2),
            "trailing_filler_sec": round(max(0.0, duration - end_sec), 2),
            "reason": "head_and_or_tail" if applied else "no_cut",
        }
    )
    return plan


def merge_ai_cut_hints(plan: dict[str, Any], ai: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Blend media plan with AI head/tail labels. AI False on an edge cancels that cut."""
    if not plan or not ai:
        return plan
    out = dict(plan)
    duration = float(out.get("original_duration") or out.get("end_sec") or 0.0)
    start = float(out.get("start_sec") or 0.0)
    end = float(out.get("end_sec") or duration)

    if ai.get("head_is_filler") is False:
        start = 0.0
    elif ai.get("content_start") is not None:
        try:
            hint = float(ai["content_start"])
            if hint > 0:
                start = max(start, min(hint, duration * 0.3))
        except (TypeError, ValueError):
            pass

    if ai.get("tail_is_filler") is False:
        end = duration
    elif ai.get("content_end") is not None:
        try:
            hint = float(ai["content_end"])
            if 0 < hint < duration:
                end = min(end, max(hint, duration * 0.4))
        except (TypeError, ValueError):
            pass

    if end <= start + 1:
        return plan

    keep = end - start
    min_keep_sec = 60.0
    min_keep_ratio = 0.40
    if keep < min_keep_sec or keep < min_keep_ratio * duration:
        return plan

    applied = start > 0.5 or (duration - end) > 0.5
    out.update(
        {
            "applied": applied,
            "start_sec": round(start, 2),
            "end_sec": round(end, 2),
            "leading_filler_sec": round(start, 2),
            "trailing_filler_sec": round(max(0.0, duration - end), 2),
            "reason": "media_plus_ai" if applied else "no_cut",
        }
    )
    return out


def parse_ai_cut_json(text: str) -> dict[str, Any]:
    """Parse a JSON object from an LLM reply; ignore wrapping markdown."""
    raw = (text or "").strip()
    if not raw:
        return {}
    if "```" in raw:
        raw = raw.split("```", 2)[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        return {}
    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return {}
    out: dict[str, Any] = {}
    if "head_is_filler" in data:
        out["head_is_filler"] = bool(data["head_is_filler"])
    if "tail_is_filler" in data:
        out["tail_is_filler"] = bool(data["tail_is_filler"])
    for key in ("content_start", "content_end"):
        if data.get(key) is not None:
            try:
                out[key] = float(data[key])
            except (TypeError, ValueError):
                pass
    return out


def build_trim_window_cmd(input_path: str, output_path: str, start_sec: float, end_sec: float) -> list[str]:
    """ffmpeg command to keep [start_sec, end_sec) using stream copy."""
    duration = max(0.1, float(end_sec) - float(start_sec))
    cmd = ["ffmpeg", "-y"]
    if start_sec > 0.05:
        cmd += ["-ss", f"{float(start_sec):.3f}"]
    cmd += ["-i", str(input_path), "-t", f"{duration:.3f}", "-c", "copy", "-avoid_negative_ts", "make_zero", str(output_path)]
    return cmd


_FREEZE_START = re.compile(r"freeze_start:\s*([0-9.]+)")
_FREEZE_END = re.compile(r"freeze_end:\s*([0-9.]+)")


def parse_freezedetect_log(stderr: str, offset: float = 0.0, duration: Optional[float] = None) -> list[tuple[float, float]]:
    """Parse ffmpeg freezedetect log; timestamps are shifted by `offset`."""
    starts: list[float] = []
    pairs: list[tuple[float, float]] = []
    for line in (stderr or "").splitlines():
        m_start = _FREEZE_START.search(line)
        if m_start:
            starts.append(float(m_start.group(1)) + offset)
            continue
        m_end = _FREEZE_END.search(line)
        if m_end and starts:
            start = starts.pop(0)
            end = float(m_end.group(1)) + offset
            if end > start:
                pairs.append((start, end))
    if starts and duration is not None:
        dangling = starts[-1]
        if dangling < float(duration):
            pairs.append((dangling, float(duration)))
    pairs.sort(key=lambda p: p[0])
    return pairs


def build_edge_classification_prompt(duration: float, speech_intervals: list[tuple[float, float]]) -> str:
    """Ask an LLM whether the head/tail outside speech looks like ads/endcards."""
    speech_txt = ", ".join(f"{a:.1f}-{b:.1f}s" for a, b in speech_intervals[:12]) or "none"
    return (
        "You classify filler at the START and END of a video (intro bumper, endcard, subscribe screen, static ad).\n"
        f"Total duration: {duration:.1f} seconds.\n"
        f"Detected speech-like spans: {speech_txt}.\n"
        "Return JSON only: "
        '{"head_is_filler": true|false, "content_start": <seconds>, "tail_is_filler": true|false, "content_end": <seconds>}.\n'
        "Only mark head/tail filler. Do not cut the middle."
    )


async def probe_silence_intervals(audio_path: str, duration: float) -> list[tuple[float, float]]:
    """Run ffmpeg silencedetect over the full extracted audio."""
    from app.core.security import safe_subprocess_run_async

    cmd = [
        "ffmpeg", "-hide_banner", "-i", str(audio_path),
        "-af", "silencedetect=noise=-30dB:d=1.0",
        "-f", "null", "-",
    ]
    try:
        result = await safe_subprocess_run_async(cmd, timeout=max(120, int(duration * 2)), check=False)
    except Exception:
        return []
    stderr = f"{result.stderr or ''}{result.stdout or ''}"
    return parse_silencedetect_log(stderr, duration=duration)


async def probe_freeze_intervals(video_path: str, duration: float) -> list[tuple[float, float]]:
    """Scan the first 2 minutes and last 3 minutes for frozen/endcard frames."""
    from app.core.security import safe_subprocess_run_async

    async def _scan(ss: float, span: float) -> list[tuple[float, float]]:
        if span < 2:
            return []
        cmd = [
            "ffmpeg", "-hide_banner",
            "-ss", f"{ss:.3f}",
            "-t", f"{span:.3f}",
            "-i", str(video_path),
            "-vf", "freezedetect=n=0.004:d=2",
            "-f", "null", "-",
        ]
        try:
            result = await safe_subprocess_run_async(cmd, timeout=max(60, int(span * 3)), check=False)
        except Exception:
            return []
        stderr = f"{result.stderr or ''}{result.stdout or ''}"
        return parse_freezedetect_log(stderr, offset=ss, duration=ss + span)

    head_span = min(120.0, duration)
    tail_start = max(0.0, duration - 180.0)
    tail_span = duration - tail_start
    head = await _scan(0.0, head_span)
    tail = await _scan(tail_start, tail_span) if tail_start > head_span - 5 else []
    return head + tail


async def classify_edges_with_llm(
    duration: float,
    speech_intervals: list[tuple[float, float]],
    llm_generate=None,
) -> dict[str, Any]:
    """Optional LLM confirmation of head/tail filler. Failures return {}."""
    if llm_generate is None:
        return {}
    prompt = build_edge_classification_prompt(duration, speech_intervals)
    try:
        raw = await llm_generate(prompt)
    except Exception:
        return {}
    return parse_ai_cut_json(raw if isinstance(raw, str) else "")


async def detect_and_trim_filler(
    *,
    video_path: str,
    audio_path: str,
    duration: float,
    output_video: str,
    output_audio: str,
    enabled: bool = True,
    llm_generate=None,
    extract_audio=None,
) -> dict[str, Any]:
    """Detect head/tail filler and trim copies. Never overwrites the original video."""
    from pathlib import Path

    empty = {
        "applied": False,
        "start_sec": 0.0,
        "end_sec": float(duration or 0.0),
        "original_duration": float(duration or 0.0),
        "leading_filler_sec": 0.0,
        "trailing_filler_sec": 0.0,
        "reason": "disabled" if not enabled else "no_cut",
        "video_path": video_path,
        "audio_path": audio_path,
        "notice": "",
        "original_video_path": video_path,
    }
    if not enabled:
        return empty
    if not video_path or not Path(video_path).is_file():
        empty["reason"] = "missing_video"
        return empty

    silences = await probe_silence_intervals(audio_path, duration) if audio_path and Path(audio_path).is_file() else []
    speech = speech_intervals_from_silence(duration, silences)
    still = await probe_freeze_intervals(video_path, duration)
    plan = propose_content_window(duration, speech_intervals=speech, still_intervals=still)
    ai = await classify_edges_with_llm(duration, speech, llm_generate=llm_generate)
    if ai:
        plan = merge_ai_cut_hints(plan, ai)

    if not plan.get("applied"):
        empty.update(plan)
        empty["video_path"] = video_path
        empty["audio_path"] = audio_path
        empty["original_video_path"] = video_path
        empty["notice"] = ""
        return empty

    from app.media.ffmpeg import trim_video_window_async

    out_v = Path(output_video)
    await trim_video_window_async(Path(video_path), out_v, plan["start_sec"], plan["end_sec"])
    audio_out = audio_path
    if extract_audio and out_v.is_file():
        await extract_audio(out_v, Path(output_audio))
        audio_out = str(Path(output_audio))

    plan["video_path"] = str(out_v)
    plan["audio_path"] = audio_out
    plan["original_video_path"] = video_path
    plan["notice"] = format_trim_notice(plan)
    return plan


def format_trim_notice(plan: dict[str, Any]) -> str:
    """Human-readable trim summary for the timeline."""
    if not plan or not plan.get("applied"):
        return ""
    orig = float(plan.get("original_duration") or 0)
    start = float(plan.get("start_sec") or 0)
    end = float(plan.get("end_sec") or orig)

    def _fmt(sec: float) -> str:
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m:02d}:{s:02d}"

    return f"Đã cắt intro/outro thừa: {_fmt(orig)} → {_fmt(end - start)} (giữ {_fmt(start)}–{_fmt(end)})"
