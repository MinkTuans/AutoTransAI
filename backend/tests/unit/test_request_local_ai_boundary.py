"""The catalog target and decrypted key reach the actual HTTP boundary."""
import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from app.providers.llm.gemini_provider import GeminiLLMProvider
from app.providers.llm.openai_provider import OpenAILLMProvider
from app.services.ai_routing import RouteTarget
from app.services.ai_routing import classify_failure
from app.core.pipeline_errors import PipelineError
from app.services.video_translator import translator_service as service


def target(provider, model, capability):
    return RouteTarget("catalog-id", provider, model, "key-id", capability)


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_cls,provider_id,response", [
    (GeminiLLMProvider, "gemini", {"candidates": [{"content": {"parts": [{"text": "done"}]}}]}),
    (OpenAILLMProvider, "openai", {"choices": [{"message": {"content": "done"}}]}),
])
async def test_concurrent_llm_requests_keep_model_and_key_local(monkeypatch, provider_cls, provider_id, response):
    calls = []

    async def post(client, url, **kwargs):
        await asyncio.sleep(0)
        calls.append((url, kwargs))
        return httpx.Response(200, json=response)

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    provider = provider_cls()
    await asyncio.gather(*(
        provider.generate_text(f"prompt-{n}", route_target=target(provider_id, f"remote-{n}", "LLM"), api_key=f"request-key-{n}")
        for n in (1, 2)
    ))
    assert len(calls) == 2
    for n in (1, 2):
        call = next(kwargs for url, kwargs in calls if f"prompt-{n}" in str(kwargs.get("json")))
        url = next(url for url, kwargs in calls if kwargs is call)
        assert "request-key-" not in url
        if provider_id == "gemini":
            assert f"/models/remote-{n}:generateContent" in url
            assert call["headers"]["x-goog-api-key"] == f"request-key-{n}"
        else:
            assert call["json"]["model"] == f"remote-{n}"
            assert call["headers"]["Authorization"] == f"Bearer request-key-{n}"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_id,response", [
    ("gemini", {"candidates": [{"content": {"parts": [{"text": '{"language":"English","segments":[{"start_time":0,"end_time":2,"text":"Hi"}]}' }]}}]}),
    ("openai", {"language": "English", "segments": [{"start": 0, "end": 2, "text": "Hi"}]}),
])
async def test_concurrent_stt_requests_keep_model_and_key_local(monkeypatch, tmp_path, provider_id, response):
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFF some synthetic audio")
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=2.0))
    calls = []

    async def post(client, url, **kwargs):
        await asyncio.sleep(0)
        calls.append((url, kwargs))
        return httpx.Response(200, json=response)

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    func = service.transcribe_audio_with_gemini if provider_id == "gemini" else service.transcribe_audio_with_whisper
    results = await asyncio.gather(*(
        func(audio, job_id=f"job-{n}", route_target=target(provider_id, f"remote-{n}", "STT"), api_key=f"request-key-{n}")
        for n in (1, 2)
    ))
    assert all(segments[0]["text"] == "Hi" for segments, _ in results)
    assert len(calls) == 2
    for n in (1, 2):
        if provider_id == "gemini":
            url, kwargs = next((url, kwargs) for url, kwargs in calls if f"/models/remote-{n}:" in url)
        else:
            url, kwargs = next((url, kwargs) for url, kwargs in calls if kwargs["data"]["model"] == f"remote-{n}")
        assert "request-key-" not in url
        if provider_id == "gemini":
            assert f"/models/remote-{n}:generateContent" in url
            assert kwargs["headers"]["x-goog-api-key"] == f"request-key-{n}"
        else:
            assert kwargs["data"]["model"] == f"remote-{n}"
            assert kwargs["headers"]["Authorization"] == f"Bearer request-key-{n}"


