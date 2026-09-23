"""Canonical keyed image adapters use exact targets without outbound traffic."""

import base64
import asyncio
import json
import socket
from types import SimpleNamespace

import httpx
import pytest

from app.providers.image import openai_image_provider, fal_image_provider, catalog_media
from app.services.ai_routing import RouteTarget


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/+QAAAABJRU5ErkJggg=="
)


@pytest.fixture(autouse=True)
def no_outbound_network(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("image adapter test attempted outbound network")))
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443)),
    ])


def mock_client(monkeypatch, provider_module, handler):
    client_type = httpx.AsyncClient
    monkeypatch.setattr(provider_module.httpx, "AsyncClient", lambda **kwargs: client_type(
        transport=httpx.MockTransport(handler), **kwargs,
    ))


def legacy_key(monkeypatch, provider_module, secret="synthetic-legacy"):
    class KeyManager:
        async def get_active_key(self, provider):
            return SimpleNamespace(api_key=secret, key_id="legacy-key")

        async def report_result(self, *args, **kwargs):
            return None

    monkeypatch.setattr(provider_module, "get_key_manager", lambda: KeyManager())


@pytest.mark.asyncio
async def test_openai_uses_exact_model_key_and_download_omits_authorization(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        if request.url.host == "api.openai.com":
            assert request.headers["authorization"] == "Bearer synthetic-openai"
            payload = json.loads(request.read())
            assert payload["model"] == "gpt-image-synthetic"
            assert "size" not in payload  # dimensions are model-specific; discovery has no size evidence
            return httpx.Response(200, json={"data": [{"url": "https://cdn.example.test/image.png"}]})
        assert request.url.host == "cdn.example.test"
        assert "authorization" not in request.headers
        return httpx.Response(200, content=PNG, headers={"content-type": "image/png"})

    mock_client(monkeypatch, openai_image_provider, respond)
    monkeypatch.setattr(openai_image_provider, "get_key_manager", lambda: (_ for _ in ()).throw(
        AssertionError("legacy KeyManager must not run")))
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-openai",
    )
    assert result.success
    assert result.metadata["image_bytes"] == PNG
    assert result.metadata["model"] == "gpt-image-synthetic"
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_fal_uses_exact_safe_endpoint_and_key(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            assert str(request.url) == "https://queue.fal.run/fal-ai/flux/synthetic"
            assert request.headers["authorization"] == "Key synthetic-fal"
            return httpx.Response(200, json={"images": [{"url": "https://cdn.example.test/image.png"}]})
        assert request.url.host == "cdn.example.test"
        assert "authorization" not in request.headers
        return httpx.Response(200, content=PNG, headers={"content-type": "image/png"})

    mock_client(monkeypatch, fal_image_provider, respond)
    monkeypatch.setattr(fal_image_provider, "get_key_manager", lambda: (_ for _ in ()).throw(
        AssertionError("legacy KeyManager must not run")))
    target = RouteTarget("catalog", "fal", "fal-ai/flux/synthetic", "key-id", "IMAGE_GENERATION")
    result = await fal_image_provider.FalImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-fal",
    )
    assert result.success
    assert result.metadata["image_bytes"] == PNG
    assert result.metadata["model"] == "fal-ai/flux/synthetic"
    assert len(requests) == 2


@pytest.mark.asyncio
async def test_canonical_image_rejects_private_download_and_raw_body(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"data": [{"url": "https://127.0.0.1/private"}]})
        raise AssertionError("private download must not execute")

    mock_client(monkeypatch, openai_image_provider, respond)
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-openai",
    )
    assert not result.success
    assert "127.0.0.1" not in (result.error_message or "")
    assert requests and len(requests) == 1


@pytest.mark.asyncio
async def test_fal_malformed_model_path_never_calls_api(monkeypatch):
    monkeypatch.setattr(fal_image_provider.httpx, "AsyncClient", lambda **kwargs: (_ for _ in ()).throw(
        AssertionError("malformed model path must not reach API")))
    target = RouteTarget("catalog", "fal", "fal-ai/../admin", "key-id", "IMAGE_GENERATION")
    result = await fal_image_provider.FalImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-fal",
    )
    assert not result.success
    assert "admin" not in (result.error_message or "")


@pytest.mark.asyncio
@pytest.mark.parametrize("download_response", [
    httpx.Response(302, headers={"location": "https://127.0.0.1/private"}),
    httpx.Response(200, content=PNG, headers={"content-type": "text/html"}),
    httpx.Response(200, content=b"x" * (10 * 1024 * 1024 + 1), headers={"content-type": "image/png"}),
])
async def test_openai_rejects_redirect_wrong_mime_and_oversized_image(monkeypatch, download_response):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"data": [{"url": "https://cdn.example.test/image.png"}]})
        return download_response

    mock_client(monkeypatch, openai_image_provider, respond)
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-openai",
    )
    assert not result.success
    assert len(requests) == 2
    assert "127.0.0.1" not in (result.error_message or "")


