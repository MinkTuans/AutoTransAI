"""Video wrapper around the isolated Gemini Live audio translation path."""

import asyncio
import io
import json
import shutil
import subprocess
import wave

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _wav(seconds: float) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\0\0" * int(24000 * seconds))
    return buffer.getvalue()


def _sample_video(path, *, with_audio=True, seconds=2):
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
               "-i", f"color=c=blue:s=64x64:r=10:d={seconds}"]
    if with_audio:
        command += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"]
    command += ["-c:v", "mpeg4", "-q:v", "3"]
    if with_audio:
        command += ["-c:a", "aac", "-shortest"]
    command += [str(path)]
    subprocess.run(command, check=True, capture_output=True)


@pytest.mark.asyncio
async def test_video_adapter_extracts_pcm_and_muxes_full_video(tmp_path):
    from app.services.live_audio_translation.video import extract_video_pcm, mux_translated_video

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required")
    source = tmp_path / "source.mp4"
    _sample_video(source)
    pcm = tmp_path / "input.pcm"
    duration = await extract_video_pcm(source, pcm, max_seconds=300)
    assert 1.8 <= duration <= 2.2
    assert pcm.stat().st_size >= 32000 * 1.8
    translated = tmp_path / "translated.wav"
    translated.write_bytes(_wav(1))
    result = tmp_path / "translated.mp4"
    await mux_translated_video(source, translated, result)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=codec_type,codec_name", "-of", "json", str(result)],
                           check=True, capture_output=True, text=True)
    info = json.loads(probe.stdout)
    assert float(info["format"]["duration"]) >= 1.9
    assert [stream["codec_type"] for stream in info["streams"]] == ["video", "audio"]
    assert info["streams"][0]["codec_name"] == "mpeg4"
    assert info["streams"][1]["codec_name"] == "aac"


@pytest.mark.asyncio
async def test_video_adapter_rejects_no_audio_and_long_video(tmp_path):
    from app.services.live_audio_translation.audio import AudioInputError
    from app.services.live_audio_translation.video import extract_video_pcm

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required")
    source = tmp_path / "silent.mp4"
    _sample_video(source, with_audio=False)
    with pytest.raises(AudioInputError) as error:
        await extract_video_pcm(source, tmp_path / "input.pcm", max_seconds=300)
    assert error.value.code == "video_has_no_audio"
    source = tmp_path / "long.mp4"
    _sample_video(source, seconds=2)
    with pytest.raises(AudioInputError) as error:
        await extract_video_pcm(source, tmp_path / "input.pcm", max_seconds=1)
    assert error.value.code == "session_limit"


@pytest.mark.asyncio
async def test_video_probe_keeps_converter_timeout_error(tmp_path, monkeypatch):
    from app.services.live_audio_translation import video
    from app.services.live_audio_translation.audio import AudioInputError

    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic")
    async def timeout(*_args, **_kwargs):
        raise AudioInputError("conversion_timeout")
    monkeypatch.setattr(video, "_run", timeout)
    with pytest.raises(AudioInputError) as error:
        await video.extract_video_pcm(source, tmp_path / "input.pcm", max_seconds=300)
    assert error.value.code == "conversion_timeout"


@pytest.mark.asyncio
async def test_video_mux_keeps_translated_speech_longer_than_source_video(tmp_path):
    from app.services.live_audio_translation.video import mux_translated_video

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required")
    source = tmp_path / "source.mp4"
    _sample_video(source)
    translated = tmp_path / "translated.wav"
    translated.write_bytes(_wav(3))
    output = tmp_path / "translated.mp4"
    await mux_translated_video(source, translated, output)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_type,duration", "-of", "json", str(output)],
                           check=True, capture_output=True, text=True)
    streams = json.loads(probe.stdout)["streams"]
    audio = next(stream for stream in streams if stream["codec_type"] == "audio")
    assert float(audio["duration"]) >= 2.95


@pytest.mark.asyncio
async def test_live_video_route_returns_mp4_and_removes_temporary_files(tmp_path, monkeypatch):
    from app.api.routes import live_audio_translation as routes
    from app.services.live_audio_translation.jobs import LiveJobManager

    config = type("Config", (), {"LIVE_AUDIO_TRANSLATION_ENABLED": True,
                                 "GEMINI_LIVE_TRANSLATE_API_KEY": "synthetic-key",
                                 "GEMINI_LIVE_TRANSLATE_MODEL": "synthetic-model",
                                 "STORAGE_ROOT": tmp_path})()
    monkeypatch.setattr(routes, "get_settings", lambda: config)
    async def resolve_key(_settings, _sessions):
        return "synthetic-key"
    monkeypatch.setattr(routes, "resolve_live_api_key", resolve_key)
    seen = []

    async def extract(_source, pcm, *, max_seconds):
        pcm.write_bytes(b"\0\0" * 1600)
        return 0.1

    async def translate(_pcm, output, *, key, model, on_connected):
        seen.append((key, model))
        on_connected()
        output.write_bytes(_wav(0.1))

    async def mux(source, translated, result):
        assert source.exists() and translated.exists()
        result.write_bytes(b"synthetic-mp4")

    manager = LiveJobManager(tmp_path, extract_video=extract, mux_video=mux, translate=translate)
    app.dependency_overrides[routes.get_live_manager] = lambda: manager
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            started = await client.post("/api/live-audio-translations", files={
                "file": ("input.mp4", b"synthetic-video", "video/mp4")})
            assert started.status_code == 202
            job_id = started.json()["data"]["id"]
            await asyncio.wait_for(manager.jobs[job_id].task, 1)
            status = (await client.get(f"/api/live-audio-translations/{job_id}")).json()["data"]
            assert status["status"] == "completed" and status["video_url"].endswith("/video")
            assert status["audio_url"] is None
            result = await client.get(f"/api/live-audio-translations/{job_id}/video")
            assert result.status_code == 200 and result.content == b"synthetic-mp4"
            assert (await client.get(f"/api/live-audio-translations/{job_id}/audio")).status_code == 409
        assert seen == [("synthetic-key", "synthetic-model")]
        assert not (manager.jobs[job_id].directory / "source.mp4").exists()
        assert not (manager.jobs[job_id].directory / "input.pcm").exists()
        assert not (manager.jobs[job_id].directory / "translated.wav").exists()
    finally:
        await manager.close()
        app.dependency_overrides.pop(routes.get_live_manager, None)


@pytest.mark.asyncio
async def test_live_video_upload_limit_cleans_partial_file(tmp_path, monkeypatch):
    from app.api.routes import live_audio_translation as routes
    from app.services.live_audio_translation.jobs import LiveJobManager

    config = type("Config", (), {"LIVE_AUDIO_TRANSLATION_ENABLED": True,
                                 "GEMINI_LIVE_TRANSLATE_API_KEY": "synthetic-key",
                                 "GEMINI_LIVE_TRANSLATE_MODEL": "synthetic-model",
                                 "STORAGE_ROOT": tmp_path})()
    monkeypatch.setattr(routes, "get_settings", lambda: config)
    monkeypatch.setattr(routes, "MAX_VIDEO_UPLOAD_BYTES", 4)
    manager = LiveJobManager(tmp_path)
    app.dependency_overrides[routes.get_live_manager] = lambda: manager
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/live-audio-translations", files={
                "file": ("input.mp4", b"too-large", "video/mp4")})
        assert response.status_code == 413 and response.json()["detail"] == "video_too_large"
        assert manager.jobs == {} and list(manager.directory.iterdir()) == []
    finally:
        await manager.close()
        app.dependency_overrides.pop(routes.get_live_manager, None)
