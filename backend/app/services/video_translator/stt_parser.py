"""
Robust Gemini Speech-to-Text Response Parser & Schema Normalizer.

Handles non-strict JSON outputs, markdown code fences, outer conversational text,
trailing commas, invalid string escaping, non-standard field key schemas, and
plain-text/dialogue transcript fallback formats.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_gemini_stt_response(
    response_text: str,
    actual_chunk_dur: float = 0.0,
    default_lang: str = "English",
) -> Dict[str, Any]:
    """
    Parse Gemini STT response text into standardized format:
    {
        "language": "English",
        "segments": [
            {"start_time": 0.0, "end_time": 4.5, "text": "Sentence text"}
        ]
    }
    """
    if not response_text or not response_text.strip():
        logger.error("[Gemini STT Parse Error] Empty or whitespace response received.")
        raise ValueError("Gemini STT response is empty")

    raw_text = response_text.strip()
    parsed_obj: Optional[Any] = None

    # Stage A: Strict JSON parse
    try:
        parsed_obj = json.loads(raw_text)
    except Exception:
        parsed_obj = None

    # Stage B: Markdown Code Block stripping (```json ... ``` or ``` ... ```)
    if parsed_obj is None:
        code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text, re.IGNORECASE)
        if code_block_match:
            inner_code = code_block_match.group(1).strip()
            try:
                parsed_obj = json.loads(inner_code)
            except Exception:
                parsed_obj = _try_repair_json(inner_code)

    # Stage C: Regex Extract Object or Array
    if parsed_obj is None:
        obj_match = re.search(r"\{[\s\S]*\}", raw_text)
        if obj_match:
            try:
                parsed_obj = json.loads(obj_match.group(0))
            except Exception:
                parsed_obj = _try_repair_json(obj_match.group(0))

    if parsed_obj is None:
        arr_match = re.search(r"\[[\s\S]*\]", raw_text)
        if arr_match:
            try:
                parsed_obj = json.loads(arr_match.group(0))
            except Exception:
                parsed_obj = _try_repair_json(arr_match.group(0))

    # Stage D: Direct Sanitize Repair on raw_text
    if parsed_obj is None:
        parsed_obj = _try_repair_json(raw_text)

    # Stage E: Fallback Text Parser if JSON parsing failed completely
    if parsed_obj is None:
        logger.warning(
            f"[Gemini STT Parse Warning] JSON parsing failed. Attempting Plain Text Fallback Parser. "
            f"Raw text snippet: {raw_text[:200]!r}"
        )
        parsed_obj = _parse_plain_text_fallback(raw_text, actual_chunk_dur, default_lang)

    # Stage F: Schema Normalization
    normalized = _normalize_stt_schema(parsed_obj, actual_chunk_dur, default_lang)

    if not normalized.get("segments") and raw_text:
        # Last resort: try plain text fallback if schema normalization yielded 0 segments
        fallback_obj = _parse_plain_text_fallback(raw_text, actual_chunk_dur, default_lang)
        normalized = _normalize_stt_schema(fallback_obj, actual_chunk_dur, default_lang)

    if not normalized.get("segments"):
        logger.error(f"[Gemini STT Parse Error] Failed to parse valid segments. Raw response:\n{raw_text[:1000]}")
        raise ValueError(f"Gemini STT response could not be parsed into valid segments. Raw response snippet: {raw_text[:200]!r}")

    return normalized


def _try_repair_json(text: str) -> Optional[Any]:
    """Sanitize and repair common malformed JSON issues."""
    if not text:
        return None

    s = text.strip()

    # 1. Remove trailing commas before } or ]
    s = re.sub(r",\s*([\}\]])", r"\1", s)

    # 2. Fix unescaped control newlines/tabs inside quotes
    def replace_newlines_in_quotes(match: re.Match) -> str:
        content = match.group(0)
        return content.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")

    s_clean = re.sub(r'"([^"\\]|\\.)*"', replace_newlines_in_quotes, s)

    try:
        return json.loads(s_clean)
    except Exception:
        pass

    # 3. Replace Python literal booleans/None
    try:
        s_py = re.sub(r"\bTrue\b", "true", s_clean)
        s_py = re.sub(r"\bFalse\b", "false", s_py)
        s_py = re.sub(r"\bNone\b", "null", s_py)
        return json.loads(s_py)
    except Exception:
        pass

    return None


def _parse_plain_text_fallback(text: str, chunk_dur: float, default_lang: str) -> Dict[str, Any]:
    """Parse timestamped lines or plain text dialogue when AI returns non-JSON text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    segments: List[Dict[str, Any]] = []

    ts_pattern = re.compile(
        r"^(?:\[?\s*((?:\d+:)*\d+(?:\.\d+)?)\s*(?:-|to|->)\s*((?:\d+:)*\d+(?:\.\d+)?)\s*\]?:?\s*)?(.*)$",
        re.IGNORECASE,
    )

    def parse_time(t_str: str) -> float:
        if not t_str:
            return 0.0
        t_str = t_str.rstrip("sS").strip()
        if ":" in t_str:
            parts = t_str.split(":")
            if len(parts) == 2:
                return float(parts[0]) * 60.0 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        try:
            return float(t_str)
        except ValueError:
            return 0.0

    for line in lines:
        if line.startswith("#") or line.lower().startswith("here is") or line.startswith("```"):
            continue

        match = ts_pattern.match(line)
        if match:
            st_str, et_str, txt = match.groups()
            txt = (txt or "").strip()
            if not txt:
                continue

            st = parse_time(st_str) if st_str else 0.0
            et = parse_time(et_str) if et_str else (st + 4.0)

            if chunk_dur > 0 and et > chunk_dur:
                et = min(et, chunk_dur)

            segments.append({
                "start_time": st,
                "end_time": max(st + 0.5, et),
                "text": txt,
            })

    if not segments:
        clean_text = " ".join([l for l in lines if not l.startswith("#") and not l.startswith("```")]).strip()
        if clean_text:
            segments.append({
                "start_time": 0.0,
                "end_time": chunk_dur if chunk_dur > 0 else 4.0,
                "text": clean_text,
            })

    return {
        "language": default_lang,
        "segments": segments,
    }


