from app.models.video_translator import TranslationJobStatus, VideoTranslationSegment
from app.models.workflow_engine import CharacterVoiceProfile, SpeakerVoiceMapping, VoicePoolEntry


def test_character_voice_schema_exposes_persistent_contract():
    assert TranslationJobStatus.NEEDS_REVIEW.value == "needs_review"
    assert {"character_id", "confidence", "needs_review"} <= set(SpeakerVoiceMapping.__table__.columns.keys())
    assert {
        "speaker_id", "character_id", "voice_provider", "voice_id",
        "original_start", "original_end", "scheduled_start", "scheduled_end",
        "tts_duration", "overlap_with", "schedule_action", "mapping_confidence",
    } <= set(VideoTranslationSegment.__table__.columns.keys())
    assert CharacterVoiceProfile.__tablename__ == "character_voice_profiles"
    assert VoicePoolEntry.__tablename__ == "voice_pool_entries"


def test_original_timeline_is_independent_from_scheduled_timeline():
    segment = VideoTranslationSegment(
        job_id="job-1", segment_number=1, start_time=1.0, end_time=2.0,
        original_start=1.0, original_end=2.0,
        scheduled_start=1.25, scheduled_end=2.75,
    )
    assert (segment.original_start, segment.original_end) == (1.0, 2.0)
    assert (segment.scheduled_start, segment.scheduled_end) == (1.25, 2.75)
