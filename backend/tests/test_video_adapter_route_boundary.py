"""Offline request-boundary regressions for keyed video adapters."""

import asyncio
import json
import socket
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from app.providers.video import fal_provider, kling_provider, catalog_media
from app.services.ai_routing import RoutePending, RouteTarget, UnsupportedModalityError


def box(kind, payload):
    return (len(payload) + 8).to_bytes(4, "big") + kind + payload


# Structurally complete ISO-BMFF video sample: ftyp, a video sample description,
# bounded nested boxes, and media data. No decoder is available in this test env.
FTYP = box(b"ftyp", b"isom\x00\x00\x02\x00isom")
VIDEO_HANDLER = box(b"hdlr", b"\x00" * 8 + b"vide" + b"\x00" * 12)
AUDIO_HANDLER = box(b"hdlr", b"\x00" * 8 + b"soun" + b"\x00" * 12)
SAMPLE_DESC = box(b"stsd", b"\x00" * 4 + (1).to_bytes(4, "big") + box(b"avc1", b"\x00" * 78))


def sample_mp4(handler=VIDEO_HANDLER):
    return FTYP + box(b"moov", box(b"trak", box(b"mdia", handler +
        box(b"minf", box(b"stbl", SAMPLE_DESC))))) + box(b"mdat", b"frame-bytes")


MP4 = sample_mp4()


@pytest.fixture(autouse=True)
def guarded_network(monkeypatch, tmp_path):
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("video adapter test attempted outbound network")))
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443)),
    ])
    for module in (fal_provider, kling_provider):
        monkeypatch.setattr(module, "settings", SimpleNamespace(DATA_DIR=tmp_path))
        monkeypatch.setattr(module, "get_key_manager", lambda: (_ for _ in ()).throw(
            AssertionError("canonical request consulted KeyManager")))


def client_for(monkeypatch, module, handler):
    real = httpx.AsyncClient
    monkeypatch.setattr(module.httpx, "AsyncClient", lambda **kwargs: real(
        transport=httpx.MockTransport(handler), **kwargs))


def target(provider, model):
    return RouteTarget("catalog-id", provider, model, "key-id", "VIDEO_GENERATION")


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider,model,auth", [
    (fal_provider, "fal", "fal-ai/hunyuan-video", "Key synthetic-fal"),
    (kling_provider, "kling", "kling-v2-6", "Bearer synthetic-kling"),
])
async def test_canonical_exact_model_key_and_media_auth_isolation(monkeypatch, tmp_path, module, provider, model, auth):
    seen = []

    def respond(request):
        seen.append(request)
        if request.method == "POST":
            assert request.headers["authorization"] == auth
            payload = json.loads(request.read())
            if provider == "fal":
                assert str(request.url) == "https://queue.fal.run/fal-ai/hunyuan-video"
                assert payload == {"prompt": "safe prompt", "aspect_ratio": "16:9",
                                   "resolution": "720p", "num_frames": 129}
                return httpx.Response(202, json={"request_id": "request-1",
                    "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/request-1/status",
                    "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/request-1"})
            assert payload["model_name"] == model
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "task-1"}})
        if request.url.host == "cdn.example.test":
            assert "authorization" not in request.headers
            return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
        assert request.headers["authorization"] == auth
        if provider == "fal":
            if str(request.url).endswith("/status"):
                return httpx.Response(200, json={"status": "COMPLETED"})
            return httpx.Response(200, json={"video": {"url": "https://cdn.example.test/clip.mp4"}})
        return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.test/clip.mp4"}]}}})

    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    result = await module.FalVideoProvider().generate_video("safe prompt", 5, tmp_path / "fal.mp4",
        route_target=target(provider, model), api_key="synthetic-fal") if provider == "fal" else \
        await module.KlingVideoProvider().generate_video("safe prompt", 5, tmp_path / "kling.mp4",
            route_target=target(provider, model), api_key="synthetic-kling")
    assert result.success
    assert result.file_path.read_bytes() == MP4
    assert len([r for r in seen if r.method == "POST"]) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider,model", [
    (fal_provider, "fal", "fal-ai/hunyuan-video"),
    (kling_provider, "kling", "kling-v2-6"),
])
async def test_mismatched_target_rejected_before_network(monkeypatch, tmp_path, module, provider, model):
    client_for(monkeypatch, module, lambda _: (_ for _ in ()).throw(AssertionError("HTTP called")))
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    with pytest.raises(ValueError):
        await cls().generate_video("secret prompt", 5, tmp_path / "x.mp4",
            route_target=RouteTarget("id", "other", model, "key", "VIDEO_GENERATION"), api_key="secret")
    with pytest.raises(ValueError):
        await cls().generate_video("secret prompt", 5, tmp_path / "x.mp4",
            route_target=RouteTarget("id", provider, model, "key", "IMAGE_GENERATION"), api_key="secret")