@pytest.mark.asyncio
async def test_mismatched_provider_target_never_reaches_http(monkeypatch):
    calls = AsyncMock()
    monkeypatch.setattr(httpx.AsyncClient, "post", calls)
    with pytest.raises(ValueError, match="does not match"):
        await OpenAILLMProvider().generate_text(
            "hello", route_target=target("gemini", "remote-one", "LLM"), api_key="request-key"
        )
    calls.assert_not_awaited()


@pytest.mark.asyncio
async def test_request_key_overrides_global_only_for_its_call(monkeypatch):
    from app.providers.llm import gemini_provider

    monkeypatch.setattr(gemini_provider.settings, "GEMINI_API_KEY", "global-key")
    calls = []

    async def post(client, url, **kwargs):
        calls.append((url, kwargs["headers"]["x-goog-api-key"]))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    provider = GeminiLLMProvider()
    await provider.generate_text("one", route_target=target("gemini", "remote-one", "LLM"), api_key="request-key")
    await provider.generate_text("two", model="legacy-model")
    assert calls == [
        ("https://generativelanguage.googleapis.com/v1beta/models/remote-one:generateContent", "request-key"),
        ("https://generativelanguage.googleapis.com/v1beta/models/legacy-model:generateContent", "global-key"),
    ]


@pytest.mark.asyncio
async def test_provider_error_does_not_echo_request_secret(monkeypatch):
    async def post(client, url, **kwargs):
        return httpx.Response(401, text="bad key request-key")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(Exception) as error:
        await GeminiLLMProvider().generate_text("hello", route_target=target("gemini", "remote-one", "LLM"), api_key="request-key")
    assert "request-key" not in str(error.value)
    assert "request-key" not in str(error.value.to_dict())


@pytest.mark.parametrize("status,code", [(401, "auth"), (404, "model_unavailable"), (429, "rate_limit"), (503, "provider_unavailable")])
def test_routing_classifies_provider_pipeline_http_status(status, code):
    assert classify_failure(PipelineError(http_status=status)) == code


@pytest.mark.asyncio
async def test_gemini_stt_parse_failure_does_not_echo_provider_body_or_key(monkeypatch, tmp_path, caplog, capsys):
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFF synthetic audio")
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=2.0))

    async def post(client, url, **kwargs):
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "{request-key"}]}}]})

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(PipelineError) as error:
        await service.transcribe_audio_with_gemini(
            audio, route_target=target("gemini", "remote-model", "STT"), api_key="request-key"
        )
    assert "request-key" not in str(error.value.to_dict())
    assert "request-key" not in caplog.text
    assert "request-key" not in capsys.readouterr().out


@pytest.mark.asyncio
async def test_gemini_validation_url_has_no_key(monkeypatch):
    from app.providers.llm import gemini_provider

    monkeypatch.setattr(gemini_provider.settings, "GEMINI_API_KEY", "global-key")
    calls = []

    async def get(client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "get", get)
    assert await GeminiLLMProvider().validate_configuration()
    assert calls == [("https://generativelanguage.googleapis.com/v1beta/models", {"headers": {"x-goog-api-key": "global-key"}})]


@pytest.mark.asyncio
@pytest.mark.parametrize("status,classification", [
    (401, "auth"),
    (404, "model_unavailable"),
    (400, "capability_mismatch"),
    (429, "rate_limit"),
])
async def test_openai_stt_http_error_preserves_status_without_echoing_secret(
    monkeypatch, tmp_path, status, classification, capsys
):
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFF synthetic audio")
    monkeypatch.setattr(service, "probe_duration_async", AsyncMock(return_value=2.0))

    async def post(client, url, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer request-key"
        assert kwargs["data"]["model"] == "remote-model"
        return httpx.Response(status, text="provider response echoes request-key")

    monkeypatch.setattr(httpx.AsyncClient, "post", post)
    with pytest.raises(PipelineError) as error:
        await service.transcribe_audio_with_whisper(
            audio, route_target=target("openai", "remote-model", "STT"), api_key="request-key"
        )
    assert error.value.http_status == status
    assert classify_failure(error.value) == classification
    assert "request-key" not in str(error.value.to_dict())
    assert "request-key" not in capsys.readouterr().out
