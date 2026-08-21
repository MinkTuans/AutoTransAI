"""
Unit tests for the script parser.

Tests multiple formats, edge cases, and validation.
"""

import pytest

from app.services.script_parser import parse_script, validate_segments, ParsedSegment
from app.core.exceptions import InvalidScriptError, EmptyScriptError


class TestParseScriptVietnamese:
    """Tests for 'Phân đoạn N:' format."""

    def test_basic_phan_doan(self):
        script = """Phân đoạn 1: Hello everyone, welcome to the show.
Phân đoạn 2: Today we are going to talk about AI.
Phân đoạn 3: Let's get started."""
        result = parse_script(script)
        assert len(result) == 3
        assert result[0].number == 1
        assert "Hello everyone" in result[0].text
        assert result[2].number == 3

    def test_phan_doan_with_dot(self):
        script = """Phân đoạn 1. First segment here.
Phân đoạn 2. Second segment here."""
        result = parse_script(script)
        assert len(result) == 2

    def test_phan_doan_case_insensitive(self):
        script = """phân đoạn 1: First one.
PHÂN ĐOẠN 2: Second one."""
        result = parse_script(script)
        assert len(result) == 2


class TestParseScriptEnglish:
    """Tests for 'Segment N:' format."""

    def test_basic_segment(self):
        script = """Segment 1: Hello everyone.
Segment 2: Today we discuss AI.
Segment 3: Thank you."""
        result = parse_script(script)
        assert len(result) == 3
        assert result[0].number == 1

    def test_segment_case_insensitive(self):
        script = """segment 1: Hello.
SEGMENT 2: World."""
        result = parse_script(script)
        assert len(result) == 2


class TestParseScriptNumbered:
    """Tests for 'N: ...' and 'N. ...' formats."""

    def test_number_colon(self):
        script = """1: Hello everyone.
2: Today we talk.
3: Goodbye."""
        result = parse_script(script)
        assert len(result) == 3
        assert result[0].number == 1
        assert result[2].number == 3

    def test_number_dot(self):
        script = """1. Hello everyone.
2. Today we talk.
3. Goodbye."""
        result = parse_script(script)
        assert len(result) == 3


class TestParseScriptFallback:
    """Tests for paragraph fallback mode."""

    def test_double_newline_split(self):
        script = """Hello everyone, welcome.

Today we are going to talk about something amazing.

Thank you for watching."""
        result = parse_script(script)
        assert len(result) == 3
        assert result[0].number == 1  # Auto-numbered

    def test_single_paragraph(self):
        script = "Just one paragraph with no breaks."
        result = parse_script(script)
        assert len(result) == 1


class TestParseScriptEdgeCases:
    """Edge cases and error handling."""

    def test_empty_string(self):
        with pytest.raises(InvalidScriptError):
            parse_script("")

    def test_whitespace_only(self):
        with pytest.raises(InvalidScriptError):
            parse_script("   \n\n   ")

    def test_unicode_text(self):
        script = """Phân đoạn 1: Xin chào tất cả mọi người.
Phân đoạn 2: Hôm nay chúng ta sẽ nói về AI."""
        result = parse_script(script)
        assert len(result) == 2
        assert "Xin chào" in result[0].text

    def test_char_count_accurate(self):
        script = "Segment 1: Hello World"
        result = parse_script(script)
        assert result[0].char_count == len(result[0].text)

    def test_multiline_segment(self):
        script = """Segment 1: This is a long segment
that spans multiple lines
and keeps going.
Segment 2: Short one."""
        result = parse_script(script)
        assert len(result) == 2
        assert "multiple lines" in result[0].text


class TestValidateSegments:
    """Tests for segment validation warnings."""

    def test_no_warnings_for_normal(self):
        segments = [
            ParsedSegment(number=1, text="A" * 100, char_count=100),
            ParsedSegment(number=2, text="B" * 200, char_count=200),
        ]
        warnings = validate_segments(segments)
        assert len(warnings) == 0

    def test_warns_short_text(self):
        segments = [
            ParsedSegment(number=1, text="Hi", char_count=2),
        ]
        warnings = validate_segments(segments)
        assert any("very short" in w for w in warnings)

    def test_warns_long_text(self):
        segments = [
            ParsedSegment(number=1, text="A" * 6000, char_count=6000),
        ]
        warnings = validate_segments(segments)
        assert any("very long" in w for w in warnings)

    def test_warns_duplicate_numbers(self):
        segments = [
            ParsedSegment(number=1, text="First", char_count=5),
            ParsedSegment(number=1, text="Duplicate", char_count=9),
        ]
        warnings = validate_segments(segments)
        assert any("Duplicate" in w for w in warnings)

    def test_empty_list(self):
        warnings = validate_segments([])
        assert len(warnings) == 1