@pytest.mark.asyncio
async def test_openai_accepts_bounded_base64_and_never_writes_arbitrary_output_path(monkeypatch, tmp_path):
    def respond(request):
        return httpx.Response(200, json={"data": [{"b64_json": base64.b64encode(PNG).decode()}]})

    mock_client(monkeypatch, openai_image_provider, respond)
    monkeypatch.setattr(openai_image_provider, "get_key_manager", lambda: (_ for _ in ()).throw(
        AssertionError("legacy KeyManager must not run")))
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    arbitrary_path = tmp_path / "should-not-write.png"
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", options={"output_path": arbitrary_path},
        route_target=target, api_key="synthetic-openai",
    )
    assert result.success
    assert result.metadata["image_bytes"] == PNG
    assert not arbitrary_path.exists()


@pytest.mark.asyncio
async def test_openai_upstream_error_body_is_not_returned(monkeypatch):
    def respond(request):
        return httpx.Response(401, text="synthetic-openai synthetic prompt secret upstream body")

    mock_client(monkeypatch, openai_image_provider, respond)
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-openai",
    )
    assert not result.success
    assert result.error_code == "HTTP_401"
    assert "synthetic-openai" not in (result.error_message or "")
    assert "synthetic prompt" not in (result.error_message or "")


@pytest.mark.asyncio
async def test_fal_rejects_untrusted_poll_url_before_forwarding_auth(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(202, json={
            "status_url": "https://cdn.example.test/request/status",
            "response_url": "https://queue.fal.run/request/response",
        })

    mock_client(monkeypatch, fal_image_provider, respond)
    target = RouteTarget("catalog", "fal", "fal-ai/flux/synthetic", "key-id", "IMAGE_GENERATION")
    result = await fal_image_provider.FalImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-fal",
    )
    assert not result.success
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_fal_queue_poll_is_bounded_to_queue_host_and_download_is_unauthenticated(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(202, json={
                "status_url": "https://queue.fal.run/fal-ai/flux/synthetic/requests/one/status",
                "response_url": "https://queue.fal.run/fal-ai/flux/synthetic/requests/one",
            })
        if request.url.path.endswith("/status"):
            assert request.headers["authorization"] == "Key synthetic-fal"
            return httpx.Response(200, json={"status": "COMPLETED"})
        if request.url.host == "queue.fal.run":
            assert request.headers["authorization"] == "Key synthetic-fal"
            return httpx.Response(200, json={"images": [{"url": "https://cdn.example.test/image.png"}]})
        assert request.url.host == "cdn.example.test"
        assert "authorization" not in request.headers
        return httpx.Response(200, content=PNG, headers={"content-type": "image/png"})

    mock_client(monkeypatch, fal_image_provider, respond)
    target = RouteTarget("catalog", "fal", "fal-ai/flux/synthetic", "key-id", "IMAGE_GENERATION")
    result = await fal_image_provider.FalImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-fal",
    )
    assert result.success
    assert [request.method for request in requests] == ["POST", "GET", "GET", "GET"]


@pytest.mark.asyncio
async def test_openai_stops_reading_oversized_json_response(monkeypatch):
    emitted = []

    class OversizedStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            for index in range(3):
                emitted.append(index)
                yield b"x" * (8 * 1024 * 1024)

    def respond(request):
        return httpx.Response(200, headers={"content-type": "application/json"}, stream=OversizedStream())

    mock_client(monkeypatch, openai_image_provider, respond)
    target = RouteTarget("catalog", "openai", "gpt-image-synthetic", "key-id", "IMAGE_GENERATION")
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", route_target=target, api_key="synthetic-openai",
    )
    assert not result.success
    assert emitted == [0, 1]


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_module,provider_class", [
    (openai_image_provider, openai_image_provider.OpenAIImageProvider),
    (fal_image_provider, fal_image_provider.FalImageProvider),
])
async def test_legacy_http_error_does_not_expose_response_or_secret(monkeypatch, provider_module, provider_class):
    mock_client(monkeypatch, provider_module, lambda request: httpx.Response(
        401, text="synthetic-legacy secret upstream prompt body"))
    legacy_key(monkeypatch, provider_module)
    result = await provider_class().generate_image("synthetic prompt")
    assert not result.success
    assert "synthetic-legacy" not in (result.error_message or "")
    assert "upstream prompt body" not in (result.error_message or "")


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_module,provider_class,response_json", [
    (openai_image_provider, openai_image_provider.OpenAIImageProvider,
     {"data": [{"url": "https://127.0.0.1/private"}]}),
    (fal_image_provider, fal_image_provider.FalImageProvider,
     {"images": [{"url": "https://127.0.0.1/private"}]}),
])
async def test_legacy_private_image_url_is_rejected_before_download(
    monkeypatch, provider_module, provider_class, response_json,
):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json=response_json)
        raise AssertionError("private download must not execute")

    mock_client(monkeypatch, provider_module, respond)
    legacy_key(monkeypatch, provider_module)
    result = await provider_class().generate_image("synthetic prompt")
    assert not result.success
    assert len(requests) == 1
    assert "127.0.0.1" not in (result.error_message or "")


