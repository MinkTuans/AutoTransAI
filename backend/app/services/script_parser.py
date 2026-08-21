"""
Script parser — converts raw script text into structured segments.

Supports multiple formats:
  - "Phân đoạn N: ..."
  - "Segment N: ..."
  - "N. ..." (numbered list)
  - "N: ..." (number-colon)
  - Double-newline separated paragraphs (fallback)
"""

import re
from dataclasses import dataclass

from app.core import get_logger
from app.core.exceptions import EmptyScriptError, InvalidScriptError

logger = get_logger(__name__)


@dataclass
class ParsedSegment:
    """A single parsed segment from a script."""
    number: int
    text: str
    char_count: int


# Patterns tried in order of specificity
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # "Phân đoạn N: text" or "Phân đoạn N. text"
    ("phan_doan", re.compile(
        r"Phân\s+đoạn\s+(\d+)\s*[:\.]\s*(.+?)(?=Phân\s+đoạn\s+\d+|$)",
        re.DOTALL | re.IGNORECASE,
    )),
    # "Segment N: text" or "Segment N. text"
    ("segment", re.compile(
        r"Segment\s+(\d+)\s*[:\.]\s*(.+?)(?=Segment\s+\d+|$)",
        re.DOTALL | re.IGNORECASE,
    )),
    # "N: text" (number-colon at start of line)
    ("number_colon", re.compile(
        r"^(\d+)\s*[:\.]\s*(.+?)(?=^\d+\s*[:\.]|$)",
        re.DOTALL | re.MULTILINE,
    )),
]


def parse_script(raw_script: str) -> list[ParsedSegment]:
    """
    Parse a raw script string into a list of segments.

    Tries structured patterns first, then falls back to paragraph splitting.

    Args:
        raw_script: The raw script text.

    Returns:
        List of ParsedSegment objects.

    Raises:
        InvalidScriptError: If the script is malformed.
        EmptyScriptError: If no segments are found.
    """
    if not raw_script or not raw_script.strip():
        raise InvalidScriptError("Script is empty")

    cleaned = raw_script.strip()

    # Try each structured pattern
    for pattern_name, pattern in _PATTERNS:
        matches = pattern.findall(cleaned)
        if matches:
            logger.info(
                "Script parsed with pattern",
                pattern=pattern_name,
                segment_count=len(matches),
            )
            segments = []
            for i, (num_str, text) in enumerate(matches):
                text = text.strip()
                if text:
                    segments.append(ParsedSegment(
                        number=int(num_str),
                        text=text,
                        char_count=len(text),
                    ))
            if segments:
                return segments

    # Fallback: split by double newline (paragraph mode)
    paragraphs = re.split(r"\n\s*\n", cleaned)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if paragraphs:
        logger.info(
            "Script parsed with paragraph fallback",
            segment_count=len(paragraphs),
        )
        return [
            ParsedSegment(number=i + 1, text=p, char_count=len(p))
            for i, p in enumerate(paragraphs)
        ]

    raise EmptyScriptError()


def validate_segments(segments: list[ParsedSegment]) -> list[str]:
    """
    Validate parsed segments and return a list of warnings.

    Returns:
        List of warning strings (empty if no issues).
    """
    warnings: list[str] = []

    if not segments:
        return ["No segments found"]

    for seg in segments:
        if seg.char_count < 5:
            warnings.append(
                f"Segment {seg.number}: very short text ({seg.char_count} chars)"
            )
        if seg.char_count > 5000:
            warnings.append(
                f"Segment {seg.number}: very long text ({seg.char_count} chars), "
                "may produce long audio"
            )

    # Check for duplicate segment numbers
    numbers = [s.number for s in segments]
    if len(numbers) != len(set(numbers)):
        warnings.append("Duplicate segment numbers detected")

    return warnings
