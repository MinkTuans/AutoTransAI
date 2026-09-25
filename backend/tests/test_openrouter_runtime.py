"""OpenRouter runtime requests use only canonical request-local credentials."""

import pytest

from app.services.ai_routing import RouteTarget


def target(capability="TRANSLATION", model="vendor/model"):
    return RouteTarget("catalog-id", "openrouter", model, "key-id", capability)


@pytest.mark.asyncio
async def test_openrouter_llm_uses_exact_route_model_and_key(monkeypatch):
    from app.providers.openrouter_provider import OpenRouterLLMProvider

    seen = {}

    class Response:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": " translated "}}]}

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, *, headers, json):
            seen.update(url=url, headers=headers, payload=json)
            return Response()

    monkeypatch.setattr("httpx.AsyncClient", Client)
    result = await OpenRouterLLMProvider().generate_text(
        "hello", route_target=target(), api_key="synthetic-secret")
    assert result == "translated"
    assert seen["payload"]["model"] == "vendor/model"
    assert seen["headers"]["Authorization"] == "Bearer synthetic-secret"


@pytest.mark.asyncio
async def test_openrouter_rejects_unrouted_credentials():
    from app.providers.openrouter_provider import OpenRouterLLMProvider

    with pytest.raises(ValueError, match="route target"):
        await OpenRouterLLMProvider().generate_text("hello", api_key="synthetic-secret")


@pytest.mark.asyncio
async def test_openrouter_stt_uses_transcription_endpoint_and_exact_route(tmp_path, monkeypatch):
    from app.providers.openrouter_provider import transcribe_audio

    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFFsynthetic")
    seen = {}

    class Response:
        status_code = 200

        def json(self):
            return {"text": "hello", "language": "en"}

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, *, headers, json):
            seen.update(url=url, headers=headers, payload=json)
            return Response()

    monkeypatch.setattr("httpx.AsyncClient", Client)
    segments, language = await transcribe_audio(audio, 4.0, route_target=target("STT"), api_key="synthetic-secret")
    assert seen["url"].endswith("/audio/transcriptions")
    assert seen["payload"]["model"] == "vendor/model"
    assert "response_format" not in seen["payload"]
    assert seen["headers"]["Authorization"] == "Bearer synthetic-secret"
    assert segments == [{"number": 1, "start_time": 0.0, "end_time": 4.0,
                         "text": "hello", "speaker_id": "UNRESOLVED_0001"}]
    assert language == "en"


@pytest.mark.asyncio
async def test_openrouter_whisper_requests_verbose_segments(tmp_path, monkeypatch):
    from app.providers.openrouter_provider import transcribe_audio

    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFFsynthetic")
    payloads = []

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, *, headers, json):
            payloads.append(json)
            return type("Response", (), {
                "status_code": 200,
                "json": lambda self: {"language": "en", "segments": [
                    {"start": 0.4, "end": 1.2, "text": "first"},
                    {"start": 1.8, "end": 2.5, "text": "second"},
                ]},
            })()

    monkeypatch.setattr("httpx.AsyncClient", Client)
    segments, _ = await transcribe_audio(
        audio, 4.0, route_target=target("STT", "openai/whisper-1"), api_key="synthetic-secret")
    assert payloads[0]["response_format"] == "verbose_json"
    assert [(s["start_time"], s["end_time"]) for s in segments] == [(0.4, 1.2), (1.8, 2.5)]


@pytest.mark.asyncio
async def test_openrouter_chunk_offsets_preserve_segment_timestamps(tmp_path, monkeypatch):
    from app.services.video_translator import translator_service as service

    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"RIFFsynthetic")

    async def probe(path):
        if path == audio:
            return 65.0
        return 55.0 if path.name == "chunk_0000.wav" else 10.0

    async def ffmpeg(command, **kwargs):
        from pathlib import Path
        Path(command[-1]).write_bytes(b"RIFFchunk")

    async def transcribe(path, duration, **kwargs):
        return ([{"number": 1, "start_time": 1.0, "end_time": 2.0,
                  "text": path.stem, "speaker_id": "UNRESOLVED_0001"}], "en")

    monkeypatch.setattr(service, "probe_duration_async", probe)
    monkeypatch.setattr(service, "run_ffmpeg_with_progress_async", ffmpeg)
    monkeypatch.setattr(service, "transcribe_openrouter_chunk", transcribe)
    segments, language = await service.transcribe_audio_with_openrouter(
        audio, route_target=target("STT", "openai/whisper-1"), api_key="synthetic-secret")
    assert language == "en"
    assert [(s["start_time"], s["end_time"]) for s in segments] == [(1.0, 2.0), (56.0, 57.0)]


