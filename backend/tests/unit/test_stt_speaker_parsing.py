from app.services.video_translator.stt_parser import parse_gemini_stt_response


def test_preserves_existing_speaker_information():
    result = parse_gemini_stt_response(
        '{"segments":[{"start":0,"end":1,"text":"A","speaker":"SPEAKER_03"}]}', 1.0
    )
    assert result["segments"][0]["speaker_id"] == "SPEAKER_03"


def test_missing_speakers_stay_separate_and_unresolved():
    result = parse_gemini_stt_response(
        '{"segments":[{"start":0,"end":1,"text":"A"},{"start":1,"end":2,"text":"B"}]}', 2.0
    )
    assert [s["speaker_id"] for s in result["segments"]] == ["UNRESOLVED_0001", "UNRESOLVED_0002"]