@pytest.mark.asyncio
async def test_fal_heterogeneous_catalog_model_is_unsupported(monkeypatch, tmp_path):
    client_for(monkeypatch, fal_provider, lambda _: (_ for _ in ()).throw(AssertionError("HTTP called")))
    with pytest.raises(UnsupportedModalityError):
        await fal_provider.FalVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target("fal", "fal-ai/veo3"), api_key="synthetic")


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider,model", [
    (fal_provider, "fal", "fal-ai/hunyuan-video"),
    (kling_provider, "kling", "kling-v2-6"),
])
async def test_accepted_job_cannot_resubmit_on_poll_failure(monkeypatch, tmp_path, module, provider, model):
    posts = []
    def respond(request):
        if request.method == "POST":
            posts.append(request)
            if provider == "fal":
                return httpx.Response(202, json={"request_id": "request-1",
                    "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/request-1/status",
                    "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/request-1"})
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "task-1"}})
        return httpx.Response(503, text="secret-upstream")
    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    with pytest.raises(RoutePending) as caught:
        await cls().generate_video("secret-prompt", 5, tmp_path / "x.mp4",
            route_target=target(provider, model), api_key="secret-key")
    assert len(posts) == 1
    assert "secret" not in str(caught.value)
    assert not (tmp_path / "x.mp4").exists()


@pytest.mark.asyncio
async def test_two_concurrent_kling_calls_keep_model_and_key_isolated(monkeypatch, tmp_path):
    def respond(request):
        if request.method == "POST":
            model = json.loads(request.read())["model_name"]
            assert (model, request.headers["authorization"]) in {
                ("kling-v2-6", "Bearer first-key"), ("kling-v3", "Bearer second-key")}
            return httpx.Response(200, json={"code": 0, "data": {"task_id": model}})
        if request.url.host == "cdn.example.test":
            assert "authorization" not in request.headers
            return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
        assert request.headers["authorization"] == (
            "Bearer first-key" if request.url.path.endswith("kling-v2-6") else "Bearer second-key")
        return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.test/video.mp4"}]}}})
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    provider = kling_provider.KlingVideoProvider()
    first, second = await asyncio.gather(
        provider.generate_video("first", 5, tmp_path / "first.mp4",
                                route_target=target("kling", "kling-v2-6"), api_key="first-key"),
        provider.generate_video("second", 5, tmp_path / "second.mp4",
                                route_target=target("kling", "kling-v3"), api_key="second-key"))
    assert first.success and second.success
    assert first.file_path.read_bytes() == second.file_path.read_bytes() == MP4


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [401, 403, 429, 404, 400])
async def test_kling_rejected_submission_is_safe_and_retryable_by_router(monkeypatch, tmp_path, status):
    calls = []
    def respond(request):
        calls.append(request)
        return httpx.Response(status, text="secret-key secret-prompt upstream body")
    client_for(monkeypatch, kling_provider, respond)
    with pytest.raises(Exception) as caught:
        await kling_provider.KlingVideoProvider().generate_video("secret-prompt", 5, tmp_path / "x.mp4",
            route_target=target("kling", "kling-v2-6"), api_key="secret-key")
    assert getattr(caught.value, "status_code", None) == status
    assert "secret" not in str(caught.value)
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("media_url,media_response", [
    ("http://cdn.example.test/video.mp4", None),
    ("https://127.0.0.1/video.mp4", None),
    ("https://cdn.example.test/video.mp4", httpx.Response(302, headers={"location": "https://127.0.0.1/private"})),
    ("https://cdn.example.test/video.mp4", httpx.Response(200, content=b"z" * 100,
        headers={"content-type": "text/html"})),
    ("https://cdn.example.test/video.mp4", httpx.Response(200, content=b"z" * 100,
        headers={"content-type": "video/mp4"})),
    ("https://cdn.example.test/video.mp4", httpx.Response(200, content=MP4,
        headers={"content-type": "video/mp4", "content-length": str(101 * 1024 * 1024)})),
])
async def test_kling_bad_media_is_pending_and_leaves_no_output(monkeypatch, tmp_path, media_url, media_response):
    requests = []
    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "task-1"}})
        if request.url.host == "api.klingai.com":
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": media_url}]}}})
        assert "authorization" not in request.headers
        return media_response
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    with pytest.raises(RoutePending):
        await kling_provider.KlingVideoProvider().generate_video("prompt", 5, tmp_path / "video.mp4",
            route_target=target("kling", "kling-v2-6"), api_key="key")
    assert not (tmp_path / "video.mp4").exists()
    assert not list(tmp_path.glob("*.part"))
    assert len([r for r in requests if r.method == "POST"]) == 1