@pytest.mark.asyncio
async def test_openrouter_image_posts_to_documented_endpoint(tmp_path, monkeypatch):
    import base64
    from io import BytesIO
    from PIL import Image
    from app.providers import openrouter_provider as module

    image = BytesIO()
    Image.new("RGB", (2, 2), "red").save(image, format="PNG")
    seen = {}

    async def request(client, method, url, *, headers, payload):
        seen.update(method=method, url=url, headers=headers, payload=payload)
        return {"data": [{"b64_json": base64.b64encode(image.getvalue()).decode()}]}

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(module, "image_request_json", request)
    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    result = await module.OpenRouterImageProvider().generate_image(
        "cat", route_target=target("IMAGE_GENERATION"), api_key="synthetic-secret")
    assert result.success and result.metadata["image_bytes"] == image.getvalue()
    assert seen["url"] == "https://openrouter.ai/api/v1/images"
    assert seen["payload"]["model"] == "vendor/model"


@pytest.mark.asyncio
async def test_openrouter_video_polls_and_downloads_authenticated_content(tmp_path, monkeypatch):
    from app.providers import openrouter_provider as module

    seen = []

    async def request(client, method, url, *, headers, payload=None, accepted=(200,)):
        seen.append((method, url, payload, headers))
        if url.endswith("/videos/models"):
            return {"data": [{"id": "vendor/model", "supported_durations": [5, 8]}]}
        return {"id": "job-123"} if method == "POST" else {"status": "completed"}

    async def download(client, job_id, headers, output):
        seen.append(("CONTENT", job_id, None, headers))
        output.write_bytes(b"validated mp4")
        return 13

    async def no_sleep(_):
        pass

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(module, "video_request_json", request)
    monkeypatch.setattr(module, "_download_video_content", download)
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    monkeypatch.setattr(module, "get_settings", lambda: type("Settings", (), {"DATA_DIR": tmp_path})())
    result = await module.OpenRouterVideoProvider().generate_video(
        "cat", 8, tmp_path / "video.mp4", route_target=target("VIDEO_GENERATION"),
        api_key="synthetic-secret")
    assert result.success
    assert seen[0][1] == "https://openrouter.ai/api/v1/videos/models"
    assert seen[1][1] == "https://openrouter.ai/api/v1/videos"
    assert seen[1][2]["model"] == "vendor/model"
    assert seen[2][1] == "https://openrouter.ai/api/v1/videos/job-123"
    assert seen[3] == ("CONTENT", "job-123", None, {"Authorization": "Bearer synthetic-secret"})


@pytest.mark.asyncio
async def test_openrouter_video_rejects_unsupported_duration_before_submit(tmp_path, monkeypatch):
    from app.providers import openrouter_provider as module
    from app.services.ai_routing import UnsupportedModalityError

    calls = []

    async def request(client, method, url, *, headers, payload=None, accepted=(200,)):
        calls.append((method, url))
        return {"data": [{"id": "vendor/model", "supported_durations": [5, 10]}]}

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(module, "video_request_json", request)
    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    monkeypatch.setattr(module, "get_settings", lambda: type("Settings", (), {"DATA_DIR": tmp_path})())
    with pytest.raises(UnsupportedModalityError):
        await module.OpenRouterVideoProvider().generate_video(
            "cat", 8, tmp_path / "video.mp4", route_target=target("VIDEO_GENERATION"),
            api_key="synthetic-secret")
    assert calls == [("GET", "https://openrouter.ai/api/v1/videos/models")]


@pytest.mark.asyncio
async def test_openrouter_video_definite_submit_rejection_can_fail_over(tmp_path, monkeypatch):
    from app.providers import openrouter_provider as module

    async def reject(*args, **kwargs):
        raise module.VideoBoundaryError("provider_unavailable", 401)

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(module, "video_request_json", reject)
    monkeypatch.setattr(module.httpx, "AsyncClient", Client)
    monkeypatch.setattr(module, "get_settings", lambda: type("Settings", (), {"DATA_DIR": tmp_path})())
    with pytest.raises(module.VideoBoundaryError) as error:
        await module.OpenRouterVideoProvider().generate_video(
            "cat", 8, tmp_path / "video.mp4", route_target=target("VIDEO_GENERATION"),
            api_key="synthetic-secret")
    assert error.value.definitive and error.value.status_code == 401


