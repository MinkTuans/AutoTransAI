from app.services.video_translator.character_mapping_service import validate_character_mapping


def test_low_confidence_merge_keeps_speakers_separate_and_requires_review():
    result = validate_character_mapping(
        ["SPEAKER_00", "SPEAKER_01"],
        [{"character_id": "same", "speaker_ids": ["SPEAKER_00", "SPEAKER_01"], "confidence": 0.7}],
        threshold=0.85,
    )
    assert result.requires_review is True
    assert result.by_speaker["SPEAKER_00"]["character_id"] != result.by_speaker["SPEAKER_01"]["character_id"]


def test_high_confidence_merge_maps_both_speakers_to_one_character():
    result = validate_character_mapping(
        ["A", "B"], [{"character_id": "hero", "speaker_ids": ["A", "B"], "confidence": 0.95}], 0.85
    )
    assert result.requires_review is False
    assert result.by_speaker["A"]["character_id"] == result.by_speaker["B"]["character_id"]