@pytest.mark.asyncio
async def test_output_escape_rejected_before_submit(monkeypatch, tmp_path):
    client_for(monkeypatch, fal_provider, lambda _: (_ for _ in ()).throw(AssertionError("HTTP called")))
    with pytest.raises(Exception) as caught:
        await fal_provider.FalVideoProvider().generate_video("prompt", 5, tmp_path.parent / "escape.mp4",
            route_target=target("fal", "fal-ai/hunyuan-video"), api_key="key")
    assert getattr(caught.value, "code", None) == "invalid_output_path"


@pytest.mark.asyncio
async def test_fal_rejects_private_status_url_without_sending_key(monkeypatch, tmp_path):
    requests = []
    def respond(request):
        requests.append(request)
        return httpx.Response(202, json={"request_id": "id-1",
            "status_url": "https://127.0.0.1/private",
            "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1"})
    client_for(monkeypatch, fal_provider, respond)
    with pytest.raises(RoutePending):
        await fal_provider.FalVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target("fal", "fal-ai/hunyuan-video"), api_key="key")
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_legacy_error_is_sanitized(monkeypatch, tmp_path):
    class KeyManager:
        async def get_active_key(self, provider):
            return SimpleNamespace(api_key="synthetic-key", key_id="id", masked_key="S***Y")
        async def report_result(self, *args, **kwargs):
            return None
    monkeypatch.setattr(kling_provider, "get_key_manager", lambda: KeyManager())
    client_for(monkeypatch, kling_provider, lambda _: httpx.Response(
        401, text="synthetic-key S***Y secret-prompt"))
    result = await kling_provider.KlingVideoProvider().generate_video(
        "secret-prompt", 5, tmp_path / "legacy.mp4")
    assert not result.success
    assert result.error_code == "HTTP_401"
    assert all(value not in repr(result) for value in ("synthetic-key", "S***Y", "secret-prompt"))


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider", [(fal_provider, "fal"), (kling_provider, "kling")])
async def test_legacy_success_and_key_manager_accounting(monkeypatch, tmp_path, module, provider):
    reported = []
    class KeyManager:
        async def get_active_key(self, requested):
            assert requested == provider
            return SimpleNamespace(api_key="legacy-key", key_id="legacy-id", masked_key="masked")
        async def get_keys_for_provider(self, requested):
            assert requested == provider
            return [{"successful_requests": 2}]
        async def report_result(self, requested, key_id, **kwargs):
            reported.append((requested, key_id, kwargs))
    monkeypatch.setattr(module, "get_key_manager", lambda: KeyManager())
    def respond(request):
        if request.method == "POST":
            payload = json.loads(request.read())
            if provider == "fal":
                assert payload["seconds_total"] == 5
                return httpx.Response(202, json={"request_id": "id-1",
                    "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1/status",
                    "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1"})
            assert payload["model_name"] == "kling-v1"
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}})
        if request.url.host == "cdn.example.test":
            assert "authorization" not in request.headers
            return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
        if provider == "fal":
            return (httpx.Response(200, json={"status": "COMPLETED"}) if str(request.url).endswith("status")
                    else httpx.Response(200, json={"video": {"url": "https://cdn.example.test/x.mp4"}}))
        return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
            "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    instance = cls()
    assert await instance.validate_configuration()
    assert (await instance.get_quota())[0].used == 10
    result = await instance.generate_video("legacy prompt", 5, tmp_path / "legacy.mp4")
    assert result.success and result.file_path.read_bytes() == MP4
    assert reported == [(provider, "legacy-id", {"success": True})]
    assert "masked" not in repr(result)


