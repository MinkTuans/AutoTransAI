"""TTS adapters keep catalog identity and credentials local to each call."""
import asyncio
import base64

import httpx
import pytest

from app.providers.audio.elevenlabs_provider import ElevenLabsAudioProvider
from app.providers.audio.google_tts_provider import GoogleCloudTTSProvider
from app.providers.audio.edge_tts_provider import EdgeTTSProvider
from app.services.ai_routing import RouteTarget
from app.services.ai_routing import UnsupportedModalityError, classify_failure


def target(provider, remote, *, capability="TTS", key_id="key-id"):
    return RouteTarget("catalog-id", provider, remote, key_id, capability)


@pytest.mark.asyncio
async def test_elevenlabs_concurrent_calls_keep_exact_model_key_and_voice(monkeypatch, tmp_path):
    calls = []

    async def post(client, url, **kwargs):
        await asyncio.sleep(0)
        calls.append((url, kwargs))
        return httpx.Response(200, content=b"synthetic mp3")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    provider = ElevenLabsAudioProvider()
    results = await asyncio.gather(*(
        provider.generate_audio(f"words-{n}", f"voice-{n}", tmp_path / f"{n}.mp3",
                                route_target=target("elevenlabs", f"model-{n}"), api_key=f"request-key-{n}")
        for n in (1, 2)
    ))
    assert all(result.success for result in results)
    assert len(calls) == 2
    for n in (1, 2):
        url, kwargs = next(call for call in calls if call[1]["json"]["text"] == f"words-{n}")
        assert url == f"https://api.elevenlabs.io/v1/text-to-speech/voice-{n}"
        assert kwargs["json"]["model_id"] == f"model-{n}"
        assert kwargs["headers"]["xi-api-key"] == f"request-key-{n}"
        assert (tmp_path / f"{n}.mp3").read_bytes() == b"synthetic mp3"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,target_value", [
    (ElevenLabsAudioProvider, target("google_cloud_tts", "model")),
    (ElevenLabsAudioProvider, target("elevenlabs", "model", capability="STT")),
    (GoogleCloudTTSProvider, target("elevenlabs", "voice")),
    (GoogleCloudTTSProvider, target("google_cloud_tts", "voice", capability="STT")),
])
async def test_keyed_providers_reject_wrong_route_before_http(monkeypatch, tmp_path, provider, target_value):
    async def no_post(*args, **kwargs):
        pytest.fail("invalid target reached HTTP")

    monkeypatch.setattr(httpx.AsyncClient, "post", no_post)
    with pytest.raises(ValueError):
        await provider().generate_audio("hello", "voice", tmp_path / "bad.wav",
                                        route_target=target_value, api_key="request-key")


@pytest.mark.asyncio
async def test_google_voice_catalog_identity_and_request_key_are_exact(monkeypatch, tmp_path):
    calls = []

    async def post(client, url, **kwargs):
        await asyncio.sleep(0)
        calls.append((url, kwargs))
        return httpx.Response(200, json={"audioContent": base64.b64encode(b"wave").decode()})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    provider = GoogleCloudTTSProvider()
    results = await asyncio.gather(*(
        provider.generate_audio(f"words-{n}", f"vi-VN-Neural2-{n}", tmp_path / f"{n}.wav",
                                route_target=target("google_cloud_tts", f"vi-VN-Neural2-{n}"),
                                api_key=f"request-key-{n}")
        for n in (1, 2)
    ))
    assert all(result.success for result in results)
    for n in (1, 2):
        url, kwargs = next(call for call in calls if call[1]["json"]["input"]["text"] == f"words-{n}")
        assert url == "https://texttospeech.googleapis.com/v1/text:synthesize"
        assert kwargs["headers"]["x-goog-api-key"] == f"request-key-{n}"
        assert kwargs["json"]["voice"] == {"languageCode": "vi-VN", "name": f"vi-VN-Neural2-{n}"}


@pytest.mark.asyncio
async def test_google_rejects_catalog_identity_that_is_not_requested_voice(monkeypatch, tmp_path):
    async def no_post(*args, **kwargs):
        pytest.fail("unsupported catalog identity reached HTTP")

    monkeypatch.setattr(httpx.AsyncClient, "post", no_post)
    with pytest.raises(UnsupportedModalityError, match="voice") as error:
        await GoogleCloudTTSProvider().generate_audio(
            "hello", "vi-VN-Neural2-A", tmp_path / "bad.wav",
            route_target=target("google_cloud_tts", "some-model-name"), api_key="request-key")
    assert classify_failure(error.value) == "capability_mismatch"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,body", [
    (ElevenLabsAudioProvider, b"bad request-key"),
    (GoogleCloudTTSProvider, b'{"error":"bad request-key"}'),
])
async def test_tts_http_failure_keeps_status_and_redacts_provider_body(monkeypatch, tmp_path, caplog, provider, body):
    async def post(client, url, **kwargs):
        return httpx.Response(429, content=body)

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    voice = "vi-VN-Neural2-A" if provider is GoogleCloudTTSProvider else "voice"
    result = await provider().generate_audio("hello", voice, tmp_path / "bad.wav",
                                             route_target=target(provider().provider_id,
                                                                 voice if provider is GoogleCloudTTSProvider else "model"),
                                             api_key="request-key")
    assert not result.success
    assert result.error_code == "HTTP_429"
    assert "request-key" not in str(result)
    assert "request-key" not in caplog.text


