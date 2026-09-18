import pytest
from app.services.video_translator.stt_parser import parse_gemini_stt_response, _normalize_stt_schema

def test_stt_parser_extracts_speaker_id():
    json_response = """
    {
      "language": "Vietnamese",
      "segments": [
        {"start_time": 0.0, "end_time": 2.5, "speaker_id": "Speaker 1", "text": "Xin chào mọi người"},
        {"start_time": 3.0, "end_time": 5.0, "speaker_id": "Speaker 2", "text": "Chào bạn"}
      ]
    }
    """
    result = parse_gemini_stt_response(json_response)
    
    assert result["language"] == "Vietnamese"
    assert len(result["segments"]) == 2
    assert result["segments"][0]["speaker_id"] == "Speaker 1"
    assert result["segments"][1]["speaker_id"] == "Speaker 2"

def test_normalize_schema_fallback_unresolved():
    # If speaker_id is missing, it should fallback to UNRESOLVED_xxxx
    segments = [
        {"start_time": 0.0, "end_time": 2.0, "text": "Hello"}
    ]
    result = _normalize_stt_schema({"segments": segments})
    
    assert result["segments"][0]["speaker_id"] == "UNRESOLVED_0001"
