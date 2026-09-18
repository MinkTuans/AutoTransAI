from app.services.video_translator.voice_assignment_service import assign_voices


POOL = [
    {"provider": "edge_tts", "voice_id": "vi-VN-NamMinhNeural", "gender": "male", "language": "vi-VN"},
    {"provider": "edge_tts", "voice_id": "vi-VN-HoaiMyNeural", "gender": "female", "language": "vi-VN"},
    {"provider": "edge_tts", "voice_id": "vi-VN-PhuongNamNeural", "gender": "male", "language": "vi-VN"},
    {"provider": "edge_tts", "voice_id": "en-US-GuyNeural", "gender": "male", "language": "en-US"},
]


def test_assigns_vietnamese_main_voices_and_distinct_supporting_voice():
    chars = [{"character_id": "m", "gender": "male", "role": "main"}, {"character_id": "f", "gender": "female", "role": "main"}, {"character_id": "s", "gender": "male", "role": "supporting"}]
    result = assign_voices(chars, POOL, {("m", "s")})
    assert result.assignments["m"]["voice_id"] == "vi-VN-NamMinhNeural"
    assert result.assignments["f"]["voice_id"] == "vi-VN-HoaiMyNeural"
    assert result.assignments["s"]["voice_id"] == "vi-VN-PhuongNamNeural"


def test_confirmed_profile_is_never_changed_on_conflict():
    chars = [{"character_id": "a", "gender": "male", "role": "main"}, {"character_id": "b", "gender": "male", "role": "supporting"}]
    profiles = {"a": {"voice_provider": "edge_tts", "voice_id": "same", "confirmed_by_user": True}, "b": {"voice_provider": "edge_tts", "voice_id": "same", "confirmed_by_user": True}}
    result = assign_voices(chars, POOL, {("a", "b")}, profiles)
    assert result.requires_review is True
    assert result.assignments["a"]["voice_id"] == result.assignments["b"]["voice_id"] == "same"


def test_assigns_custom_default_male_and_female_voices():
    chars = [
        {"character_id": "c_male", "gender": "male", "role": "supporting"},
        {"character_id": "c_female", "gender": "female", "role": "supporting"},
    ]
    # Pass custom default male voice vi-VN-PhuongNamNeural
    result = assign_voices(
        chars,
        POOL,
        set(),
        target_language="vi",
        default_male_voice_id="vi-VN-PhuongNamNeural",
        default_female_voice_id="vi-VN-HoaiMyNeural",
    )
    assert result.assignments["c_male"]["voice_id"] == "vi-VN-PhuongNamNeural"
    assert result.assignments["c_female"]["voice_id"] == "vi-VN-HoaiMyNeural"