def test_openrouter_registry_exposes_all_runtime_adapters():
    from app.providers.registry import ProviderRegistry, _register_defaults

    registry = ProviderRegistry()
    _register_defaults(registry)
    assert registry.get_llm("openrouter") is not None
    assert registry.get_vision("openrouter") is not None
    assert registry.get_audio("openrouter") is not None
    assert registry.get_image("openrouter") is not None
    assert registry.get_video("openrouter") is not None


def test_openrouter_video_catalog_target_is_supported():
    from app.services.video_catalog_selection import supported_video_target

    metadata = {"architecture": {"input_modalities": ["text"], "output_modalities": ["video"]},
                "video": {"supported_durations": [5, 8]}}
    assert supported_video_target("openrouter", "vendor/video", metadata=metadata, duration=8)
    assert not supported_video_target("openrouter", "vendor/video", metadata=metadata, duration=10)
    assert not supported_video_target("openrouter", "vendor/video", metadata={"architecture": {
        "input_modalities": ["video"], "output_modalities": ["video"]},
        "video": {"supported_durations": [8]}}, duration=8)
    assert not supported_video_target("openrouter", "vendor/video")


def test_openrouter_explicit_voice_can_be_selected_for_studio():
    from app.services.ai_routing import RoutePlan
    from app.services.video_translator.studio_tts_routing import select_segment_route

    choice = target("TTS", "vendor/speech")
    route = RoutePlan("TTS", (choice,), choice.model_id)
    selected, voices = select_segment_route(
        route, {"voice_provider": "openrouter", "voice_id": "alloy"},
        [{"provider": "openrouter", "voice_id": "alloy", "language": "und",
          "catalog_model_id": "catalog-id"}], "en-US")
    assert selected.targets == (choice,)
    assert voices[choice] == "alloy"


def test_openrouter_voice_cannot_cross_catalog_models():
    from app.services.ai_routing import RouteConfigurationError, RoutePlan
    from app.services.video_translator.studio_tts_routing import select_segment_route

    choice = target("TTS", "vendor/speech")
    route = RoutePlan("TTS", (choice,), choice.model_id)
    with pytest.raises(RouteConfigurationError):
        select_segment_route(route, {"voice_provider": "openrouter", "voice_id": "alloy"},
                             [{"provider": "openrouter", "voice_id": "alloy", "language": "und",
                               "catalog_model_id": "different"}], "en-US")


def test_rebinding_shared_voice_to_new_model_blocks_prior_model():
    from app.services.ai_routing import RouteConfigurationError, RoutePlan, RouteTarget
    from app.services.video_translator.studio_tts_routing import select_segment_route

    old = target("TTS", "vendor/old")
    new = RouteTarget("new-catalog-id", "openrouter", "vendor/new", "key-id", "TTS")
    voice = {"provider": "openrouter", "voice_id": "alloy", "language": "und",
             "catalog_model_id": new.model_id}
    segment = {"voice_provider": "openrouter", "voice_id": "alloy", "confirmed_by_user": True}
    selected, _ = select_segment_route(RoutePlan("TTS", (new,), new.model_id), segment, [voice], "en-US")
    assert selected.targets == (new,)
    with pytest.raises(RouteConfigurationError):
        select_segment_route(RoutePlan("TTS", (old,), old.model_id), segment, [voice], "en-US")


@pytest.mark.asyncio
@pytest.mark.parametrize("voices,requested,source,output,valid", [
    (["alloy", "nova"], "alloy", "discovered", "speech", True),
    (["nova"], "alloy", "discovered", "speech", False),
    (None, "alloy", "discovered", "speech", False),
    (["alloy"], "alloy", "manual", "speech", False),
    (["alloy"], "alloy", "discovered", "text", False),
    (["a" * 101], "a" * 101, "discovered", "speech", False),
])
async def test_studio_openrouter_voice_requires_selected_models_list(voices, requested, source, output, valid):
    from app.api.routes.video_translator import validate_voice_assignment
    from app.models import CatalogModel
    from app.models.settings import AIFunctionConfig

    class Session:
        async def get(self, cls, key):
            if cls is AIFunctionConfig:
                return AIFunctionConfig(function_id="tts", primary_provider_id="openrouter",
                                        model_id="catalog-id")
            if cls is CatalogModel:
                return CatalogModel(id="catalog-id", provider_id="openrouter", source=source, enabled=True,
                                        remote_model_id="vendor/speech",
                                        discovery_metadata={"supported_voices": voices,
                                                            "architecture": {"input_modalities": ["text"],
                                                                             "output_modalities": [output]}})

    found = []
    error = await validate_voice_assignment("openrouter", requested, target_language="en-US",
                                            character_gender="female", validated_voice=found,
                                            session=Session())
    assert (error is None) is valid
    assert bool(found) is valid