def _normalize_stt_schema(obj: Any, chunk_dur: float = 0.0, default_lang: str = "English") -> Dict[str, Any]:
    """Normalize arbitrary JSON dicts or lists into standardized STT schema."""
    if obj is None:
        return {"language": default_lang, "segments": []}

    detected_lang = default_lang
    raw_segments: List[Any] = []

    if isinstance(obj, list):
        raw_segments = obj
    elif isinstance(obj, dict):
        for lang_key in ["language", "lang", "language_code", "detected_language", "locale"]:
            if lang_key in obj and isinstance(obj[lang_key], str) and obj[lang_key].strip():
                detected_lang = obj[lang_key].strip()
                break

        for seg_key in ["segments", "items", "transcript", "transcripts", "data", "results", "sentences", "dialogue", "content"]:
            val = obj.get(seg_key)
            if isinstance(val, list):
                raw_segments = val
                break
            elif isinstance(val, str) and val.strip():
                raw_segments = [{"start_time": 0.0, "end_time": chunk_dur or 4.0, "text": val.strip()}]
                break

    norm_segments: List[Dict[str, Any]] = []
    if isinstance(raw_segments, list):
        for s in raw_segments:
            if isinstance(s, dict):
                txt = ""
                for txt_key in ["text", "content", "transcript", "sentence", "val", "line"]:
                    if txt_key in s and s[txt_key] is not None:
                        txt = str(s[txt_key]).strip()
                        break

                if not txt:
                    continue

                st = 0.0
                for st_key in ["start_time", "start", "from", "begin", "timestamp_start"]:
                    if st_key in s and s[st_key] is not None:
                        try:
                            st = float(s[st_key])
                            break
                        except (ValueError, TypeError):
                            pass

                et = st + 4.0
                for et_key in ["end_time", "end", "to", "timestamp_end"]:
                    if et_key in s and s[et_key] is not None:
                        try:
                            et = float(s[et_key])
                            break
                        except (ValueError, TypeError):
                            pass

                norm_segments.append({
                    "start_time": max(0.0, st),
                    "end_time": max(st + 0.1, et),
                    "text": txt,
                })
            elif isinstance(s, str) and s.strip():
                norm_segments.append({
                    "start_time": 0.0,
                    "end_time": chunk_dur or 4.0,
                    "text": s.strip(),
                })

    return {
        "language": detected_lang,
        "segments": norm_segments,
    }