@pytest.mark.asyncio
async def test_legacy_openai_rejects_output_path_outside_data_root(monkeypatch, tmp_path):
    def respond(request):
        if request.method == "POST":
            return httpx.Response(200, json={"data": [{"url": "https://cdn.example.test/image.png"}]})
        return httpx.Response(200, content=PNG + b"x" * 1200, headers={"content-type": "image/png"})

    mock_client(monkeypatch, openai_image_provider, respond)
    legacy_key(monkeypatch, openai_image_provider)
    monkeypatch.setattr(openai_image_provider.settings, "DATA_DIR", tmp_path / "data")
    unsafe = tmp_path / "outside.png"
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", options={"output_path": unsafe},
    )
    assert not result.success
    assert not unsafe.exists()


@pytest.mark.asyncio
async def test_legacy_fal_untrusted_poll_url_never_gets_authorization(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(202, json={
                "status_url": "https://cdn.example.test/status",
                "response_url": "https://queue.fal.run/response",
            })
        raise AssertionError("untrusted poll URL must not execute")

    mock_client(monkeypatch, fal_image_provider, respond)
    legacy_key(monkeypatch, fal_image_provider)
    result = await fal_image_provider.FalImageProvider().generate_image("synthetic prompt")
    assert not result.success
    assert len(requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_module,provider_class,response_json", [
    (openai_image_provider, openai_image_provider.OpenAIImageProvider,
     {"data": [{"url": "https://cdn.example.test/image.png"}]}),
    (fal_image_provider, fal_image_provider.FalImageProvider,
     {"images": [{"url": "https://cdn.example.test/image.png"}]}),
])
async def test_legacy_valid_image_still_succeeds(
    monkeypatch, provider_module, provider_class, response_json,
):
    def respond(request):
        if request.method == "POST":
            return httpx.Response(200, json=response_json)
        assert "authorization" not in request.headers
        return httpx.Response(200, content=PNG, headers={"content-type": "image/png"})

    mock_client(monkeypatch, provider_module, respond)
    legacy_key(monkeypatch, provider_module)
    result = await provider_class().generate_image("synthetic prompt")
    assert result.success
    assert result.metadata["image_bytes"] == PNG


@pytest.mark.asyncio
async def test_legacy_openai_allows_output_path_within_data_root(monkeypatch, tmp_path):
    def respond(request):
        if request.method == "POST":
            return httpx.Response(200, json={"data": [{"url": "https://cdn.example.test/image.png"}]})
        return httpx.Response(200, content=PNG, headers={"content-type": "image/png"})

    mock_client(monkeypatch, openai_image_provider, respond)
    legacy_key(monkeypatch, openai_image_provider)
    monkeypatch.setattr(openai_image_provider.settings, "DATA_DIR", tmp_path / "data")
    safe = tmp_path / "data" / "thumb.png"
    result = await openai_image_provider.OpenAIImageProvider().generate_image(
        "synthetic prompt", options={"output_path": safe},
    )
    assert result.success
    assert safe.read_bytes() == PNG


@pytest.mark.asyncio
async def test_image_download_dns_timeout_is_classified(monkeypatch):
    async def timed_out(*args, **kwargs):
        raise asyncio.TimeoutError()

    monkeypatch.setattr(catalog_media.asyncio, "to_thread", timed_out)
    with pytest.raises(catalog_media.CatalogImageError, match="invalid_output"):
        await catalog_media.validate_public_https_url("https://cdn.example.test/image.png")


@pytest.mark.asyncio
async def test_image_download_dns_lookup_has_finite_deadline(monkeypatch):
    wait_for = asyncio.wait_for
    deadlines = []

    async def observed(awaitable, timeout):
        deadlines.append(timeout)
        return await wait_for(awaitable, timeout)

    monkeypatch.setattr(catalog_media.asyncio, "wait_for", observed)
    await catalog_media.validate_public_https_url("https://cdn.example.test/image.png")
    assert deadlines == [5.0]