@pytest.mark.asyncio
async def test_edge_canonical_target_remains_keyless_and_uses_confirmed_voice(monkeypatch, tmp_path):
    voices = []

    class Communicate:
        def __init__(self, text, voice):
            voices.append((text, voice))

        async def save(self, path):
            from pathlib import Path
            Path(path).write_bytes(b"edge audio")

    monkeypatch.setattr("app.providers.audio.edge_tts_provider.edge_tts.Communicate", Communicate)
    result = await EdgeTTSProvider().generate_audio("hello", "vi-VN-HoaiMyNeural", tmp_path / "edge.wav",
                                                  route_target=target("edge_tts", "edge-tts", key_id=None))
    assert result.success
    assert voices == [("hello", "vi-VN-HoaiMyNeural")]
    with pytest.raises(ValueError):
        await EdgeTTSProvider().generate_audio("hello", "vi-VN-HoaiMyNeural", tmp_path / "bad.wav",
                                               route_target=target("edge_tts", "edge-tts", key_id=None),
                                               api_key="request-key")


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,setting,expected_model", [
    (ElevenLabsAudioProvider, "ELEVENLABS_API_KEY", "eleven_multilingual_v2"),
    (GoogleCloudTTSProvider, "GOOGLE_CLOUD_TTS_API_KEY", None),
])
async def test_legacy_positional_call_uses_configured_key_in_header(monkeypatch, tmp_path, provider, setting, expected_model):
    module = __import__(provider.__module__, fromlist=["settings"])
    monkeypatch.setattr(module.settings, setting, "legacy-key")
    calls = []

    async def post(client, url, **kwargs):
        calls.append((url, kwargs))
        if provider is ElevenLabsAudioProvider:
            return httpx.Response(200, content=b"mp3")
        return httpx.Response(200, json={"audioContent": base64.b64encode(b"wav").decode()})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    voice = "vi-VN-Neural2-A" if provider is GoogleCloudTTSProvider else "voice"
    result = await provider().generate_audio("hello", voice, tmp_path / "legacy.wav")
    assert result.success
    url, kwargs = calls[0]
    assert "legacy-key" not in url
    assert kwargs["headers"]["x-goog-api-key" if provider is GoogleCloudTTSProvider else "xi-api-key"] == "legacy-key"
    if expected_model:
        assert kwargs["json"]["model_id"] == expected_model


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,status,expected", [
    (ElevenLabsAudioProvider, 401, "HTTP_401"),
    (GoogleCloudTTSProvider, 401, "HTTP_401"),
    (ElevenLabsAudioProvider, 429, "HTTP_429"),
    (GoogleCloudTTSProvider, 429, "HTTP_429"),
])
async def test_auth_and_rate_errors_preserve_status_without_secret(monkeypatch, tmp_path, caplog, provider, status, expected):
    async def post(client, url, **kwargs):
        return httpx.Response(status, text="echo request-key")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    voice = "vi-VN-Neural2-A" if provider is GoogleCloudTTSProvider else "voice"
    result = await provider().generate_audio("hello", voice, tmp_path / "error.wav",
                                             route_target=target(provider().provider_id,
                                                                 voice if provider is GoogleCloudTTSProvider else "model"),
                                             api_key="request-key")
    assert result.error_code == expected
    assert "request-key" not in str(result) + caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", [ElevenLabsAudioProvider, GoogleCloudTTSProvider])
async def test_timeout_exception_is_classified_and_redacted(monkeypatch, tmp_path, caplog, provider):
    async def post(client, url, **kwargs):
        raise httpx.ReadTimeout("request-key", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    voice = "vi-VN-Neural2-A" if provider is GoogleCloudTTSProvider else "voice"
    result = await provider().generate_audio("hello", voice, tmp_path / "timeout.wav",
                                             route_target=target(provider().provider_id,
                                                                 voice if provider is GoogleCloudTTSProvider else "model"),
                                             api_key="request-key")
    assert result.error_code == "TTS_TIMEOUT"
    assert "request-key" not in str(result) + caplog.text


@pytest.mark.asyncio
async def test_google_voice_listing_and_validation_never_put_key_in_url(monkeypatch):
    from app.providers.audio import google_tts_provider as module

    monkeypatch.setattr(module.settings, "GOOGLE_CLOUD_TTS_API_KEY", "legacy-key")
    calls = []

    async def get(client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, json={"voices": [{
            "name": "vi-VN-Neural2-A", "languageCodes": ["vi-VN"], "ssmlGender": "FEMALE",
        }]})

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    provider = GoogleCloudTTSProvider()
    assert await provider.validate_configuration()
    assert (await provider.get_voices("vi"))[0].id == "vi-VN-Neural2-A"
    assert len(calls) == 2
    assert all(url == "https://texttospeech.googleapis.com/v1/voices" for url, _ in calls)
    assert all(kwargs["headers"]["x-goog-api-key"] == "legacy-key" for _, kwargs in calls)


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", [ElevenLabsAudioProvider, GoogleCloudTTSProvider])
async def test_request_credential_without_route_is_rejected(monkeypatch, tmp_path, provider):
    async def no_post(*args, **kwargs):
        pytest.fail("unscoped request key reached HTTP")

    monkeypatch.setattr(httpx.AsyncClient, "post", no_post)
    with pytest.raises(ValueError):
        await provider().generate_audio("hello", "voice", tmp_path / "bad.wav", api_key="request-key")
