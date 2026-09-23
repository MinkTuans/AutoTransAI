"""Keyless image downloads must be bounded, decoded, and stay in task storage."""

import asyncio
import socket
from io import BytesIO
from types import SimpleNamespace

import httpx
import pytest
from PIL import Image

from app.providers.image import local_image_provider, pollinations_provider


def png():
    output = BytesIO()
    Image.new("RGB", (2, 2), (1, 2, 3)).save(output, "PNG")
    return output.getvalue()


@pytest.fixture(autouse=True)
def sandbox(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("keyless adapter attempted outbound network")))
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443)),
    ])
    task_settings = SimpleNamespace(DATA_DIR=tmp_path / "app_data")
    monkeypatch.setattr(pollinations_provider, "get_settings", lambda: task_settings)
    monkeypatch.setattr(local_image_provider, "get_settings", lambda: task_settings)


def mock_client(monkeypatch, responder):
    client_type = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: client_type(
        transport=httpx.MockTransport(responder), **kwargs,
    ))


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_type", [pollinations_provider.PollinationsImageProvider,
                                            local_image_provider.LocalImageProvider])
async def test_keyless_public_redirect_downloads_verified_image_without_auth(monkeypatch, provider_type):
    requests = []

    def respond(request):
        requests.append(request)
        assert "authorization" not in request.headers
        if request.url.host in ("image.pollinations.ai", "picsum.photos"):
            return httpx.Response(302, headers={"location": "https://cdn.example.test/image.png"})
        assert request.url.host == "cdn.example.test"
        return httpx.Response(200, content=png(), headers={"content-type": "image/png"})

    mock_client(monkeypatch, respond)
    result = await provider_type().generate_image("synthetic prompt")
    assert result.success and result.metadata["image_bytes"] == png()
    assert len(requests) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_type", [pollinations_provider.PollinationsImageProvider,
                                            local_image_provider.LocalImageProvider])
async def test_keyless_private_redirect_is_rejected_before_fetch(monkeypatch, provider_type):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(302, headers={"location": "https://127.0.0.1/private"})

    mock_client(monkeypatch, respond)
    from app.providers.image import local_image_provider as local_module
    async def no_ffmpeg(*args, **kwargs):
        raise RuntimeError("offline")
    monkeypatch.setattr(local_module, "run_ffmpeg_with_progress_async", no_ffmpeg)
    result = await provider_type().generate_image("synthetic prompt")
    assert not result.success
    assert len(requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_type", [pollinations_provider.PollinationsImageProvider,
                                            local_image_provider.LocalImageProvider])
async def test_keyless_rejects_output_path_outside_data_root_before_download(monkeypatch, tmp_path, provider_type):
    def respond(request):
        raise AssertionError("unsafe path must be rejected before network")

    mock_client(monkeypatch, respond)
    outside = tmp_path / "outside.png"
    result = await provider_type().generate_image("synthetic prompt", options={"output_path": outside})
    assert not result.success
    assert not outside.exists()


@pytest.mark.asyncio
async def test_local_rejects_even_in_root_output_path_before_work(monkeypatch, tmp_path):
    def respond(request):
        raise AssertionError("caller output path must be rejected before network")

    mock_client(monkeypatch, respond)
    target = tmp_path / "app_data" / "caller.jpg"
    result = await local_image_provider.LocalImageProvider().generate_image(
        "synthetic prompt", options={"output_path": target},
    )
    assert not result.success and result.error_code == "INVALID_OUTPUT_PATH"
    assert not target.exists()


@pytest.mark.asyncio
async def test_local_fallback_uses_unique_data_temp_and_removes_it(monkeypatch, tmp_path):
    def respond(request):
        return httpx.Response(503)

    mock_client(monkeypatch, respond)
    monkeypatch.setattr(local_image_provider, "get_ffmpeg_executable", lambda: "synthetic-ffmpeg")
    output_paths = []

    async def render(command, **kwargs):
        path = command[-1]
        output_paths.append(path)
        from pathlib import Path
        Path(path).write_bytes(png())

    monkeypatch.setattr(local_image_provider, "run_ffmpeg_with_progress_async", render)
    first = await local_image_provider.LocalImageProvider().generate_image("first")
    second = await local_image_provider.LocalImageProvider().generate_image("second")
    assert first.success and second.success
    assert output_paths[0] != output_paths[1]
    assert all(str(tmp_path / "app_data") in path for path in output_paths)
    assert all(not __import__("pathlib").Path(path).exists() for path in output_paths)


@pytest.mark.asyncio
async def test_pollinations_redirect_chain_is_capped(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(302, headers={"location": f"https://cdn.example.test/step-{len(requests)}"})

    mock_client(monkeypatch, respond)
    result = await pollinations_provider.PollinationsImageProvider().generate_image("synthetic prompt")
    assert not result.success and len(requests) == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("content_type,body", [
    ("text/html", b"<html>bad</html>"),
    ("image/png", b"\x89PNG\r\n\x1a\n" + b"x" * 24),
    ("image/png", b"x" * (10 * 1024 * 1024 + 1)),
])
async def test_pollinations_rejects_wrong_mime_corrupt_and_oversized_image(
    monkeypatch, content_type, body,
):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, content=body, headers={"content-type": content_type})

    mock_client(monkeypatch, respond)
    result = await pollinations_provider.PollinationsImageProvider().generate_image("synthetic prompt")
    assert not result.success and len(requests) == 1


@pytest.mark.asyncio
async def test_local_temp_is_removed_when_ffmpeg_fails_after_writing(monkeypatch):
    def respond(request):
        return httpx.Response(503)

    mock_client(monkeypatch, respond)
    monkeypatch.setattr(local_image_provider, "get_ffmpeg_executable", lambda: "synthetic-ffmpeg")
    paths = []

    async def render(command, **kwargs):
        from pathlib import Path
        path = Path(command[-1])
        paths.append(path)
        path.write_bytes(b"partial image")
        raise RuntimeError("synthetic-secret")

    monkeypatch.setattr(local_image_provider, "run_ffmpeg_with_progress_async", render)
    result = await local_image_provider.LocalImageProvider().generate_image("synthetic prompt")
    assert not result.success and len(paths) == 1 and not paths[0].exists()
