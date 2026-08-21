"""
Unit tests for the estimator.
"""

from app.services.estimator import estimate_project, estimate_audio_duration


class TestEstimateAudioDuration:
    def test_basic_estimate(self):
        duration = estimate_audio_duration(130)
        assert duration == 10.0  # 130 chars / 13 chars per sec

    def test_zero_chars(self):
        duration = estimate_audio_duration(0)
        assert duration == 0.0

    def test_large_text(self):
        duration = estimate_audio_duration(13000)
        assert duration == 1000.0


class TestEstimateProject:
    def test_audio_only(self):
        segments = [
            {"number": 1, "char_count": 130},
            {"number": 2, "char_count": 260},
        ]
        est = estimate_project(segments, "audio_only")
        assert est.total_segments == 2
        assert est.total_characters == 390
        assert est.estimated_audio_duration_seconds > 0
        assert est.estimated_video_clips == 0

    def test_audio_video(self):
        segments = [
            {"number": 1, "char_count": 100},
            {"number": 2, "char_count": 200},
            {"number": 3, "char_count": 150},
        ]
        est = estimate_project(segments, "audio_video")
        assert est.total_segments == 3
        assert est.estimated_video_clips == 3
        assert est.estimated_video_seconds == 24.0  # 3 * 8 sec default

    def test_custom_video_duration(self):
        segments = [{"number": 1, "char_count": 100}]
        est = estimate_project(segments, "audio_video", video_target_duration=10)
        assert est.estimated_video_seconds == 10.0

    def test_token_estimation(self):
        segments = [{"number": 1, "char_count": 400}]
        est = estimate_project(segments, "audio_only")
        assert est.estimated_input_tokens == 100  # 400 / 4

    def test_empty_segments(self):
        est = estimate_project([], "audio_only")
        assert est.total_segments == 0
        assert est.total_characters == 0
