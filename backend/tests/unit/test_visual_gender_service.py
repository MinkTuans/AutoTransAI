import pytest
import asyncio
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.services.video_translator.visual_gender_service import detect_speakers_gender

@pytest.mark.asyncio
async def test_detect_speakers_gender_logic(tmp_path):
    # Mock video path
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.touch()

    segments = [
        {"speaker_id": "Speaker 1", "start_time": 0.0, "end_time": 2.0},
        {"speaker_id": "Speaker 1", "start_time": 5.0, "end_time": 10.0}, # Longest segment for Speaker 1 (5s)
        {"speaker_id": "Speaker 2", "start_time": 12.0, "end_time": 14.0}, # Longest for Speaker 2 (2s)
        {"speaker_id": "UNRESOLVED_0001", "start_time": 15.0, "end_time": 16.0}, # Should be skipped
    ]

    async def mock_extract(video_path, timestamp, output_path):
        Path(output_path).touch() # Simulate successful extraction

    async def mock_detect(image_path):
        if "Speaker 1" in image_path:
            return "male"
        elif "Speaker 2" in image_path:
            return "female"
        return "unknown"

    with patch("app.services.video_translator.visual_gender_service.extract_speaker_keyframe", side_effect=mock_extract) as extract_mock:
        with patch("app.services.video_translator.visual_gender_service.detect_gender_from_image", side_effect=mock_detect):
            results = await detect_speakers_gender(str(dummy_video), segments)

            assert "Speaker 1" in results
            assert results["Speaker 1"] == "male"
            assert "Speaker 2" in results
            assert results["Speaker 2"] == "female"
            assert "UNRESOLVED_0001" not in results

            # Verify extract was called with correct midpoints
            # Speaker 1: 5.0 to 10.0 -> mid is 7.5
            # Speaker 2: 12.0 to 14.0 -> mid is 13.0
            calls = extract_mock.call_args_list
            assert len(calls) == 2
            
            # Since dictionary iteration order is preserved in Python 3.7+,
            # let's just check if both midpoints were called
            midpoints = [call[0][1] for call in calls]
            assert 7.5 in midpoints
            assert 13.0 in midpoints

@pytest.mark.asyncio
async def test_detect_speakers_gender_missing_video():
    results = await detect_speakers_gender("invalid_path.mp4", [{"speaker_id": "Speaker 1"}])
    assert results == {}