@pytest.mark.asyncio
@pytest.mark.parametrize("provider,state", [("fal", "FAILED"), ("fal", "CANCELED"), ("kling", "failed")])
async def test_known_failed_job_has_safe_non_pending_outcome(monkeypatch, tmp_path, provider, state):
    module = fal_provider if provider == "fal" else kling_provider
    def respond(request):
        if request.method == "POST":
            return (httpx.Response(202, json={"request_id": "id-1",
                "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1/status",
                "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1"})
                if provider == "fal" else httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}}))
        return (httpx.Response(200, json={"status": state, "error": "secret-key secret-prompt"})
                if provider == "fal" else httpx.Response(200, json={"code": 0, "data": {
                    "task_status": state, "task_status_msg": "secret-key secret-prompt"}}))
    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    model = "fal-ai/hunyuan-video" if provider == "fal" else "kling-v2-6"
    with pytest.raises(Exception) as caught:
        await cls().generate_video("secret-prompt", 5, tmp_path / "x.mp4",
            route_target=target(provider, model), api_key="secret-key")
    assert not isinstance(caught.value, RoutePending)
    assert getattr(caught.value, "code", None) == "job_failed"
    assert "secret" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["fal", "kling"])
async def test_poll_exhaustion_is_terminal_pending(monkeypatch, tmp_path, provider):
    module = fal_provider if provider == "fal" else kling_provider
    polls = []
    def respond(request):
        if request.method == "POST":
            return (httpx.Response(202, json={"request_id": "id-1",
                "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1/status",
                "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1"})
                if provider == "fal" else httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}}))
        polls.append(request)
        return (httpx.Response(200, json={"status": "IN_PROGRESS"}) if provider == "fal"
                else httpx.Response(200, json={"code": 0, "data": {"task_status": "processing"}}))
    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    model = "fal-ai/hunyuan-video" if provider == "fal" else "kling-v2-6"
    with pytest.raises(RoutePending) as caught:
        await cls().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target(provider, model), api_key="key")
    assert caught.value.outcome == "timeout"
    assert len(polls) == 60


@pytest.mark.asyncio
async def test_kling_explicit_submit_rejection_is_non_pending(monkeypatch, tmp_path):
    client_for(monkeypatch, kling_provider, lambda _: httpx.Response(200, json={
        "code": 1001, "message": "secret-key secret-prompt", "data": None}))
    with pytest.raises(Exception) as caught:
        await kling_provider.KlingVideoProvider().generate_video("secret-prompt", 5, tmp_path / "x.mp4",
            route_target=target("kling", "kling-v2-6"), api_key="secret-key")
    assert not isinstance(caught.value, RoutePending)
    assert getattr(caught.value, "code", None) == "provider_unavailable"
    assert "secret" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider", [(fal_provider, "fal"), (kling_provider, "kling")])
