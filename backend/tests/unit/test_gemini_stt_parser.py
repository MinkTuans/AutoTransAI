"""
Unit tests for robust Gemini Speech-to-Text response parser (stt_parser.py).
"""

import pytest
from app.services.video_translator.stt_parser import parse_gemini_stt_response


def test_parse_valid_strict_json():
    """1. Test parsing valid strict JSON response."""
    raw = '{\n  "language": "Vietnamese",\n  "segments": [\n    {"start_time": 0.0, "end_time": 3.5, "text": "Xin chào thế giới"}\n  ]\n}'
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0)
    assert res["language"] == "Vietnamese"
    assert len(res["segments"]) == 1
    assert res["segments"][0]["text"] == "Xin chào thế giới"
    assert res["segments"][0]["start_time"] == 0.0
    assert res["segments"][0]["end_time"] == 3.5


def test_parse_markdown_code_block():
    """2. Test parsing JSON enclosed in markdown code fences."""
    raw = '```json\n{\n  "language": "English",\n  "segments": [\n    {"start_time": 1.0, "end_time": 4.0, "text": "Hello in markdown"}\n  ]\n}\n```'
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0)
    assert res["language"] == "English"
    assert len(res["segments"]) == 1
    assert res["segments"][0]["text"] == "Hello in markdown"


def test_parse_surrounding_conversational_text():
    """3. Test parsing JSON wrapped with conversational text before and after."""
    raw = (
        "Here is the transcription for your audio file chunk:\n\n"
        "```json\n"
        '{\n  "language": "Japanese",\n  "segments": [\n    {"start_time": 0.5, "end_time": 2.5, "text": "Konnichiwa"}\n  ]\n}\n'
        "```\n\n"
        "Hope this transcript is helpful!"
    )
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0)
    assert res["language"] == "Japanese"
    assert len(res["segments"]) == 1
    assert res["segments"][0]["text"] == "Konnichiwa"


def test_parse_trailing_commas_and_unescaped_newlines():
    """4. Test repairing JSON with trailing commas and control characters inside strings."""
    raw = (
        '{\n'
        '  "language": "English",\n'
        '  "segments": [\n'
        '    {"start_time": 0.0, "end_time": 4.0, "text": "Line with\nnewline inside",},\n'
        '  ],\n'
        '}'
    )
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0)
    assert res["language"] == "English"
    assert len(res["segments"]) == 1
    assert "Line with" in res["segments"][0]["text"]


def test_parse_plain_text_dialogue_fallback():
    """5. Test fallback parsing when Gemini returns plain text / timestamped dialogue instead of JSON."""
    raw = (
        "Here is what was spoken:\n"
        "[00:00 - 00:03] Welcome to our video.\n"
        "[00:04 - 00:08] Today we will discuss AI STT features.\n"
    )
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0, default_lang="English")
    assert res["language"] == "English"
    assert len(res["segments"]) == 2
    assert res["segments"][0]["text"] == "Welcome to our video."
    assert res["segments"][0]["start_time"] == 0.0
    assert res["segments"][0]["end_time"] == 3.0
    assert res["segments"][1]["text"] == "Today we will discuss AI STT features."
    assert res["segments"][1]["start_time"] == 4.0
    assert res["segments"][1]["end_time"] == 8.0


def test_parse_alternative_schema_keys():
    """6. Test schema normalization when Gemini returns non-standard keys like items, transcript, language_code."""
    raw = (
        '{\n'
        '  "language_code": "fr",\n'
        '  "items": [\n'
        '    {"start": 0.2, "end": 2.8, "content": "Bonjour tout le monde"}\n'
        '  ]\n'
        '}'
    )
    res = parse_gemini_stt_response(raw, actual_chunk_dur=10.0)
    assert res["language"] == "fr"
    assert len(res["segments"]) == 1
    assert res["segments"][0]["text"] == "Bonjour tout le monde"
    assert res["segments"][0]["start_time"] == 0.2
    assert res["segments"][0]["end_time"] == 2.8


def test_parse_completely_invalid_empty_response():
    """7. Test handling of completely empty or invalid response, raising ValueError."""
    with pytest.raises(ValueError) as exc_info:
        parse_gemini_stt_response("", actual_chunk_dur=10.0)
    assert "empty" in str(exc_info.value).lower()

    with pytest.raises(ValueError) as exc_info2:
        parse_gemini_stt_response("   \n\t  ", actual_chunk_dur=10.0)
    assert "empty" in str(exc_info2.value).lower()
