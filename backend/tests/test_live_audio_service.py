"""Gemini Live audio boundary tests; no network or real credential."""
import asyncio
import base64
import json
import logging
import os
import shutil
import time
import wave

import pytest


@pytest.mark.asyncio
async def test_convert_wav_to_live_pcm_and_reject_long_or_unsupported(tmp_path):
    from app.services.live_audio_translation.audio import AudioInputError, convert_to_pcm
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required for a real conversion test")

    source = tmp_path / "speech.wav"
    with wave.open(str(source), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\0\0\0\0" * 2400)
    pcm = tmp_path / "input.pcm"
    duration = await convert_to_pcm(source, pcm, max_seconds=5)
    assert 0.09 <= duration <= 0.11
    assert pcm.stat().st_size == 3200
    with pytest.raises(AudioInputError) as error:
        await convert_to_pcm(source, tmp_path / "long.pcm", max_seconds=0.01)
    assert error.value.code == "session_limit"
    unknown = tmp_path / "speech.txt"
    unknown.write_bytes(source.read_bytes())
    with pytest.raises(AudioInputError) as error:
        await convert_to_pcm(unknown, tmp_path / "wrong.pcm", max_seconds=5)
    assert error.value.code == "unsupported_audio_format"


@pytest.mark.asyncio
async def test_conversion_invokes_isolated_16khz_mono_pcm_adapter_without_system_ffmpeg(tmp_path, monkeypatch):
    from app.services.live_audio_translation import audio

    source = tmp_path / "speech.wav"
    source.write_bytes(b"synthetic audio")
    output = tmp_path / "input.pcm"
    calls = []

    async def probe(*args, timeout):
        assert args[0] == "ffprobe" and timeout == 15
        return json.dumps({"streams": [{"codec_type": "audio"}],
                           "format": {"duration": "0.100"}}).encode()

    class Process:
        returncode = 0

        async def wait(self):
            return 0

    async def spawn(*args, **_kwargs):
        calls.append(args)
        output.write_bytes(b"\0\0" * 1600)
        return Process()

    monkeypatch.setattr(audio, "_run", probe)
    monkeypatch.setattr(audio.asyncio, "create_subprocess_exec", spawn)
    duration = await audio.convert_to_pcm(source, output, max_seconds=5)
    assert duration == pytest.approx(0.1)
    assert calls[0][0] == "ffmpeg"
    assert calls[0][calls[0].index("-ac") + 1] == "1"
    assert calls[0][calls[0].index("-ar") + 1] == "16000"
    assert calls[0][calls[0].index("-f") + 1] == "s16le"


@pytest.mark.asyncio
async def test_conversion_rejects_duration_over_session_limit_before_ffmpeg(tmp_path, monkeypatch):
    from app.services.live_audio_translation import audio

    source = tmp_path / "speech.wav"
    source.write_bytes(b"synthetic audio")

    async def probe(*_args, timeout):
        return json.dumps({"streams": [{"codec_type": "audio"}],
                           "format": {"duration": "301"}}).encode()

    async def no_conversion(*_args, **_kwargs):
        pytest.fail("long audio must be rejected before conversion")

    monkeypatch.setattr(audio, "_run", probe)
    monkeypatch.setattr(audio.asyncio, "create_subprocess_exec", no_conversion)
    with pytest.raises(audio.AudioInputError) as error:
        await audio.convert_to_pcm(source, tmp_path / "input.pcm", max_seconds=300)
    assert error.value.code == "session_limit"


@pytest.mark.asyncio
async def test_conversion_rejects_malformed_probe_duration(tmp_path, monkeypatch):
    from app.services.live_audio_translation import audio

    source = tmp_path / "speech.wav"
    source.write_bytes(b"synthetic audio")

    async def probe(*_args, timeout):
        return json.dumps({"streams": [{"codec_type": "audio"}],
                           "format": {"duration": "NaN"}}).encode()

    monkeypatch.setattr(audio, "_run", probe)
    with pytest.raises(audio.AudioInputError) as error:
        await audio.convert_to_pcm(source, tmp_path / "input.pcm", max_seconds=300)
    assert error.value.code == "unsupported_audio_format"


@pytest.mark.asyncio
async def test_live_translate_streams_pcm_and_writes_vietnamese_wav(tmp_path):
    from app.services.live_audio_translation.live_api import translate_pcm

    pcm = tmp_path / "input.pcm"
    pcm.write_bytes(b"\x01\x00" * 1600)
    output = tmp_path / "translated.wav"
    chunk = b"\x02\x00" * 2400
    sent = []
    connection_states = []
    ended = asyncio.Event()
    ready = False

    class Socket:
        async def send(self, message):
            sent.append(json.loads(message))
            if "audioStreamEnd" in sent[-1].get("realtimeInput", {}):
                ended.set()

        async def recv(self):
            nonlocal ready
            if not ready:
                ready = True
                return json.dumps({"setupComplete": {}})
            await ended.wait()
            return json.dumps({"serverContent": {"modelTurn": {"parts": [{"inlineData": {
                "mimeType": "audio/pcm;rate=24000", "data": base64.b64encode(chunk).decode(),
            }}]}, "turnComplete": True}})

    class Connector:
        async def __aenter__(self):
            return Socket()

        async def __aexit__(self, *_):
            return None

    async def no_wait(_):
        return None

    def connect_without_debug_handshake(_uri, **kwargs):
        assert kwargs["logger"].getEffectiveLevel() >= logging.WARNING
        return Connector()

    await translate_pcm(pcm, output, key="synthetic-key", model="gemini-3.5-live-translate-preview",
                        connect=connect_without_debug_handshake, pace=no_wait,
                        on_connected=lambda: connection_states.append("streaming"))
    assert connection_states == ["streaming"]
    assert sent[0]["setup"]["generationConfig"]["translationConfig"]["targetLanguageCode"] == "vi"
    assert sent[0]["setup"]["generationConfig"]["translationConfig"]["echoTargetLanguage"] is True
    assert sent[0]["setup"]["model"] == "models/gemini-3.5-live-translate-preview"
    assert base64.b64decode(sent[1]["realtimeInput"]["audio"]["data"]) == pcm.read_bytes()
    assert sent[-1] == {"realtimeInput": {"audioStreamEnd": True}}
    with wave.open(str(output)) as wav:
        assert wav.getframerate() == 24000 and wav.getnchannels() == 1
        assert wav.readframes(2400) == chunk


@pytest.mark.asyncio
async def test_live_translate_finishes_after_quiet_drain_without_turn_complete(tmp_path):
    from app.services.live_audio_translation.live_api import translate_pcm

    pcm = tmp_path / "input.pcm"
    pcm.write_bytes(b"\0\0" * 1600)
    output = tmp_path / "result.wav"
    end = asyncio.Event()
    received = False

    class Socket:
        async def send(self, value):
            if "audioStreamEnd" in json.loads(value).get("realtimeInput", {}):
                end.set()

        async def recv(self):
            nonlocal received
            if not received:
                received = True
                return json.dumps({"setupComplete": {}})
            await end.wait()
            if not hasattr(self, "audio_sent"):
                self.audio_sent = True
                return json.dumps({"serverContent": {"modelTurn": {"parts": [{"inlineData": {
                    "mimeType": "audio/pcm;rate=24000", "data": base64.b64encode(b"\0\0" * 2400).decode(),
                }}]}}})
            await asyncio.Event().wait()

    class Connector:
        async def __aenter__(self):
            return Socket()

        async def __aexit__(self, *_):
            return None

    async def no_wait(_):
        return None

    await asyncio.wait_for(translate_pcm(pcm, output, key="synthetic-key", model="model",
                                     connect=lambda _uri, **_kwargs: Connector(), pace=no_wait,
                                     drain_seconds=0.01, final_timeout=0.1), 1)
    with wave.open(str(output)) as wav:
        assert wav.getframerate() == 24000
        assert wav.getnframes() == 2400


@pytest.mark.asyncio
async def test_live_translate_reports_sender_failure_without_waiting_for_receiver(tmp_path):
    from app.services.live_audio_translation.live_api import LiveTranslationError, translate_pcm

    pcm = tmp_path / "input.pcm"
    pcm.write_bytes(b"\0\0" * 1600)
    ready = False

    class Socket:
        async def send(self, message):
            if "realtimeInput" in json.loads(message):
                raise OSError("synthetic send failure")

        async def recv(self):
            nonlocal ready
            if not ready:
                ready = True
                return json.dumps({"setupComplete": {}})
            await asyncio.Event().wait()

    class Connector:
        async def __aenter__(self):
            return Socket()

        async def __aexit__(self, *_):
            return None

    with pytest.raises(LiveTranslationError) as error:
        await asyncio.wait_for(translate_pcm(
            pcm, tmp_path / "result.wav", key="synthetic-key", model="model",
            connect=lambda _uri, **_kwargs: Connector(), pace=lambda _: asyncio.sleep(0)), 2)
    assert error.value.code == "connection_failure"


@pytest.mark.asyncio
async def test_cancelling_queued_job_releases_slot_and_removes_upload(tmp_path):
    from app.services.live_audio_translation.jobs import LiveJobManager

    manager = LiveJobManager(tmp_path, max_active=1)
    directory = manager.directory / "first"
    directory.mkdir(parents=True)
    source = directory / "source.wav"
    source.write_bytes(b"synthetic audio")
    manager.start("first", source, directory, key="key", model="model")
    assert await manager.cancel("first") is True
    assert manager.jobs["first"].status == "cancelled"
    assert not source.exists()

    next_directory = manager.directory / "second"
    next_directory.mkdir()
    next_source = next_directory / "source.wav"
    next_source.write_bytes(b"synthetic audio")
    manager.start("second", next_source, next_directory, key="key", model="model")
    await manager.close()


@pytest.mark.asyncio
async def test_live_job_manager_bounds_results_and_removes_stale_crash_files(tmp_path):
    from app.services.live_audio_translation.jobs import LiveJob, LiveJobManager

    stale = tmp_path / "live_audio_translation" / "stale"
    stale.mkdir(parents=True)
    (stale / "translated.wav").write_bytes(b"old")
    old_time = time.time() - 25 * 60 * 60
    os.utime(stale, (old_time, old_time))

    manager = LiveJobManager(tmp_path, max_results=1)
    assert not stale.exists()
    first = manager.directory / "first"
    first.mkdir()
    (first / "translated.wav").write_bytes(b"result")
    manager.jobs["first"] = LiveJob("first", first, first / "source.wav", status="completed")

    second = manager.directory / "second"
    second.mkdir()
    source = second / "source.wav"
    source.write_bytes(b"synthetic audio")
    manager.start("second", source, second, key="key", model="model")
    assert "first" not in manager.jobs and not first.exists()
    await manager.close()
    assert not second.exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("message,code", [
    ({"error": {"code": 429, "message": "secret upstream body"}}, "quota_or_rate_limit"),
    ({"serverContent": {"modelTurn": {"parts": [{"inlineData": {
        "mimeType": "audio/pcm;rate=24000", "data": "bad$base64"}}]}, "turnComplete": True}}, "malformed_response"),
    ({"serverContent": {"turnComplete": True}}, "no_translated_audio"),
])
async def test_live_translate_maps_upstream_errors_without_leaking_message(tmp_path, message, code):
    from app.services.live_audio_translation.live_api import LiveTranslationError, translate_pcm

    pcm = tmp_path / "input.pcm"
    pcm.write_bytes(b"\0\0" * 1600)
    ended = asyncio.Event()
    ready = False

    class Socket:
        async def send(self, value):
            if "audioStreamEnd" in json.loads(value).get("realtimeInput", {}):
                ended.set()

        async def recv(self):
            nonlocal ready
            if not ready:
                ready = True
                return json.dumps({"setupComplete": {}})
            await ended.wait()
            return json.dumps(message)

    class Connector:
        async def __aenter__(self):
            return Socket()

        async def __aexit__(self, *_):
            return None

    async def no_wait(_):
        return None

    with pytest.raises(LiveTranslationError) as error:
        await translate_pcm(pcm, tmp_path / "translated.wav", key="synthetic-key", model="model",
                            connect=lambda _uri, **_kwargs: Connector(), pace=no_wait)
    assert error.value.code == code
    assert "secret upstream body" not in str(error.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure,code", [(TimeoutError(), "timeout"),
                                              (OSError("synthetic secret"), "connection_failure")])
async def test_live_translate_maps_connection_and_timeout(tmp_path, failure, code):
    from app.services.live_audio_translation.live_api import LiveTranslationError, translate_pcm

    pcm = tmp_path / "input.pcm"
    pcm.write_bytes(b"\0\0" * 1600)

    class Connector:
        async def __aenter__(self):
            raise failure

        async def __aexit__(self, *_):
            return None

    with pytest.raises(LiveTranslationError) as error:
        await translate_pcm(pcm, tmp_path / "result.wav", key="synthetic-key", model="model",
                            connect=lambda _uri, **_kwargs: Connector())
    assert error.value.code == code
    assert "synthetic secret" not in str(error.value)