async def test_legacy_quota_without_keys_retains_zero_limit(monkeypatch, module, provider):
    class KeyManager:
        async def get_keys_for_provider(self, requested):
            assert requested == provider
            return []
    monkeypatch.setattr(module, "get_key_manager", lambda: KeyManager())
    quota = (await (module.FalVideoProvider() if provider == "fal" else module.KlingVideoProvider()).get_quota())[0]
    assert (quota.used, quota.limit, quota.remaining) == (0, 0, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize("module,provider", [(fal_provider, "fal"), (kling_provider, "kling")])
async def test_legacy_accounting_failure_does_not_hide_completed_video(monkeypatch, tmp_path, module, provider):
    class KeyManager:
        async def get_active_key(self, provider):
            return SimpleNamespace(api_key="key", key_id="id")
        async def report_result(self, *args, **kwargs):
            raise RuntimeError("secret-key accounting error")
    monkeypatch.setattr(module, "get_key_manager", lambda: KeyManager())
    def respond(request):
        if request.method == "POST":
            return (httpx.Response(202, json={"request_id": "id-1",
                "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1/status",
                "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-1"})
                if provider == "fal" else httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}}))
        if provider == "fal" and request.url.host == "queue.fal.run":
            return (httpx.Response(200, json={"status": "COMPLETED"}) if str(request.url).endswith("status")
                    else httpx.Response(200, json={"video": {"url": "https://cdn.example.test/x.mp4"}}))
        if request.url.host == "api.klingai.com":
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
        return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
    client_for(monkeypatch, module, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(module.asyncio, "sleep", no_sleep)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    result = await cls().generate_video("prompt", 5, tmp_path / "x.mp4")
    assert result.success and result.file_path.read_bytes() == MP4


@pytest.mark.asyncio
async def test_legacy_rotates_only_after_definitive_key_rejection(monkeypatch, tmp_path):
    entries = iter([SimpleNamespace(api_key="first", key_id="one"),
                    SimpleNamespace(api_key="second", key_id="two")])
    class KeyManager:
        async def get_active_key(self, provider):
            return next(entries, None)
        async def report_result(self, *args, **kwargs):
            return None
    monkeypatch.setattr(kling_provider, "get_key_manager", lambda: KeyManager())
    posts = []
    def respond(request):
        if request.method == "POST":
            posts.append(request)
            return (httpx.Response(401, text="first secret") if len(posts) == 1 else
                    httpx.Response(200, json={"code": 0, "data": {"task_id": "id-2"}}))
        if request.url.host == "api.klingai.com":
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
        return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    result = await kling_provider.KlingVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4")
    assert result.success
    assert [r.headers["authorization"] for r in posts] == ["Bearer first", "Bearer second"]


@pytest.mark.asyncio
async def test_fal_legacy_rotation_uses_second_key_only_after_explicit_429(monkeypatch, tmp_path):
    entries = iter([SimpleNamespace(api_key="first", key_id="one"),
                    SimpleNamespace(api_key="second", key_id="two")])
    class KeyManager:
        async def get_active_key(self, provider):
            return next(entries, None)
        async def report_result(self, *args, **kwargs):
            return None
    monkeypatch.setattr(fal_provider, "get_key_manager", lambda: KeyManager())
    posts = []
    def respond(request):
        if request.method == "POST":
            posts.append(request)
            return (httpx.Response(429, text="first secret") if len(posts) == 1 else
                    httpx.Response(202, json={"request_id": "id-2",
                        "status_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-2/status",
                        "response_url": "https://queue.fal.run/fal-ai/hunyuan-video/requests/id-2"}))
        if request.url.host == "cdn.example.test":
            return httpx.Response(200, content=MP4, headers={"content-type": "video/mp4"})
        return (httpx.Response(200, json={"status": "COMPLETED"}) if str(request.url).endswith("status")
                else httpx.Response(200, json={"video": {"url": "https://cdn.example.test/x.mp4"}}))
    client_for(monkeypatch, fal_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(fal_provider.asyncio, "sleep", no_sleep)
    result = await fal_provider.FalVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4")
    assert result.success
    assert [r.headers["authorization"] for r in posts] == ["Key first", "Key second"]


@pytest.mark.asyncio
async def test_stream_cap_cleans_partial_temp_and_preserves_existing_output(monkeypatch, tmp_path):
    class Chunks(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield MP4[:24]
            yield MP4[24:]
    monkeypatch.setattr(catalog_media, "MAX_VIDEO_BYTES", 32)
    def respond(request):
        if request.method == "POST":
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}})
        if request.url.host == "api.klingai.com":
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
        return httpx.Response(200, stream=Chunks(), headers={"content-type": "video/mp4"})
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    output = tmp_path / "x.mp4"
    output.write_bytes(b"existing-output")
    with pytest.raises(RoutePending):
        await kling_provider.KlingVideoProvider().generate_video("prompt", 5, output,
            route_target=target("kling", "kling-v2-6"), api_key="key")
    assert output.read_bytes() == b"existing-output"
    assert not list(tmp_path.glob("*.part"))


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["poll", "media"])
async def test_post_acceptance_http_401_does_not_enable_fallback(monkeypatch, tmp_path, stage):
    requests = []
    def respond(request):
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}})
        if request.url.host == "api.klingai.com":
            if stage == "poll":
                return httpx.Response(401, text="key prompt")
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
        return httpx.Response(401, text="key prompt")
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    with pytest.raises(RoutePending):
        await kling_provider.KlingVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target("kling", "kling-v2-6"), api_key="key")
    assert len([r for r in requests if r.method == "POST"]) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_code", [None, "0", False, 0.0, [], {}])
