"""
Automated unit & integration test suite for VideoAudioSyncService.
"""

import math
import struct
import tempfile
import wave
from pathlib import Path

import pytest

from app.services.video_translator.sync_service import (
    VideoAudioSyncService,
    build_atempo_filter_chain,
    SAMPLE_RATE,
    CHANNELS,
    SAMPLE_WIDTH,
    BYTES_PER_FRAME,
)


def create_dummy_wav(path: Path, duration_sec: float = 2.0, freq: float = 440.0):
    """Generate a valid 44.1kHz 16-bit stereo PCM WAV file with a sine wave tone."""
    path.parent.mkdir(parents=True, exist_ok=True)
    num_frames = int(round(duration_sec * SAMPLE_RATE))
    pcm_data = bytearray()

    for i in range(num_frames):
        t = i / SAMPLE_RATE
        sample_val = int(16000 * math.sin(2 * math.pi * freq * t))
        # Pack 16-bit stereo (left and right channels)
        frame = struct.pack("<hh", sample_val, sample_val)
        pcm_data.extend(frame)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)


def test_build_atempo_filter_chain():
    assert build_atempo_filter_chain(1.0) == "atempo=1.0"
    assert build_atempo_filter_chain(1.5) == "atempo=1.5000"
    assert build_atempo_filter_chain(2.5) == "atempo=2.0,atempo=1.2500"
    assert build_atempo_filter_chain(0.4) == "atempo=0.5,atempo=0.8000"


def test_build_dubbed_audio_timeline_gaps_and_alignment(tmp_path: Path):
    audio1_path = tmp_path / "seg1.wav"
    audio2_path = tmp_path / "seg2.wav"
    create_dummy_wav(audio1_path, duration_sec=2.0, freq=440.0)
    create_dummy_wav(audio2_path, duration_sec=2.0, freq=880.0)

    segments = [
        {"number": 1, "start_time": 2.0, "end_time": 4.0, "audio_path": str(audio1_path)},
        {"number": 2, "start_time": 6.0, "end_time": 8.0, "audio_path": str(audio2_path)},
    ]

    out_wav = tmp_path / "timeline.wav"
    total_video_duration = 10.0

    res = VideoAudioSyncService.build_dubbed_audio_timeline(
        segments=segments,
        total_video_duration=total_video_duration,
        output_wav_path=out_wav,
        job_id="TEST-JOB",
    )

    assert out_wav.exists()
    assert math.isclose(res["output_duration"], total_video_duration, abs_tol=0.01)
    assert len(res["overlap_warnings"]) == 0

    with wave.open(str(out_wav), "rb") as wf:
        assert wf.getframerate() == SAMPLE_RATE
        assert wf.getnchannels() == CHANNELS
        frames = wf.readframes(wf.getnframes())

    # Check initial margin (0.0s to 2.0s): must be pure silence (zero bytes)
    margin_1_bytes = int(2.0 * SAMPLE_RATE * BYTES_PER_FRAME)
    assert not any(frames[:margin_1_bytes]), "Initial 0-2s must be silence"

    # Check segment 1 (2.0s to 4.0s): must contain non-zero audio samples
    seg_1_start_byte = margin_1_bytes
    seg_1_end_byte = int(4.0 * SAMPLE_RATE * BYTES_PER_FRAME)
    assert any(frames[seg_1_start_byte:seg_1_end_byte]), "Segment 1 audio must be present"

    # Check silence gap between segments (4.0s to 6.0s): must be pure silence
    gap_start_byte = seg_1_end_byte
    gap_end_byte = int(6.0 * SAMPLE_RATE * BYTES_PER_FRAME)
    assert not any(frames[gap_start_byte:gap_end_byte]), "Gap 4s-6s must be silence"

    # Check segment 2 (6.0s to 8.0s): must contain non-zero audio samples
    seg_2_start_byte = gap_end_byte
    seg_2_end_byte = int(8.0 * SAMPLE_RATE * BYTES_PER_FRAME)
    assert any(frames[seg_2_start_byte:seg_2_end_byte]), "Segment 2 audio must be present"

    # Check trailing silence (8.0s to 10.0s): must be pure silence
    assert not any(frames[seg_2_end_byte:]), "Trailing 8s-10s must be silence"


def test_build_dubbed_audio_timeline_overlap_detection(tmp_path: Path):
    audio1_path = tmp_path / "seg1.wav"
    audio2_path = tmp_path / "seg2.wav"
    create_dummy_wav(audio1_path, duration_sec=3.0, freq=440.0)
    create_dummy_wav(audio2_path, duration_sec=2.0, freq=880.0)

    # Overlapping segments: segment 1 ends at 5.0s, segment 2 starts at 4.0s
    segments = [
        {"number": 1, "start_time": 2.0, "end_time": 5.0, "audio_path": str(audio1_path)},
        {"number": 2, "start_time": 4.0, "end_time": 6.0, "audio_path": str(audio2_path)},
    ]

    out_wav = tmp_path / "timeline_overlap.wav"
    res = VideoAudioSyncService.build_dubbed_audio_timeline(
        segments=segments,
        total_video_duration=8.0,
        output_wav_path=out_wav,
        job_id="TEST-OVERLAP",
    )

    assert len(res["overlap_warnings"]) > 0
    assert "OVERLAPPING_SEGMENTS" in res["overlap_warnings"][0]