async def test_kling_ambiguous_submit_code_is_terminal_pending(monkeypatch, tmp_path, bad_code):
    payload = {"data": {"task_id": "id-1"}}
    if bad_code is not None:
        payload["code"] = bad_code
    calls = []
    def respond(request):
        calls.append(request)
        return httpx.Response(200, json=payload)
    client_for(monkeypatch, kling_provider, respond)
    with pytest.raises(RoutePending):
        await kling_provider.KlingVideoProvider().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target("kling", "kling-v2-6"), api_key="key")
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["fal", "kling"])
async def test_trickling_submit_body_hits_total_deadline(monkeypatch, tmp_path, provider):
    module = fal_provider if provider == "fal" else kling_provider
    class Trickling(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"{"
            await asyncio.Event().wait()
    client_for(monkeypatch, module, lambda _: httpx.Response(
        202 if provider == "fal" else 200, stream=Trickling(),
        headers={"content-type": "application/json"}))
    monkeypatch.setattr(module, "SUBMIT_TIMEOUT", 0.02, raising=False)
    cls = module.FalVideoProvider if provider == "fal" else module.KlingVideoProvider
    model = "fal-ai/hunyuan-video" if provider == "fal" else "kling-v2-6"
    with pytest.raises(RoutePending) as caught:
        await asyncio.wait_for(cls().generate_video("prompt", 5, tmp_path / "x.mp4",
            route_target=target(provider, model), api_key="key"), 0.2)
    assert caught.value.outcome == "timeout"


@pytest.mark.asyncio
@pytest.mark.parametrize("content", [
    b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00isom" + b"x" * 32,
    sample_mp4(AUDIO_HANDLER),
    MP4[:-4],
    FTYP + box(b"moov", box(b"trak", box(b"mdia", VIDEO_HANDLER))) + box(b"mdat", b""),
])
async def test_structurally_invalid_mp4_cannot_replace_old_output(monkeypatch, tmp_path, content):
    def respond(request):
        if request.method == "POST":
            return httpx.Response(200, json={"code": 0, "data": {"task_id": "id-1"}})
        if request.url.host == "api.klingai.com":
            return httpx.Response(200, json={"code": 0, "data": {"task_status": "succeed",
                "task_result": {"videos": [{"url": "https://cdn.example.test/x.mp4"}]}}})
        return httpx.Response(200, content=content, headers={"content-type": "video/mp4"})
    client_for(monkeypatch, kling_provider, respond)
    async def no_sleep(_): pass
    monkeypatch.setattr(kling_provider.asyncio, "sleep", no_sleep)
    output = tmp_path / "x.mp4"
    output.write_bytes(b"old-output")
    with pytest.raises(RoutePending):
        await kling_provider.KlingVideoProvider().generate_video("prompt", 5, output,
            route_target=target("kling", "kling-v2-6"), api_key="key")
    assert output.read_bytes() == b"old-output"
    assert not list(tmp_path.glob("*.part"))
