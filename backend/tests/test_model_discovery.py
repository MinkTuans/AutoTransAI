"""Discovery contract tests: HTTP is synthetic; no database or real credentials."""
import asyncio
from dataclasses import asdict

import httpx
import pytest


SECRET = "synthetic-discovery-secret"


@pytest.fixture
def discovery():
    from app.services import model_discovery_service
    return model_discovery_service


async def scan(discovery, provider, pages, **limits):
    requests = []

    def respond(request):
        requests.append(request)
        page = pages[len(requests) - 1]
        if isinstance(page, Exception):
            raise page
        return page if isinstance(page, httpx.Response) else httpx.Response(200, json=page)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as client:
        result = await discovery.discover_models(
            provider, SECRET, client=client, limits=discovery.DiscoveryLimits(**limits)
        )
        assert not client.is_closed
    assert all(SECRET not in str(request.url) for request in requests)
    assert all(request.method == "GET" and not request.content for request in requests)
    assert SECRET not in repr(asdict(result))
    return result, requests


async def test_gemini_paginates_exact_versions_and_deduplicates(discovery):
    model = {"name": "models/Gemini-future-001", "baseModelId": "Gemini-future",
             "displayName": "Future", "supportedGenerationMethods": ["generateContent"],
             "inputTokenLimit": 1000, "outputTokenLimit": 100}
    result, requests = await scan(discovery, "gemini", [
        {"models": [model], "nextPageToken": "page-two"},
        {"models": [model, {"name": "models/Gemini-future-002"}]},
    ])
    assert result.status == "complete" and result.pages_fetched == 2
    assert result.access_scope == "credential"
    assert [m.remote_model_id for m in result.models] == ["Gemini-future-001", "Gemini-future-002"]
    assert result.models[0].metadata["supportedGenerationMethods"] == ["generateContent"]
    assert result.models[0].metadata["inputTokenLimit"] == 1000
    assert requests[0].url.host == "generativelanguage.googleapis.com"
    assert requests[0].headers["x-goog-api-key"] == SECRET
    assert requests[1].url.params["pageToken"] == "page-two"


async def test_openai_preserves_custom_ids_and_allowlists_metadata(discovery):
    result, requests = await scan(discovery, "openai", [{"object": "list", "data": [
        {"id": "ft:Future:Org:Case-Sensitive", "owned_by": "organization", "created": 123,
         "object": "model", "api_key": SECRET, "url": "https://example.com/?key=" + SECRET},
    ]}])
    assert result.status == "complete" and result.access_scope == "credential"
    assert result.models[0].remote_model_id == "ft:Future:Org:Case-Sensitive"
    assert result.models[0].metadata == {"owned_by": "organization", "created": 123}
    assert requests[0].url == "https://api.openai.com/v1/models"
    assert requests[0].headers["authorization"] == "Bearer " + SECRET


async def test_anthropic_cursor_headers_and_safe_metadata(discovery):
    result, requests = await scan(discovery, "anthropic", [
        {"data": [{"id": "claude-future-001", "display_name": "Future", "type": "model",
                   "created_at": "2026-01-01T00:00:00Z", "max_input_tokens": 1000}],
         "first_id": "claude-future-001", "last_id": "claude-future-001", "has_more": True},
        {"data": [{"id": "claude-future-002"}], "last_id": "claude-future-002", "has_more": False},
    ])
    assert result.status == "complete" and len(result.models) == 2
    assert result.models[0].display_name == "Future"
    assert result.models[0].metadata["max_input_tokens"] == 1000
    assert requests[0].url.host == "api.anthropic.com"
    assert requests[0].headers["x-api-key"] == SECRET
    assert requests[0].headers["anthropic-version"] == "2023-06-01"
    assert requests[1].url.params["after_id"] == "claude-future-001"


async def test_elevenlabs_catalog_is_not_entitlement_and_keeps_negative_evidence(discovery):
    result, requests = await scan(discovery, "elevenlabs", [[
        {"model_id": "eleven_future", "name": "Future\n" + SECRET,
         "can_do_text_to_speech": False, "can_do_voice_conversion": True,
         "requires_alpha_access": True, "description": SECRET},
    ]])
    assert result.status == "complete" and result.access_scope == "catalog"
    assert result.models[0].metadata == {"can_do_text_to_speech": False,
        "can_do_voice_conversion": True, "requires_alpha_access": True}
    assert "\n" not in result.models[0].display_name
    assert requests[0].url == "https://api.elevenlabs.io/v1/models"
    assert requests[0].headers["xi-api-key"] == SECRET


async def test_fal_paginates_public_catalog_and_only_keeps_safe_metadata(discovery):
    result, requests = await scan(discovery, "fal", [
        {"models": [{"endpoint_id": "fal-ai/future/dev", "metadata": {
            "display_name": "Future", "category": "text-to-image", "status": "active",
            "model_url": "https://evil.example/" + SECRET}}], "has_more": True, "next_cursor": "Mg=="},
        {"models": [{"endpoint_id": "fal-ai/future/pro"}], "has_more": False, "next_cursor": None},
    ])
    assert result.status == "complete" and result.access_scope == "catalog"
    assert result.models[0].remote_model_id == "fal-ai/future/dev"
    assert result.models[0].metadata == {"category": "text-to-image", "status": "active"}
    assert requests[0].url.host == "api.fal.ai"
    assert requests[0].headers["authorization"] == "Key " + SECRET
    assert requests[1].url.params["cursor"] == "Mg=="


@pytest.mark.parametrize("provider", ["kling", "google_tts", "google_cloud_tts", "edge_tts", "unknown"])
async def test_unsupported_providers_never_make_requests(discovery, provider):
    result, requests = await scan(discovery, provider, [])
    assert result.status == "unsupported" and result.models == () and requests == []


@pytest.mark.parametrize(("status", "code"), [(401, "auth_invalid"), (403, "permission_denied"),
    (429, "rate_limited"), (503, "transient"), (400, "request_rejected"), (302, "redirect_rejected")])
async def test_http_failures_are_classified_without_echoing_body(discovery, status, code, caplog):
    result, requests = await scan(discovery, "openai", [httpx.Response(status,
        text=SECRET, headers={"location": "https://evil.example/" + SECRET})])
    assert result.status == "failed" and result.error_code == code and len(requests) == 1
    assert SECRET not in caplog.text


@pytest.mark.parametrize("page", [{}, {"data": {}}, {"data": [None]}, {"data": [{"id": ""}]},
    {"data": [{"id": "bad\nidentity"}]}, {"data": [{"id": SECRET}]},
    {"data": [{"id": "x" * 256}]}, {"data": [{"id": "good"}], "has_more": True}])
async def test_malformed_results_never_report_complete(discovery, page):
    result, _ = await scan(discovery, "openai", [page])
    assert result.status in {"failed", "partial"} and result.error_code == "malformed"


async def test_empty_result_is_ambiguous(discovery):
    result, _ = await scan(discovery, "openai", [{"data": []}])
    assert result.status == "partial" and result.error_code == "empty_result"


@pytest.mark.parametrize("second", [{"models": [{"name": "models/b"}], "nextPageToken": "again"},
    {"models": [], "nextPageToken": "third"}, {"models": [{"name": "models/a"}], "nextPageToken": "third"},
    {"models": [{"name": "models/b"}], "nextPageToken": SECRET}])
async def test_suspicious_pagination_is_partial_and_bounded(discovery, second):
    result, requests = await scan(discovery, "gemini", [
        {"models": [{"name": "models/a"}], "nextPageToken": "again"}, second])
    assert result.status == "partial" and result.error_code in {"incomplete", "malformed"}
    assert result.models[0].remote_model_id == "a" and len(requests) == 2


async def test_failure_after_valid_page_preserves_partial_snapshot(discovery):
    result, _ = await scan(discovery, "gemini", [
        {"models": [{"name": "models/a"}], "nextPageToken": "next"},
        httpx.ReadTimeout(SECRET)])
    assert result.status == "partial" and result.error_code == "timeout"
    assert [m.remote_model_id for m in result.models] == ["a"]


@pytest.mark.parametrize(("limits", "pages", "code"), [
    ({"max_pages": 1}, [{"models": [{"name": "models/a"}], "nextPageToken": "next"}], "page_limit"),
    ({"max_models": 1}, [{"models": [{"name": "models/a"}, {"name": "models/b"}]}], "model_limit"),
    ({"max_bytes": 10}, [{"models": [{"name": "models/a"}]}], "byte_limit"),
])
async def test_limits_cannot_return_complete(discovery, limits, pages, code):
    result, _ = await scan(discovery, "gemini", pages, **limits)
    assert result.status in {"partial", "failed"} and result.error_code == code


async def test_total_deadline_cancels_slow_transport(discovery):
    async def slow(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json={"data": [{"id": "a"}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(slow)) as client:
        result = await discovery.discover_models("openai", SECRET, client=client,
            limits=discovery.DiscoveryLimits(total_timeout=0.01))
    assert result.status == "failed" and result.error_code == "timeout"


async def test_stream_byte_bound_stops_before_remaining_body(discovery):
    chunks_read = []

    class LargeStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            for chunk in [b"{" * 11, b"never read"]:
                chunks_read.append(chunk)
                yield chunk

    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, stream=LargeStream()))) as client:
        result = await discovery.discover_models("openai", SECRET, client=client,
            limits=discovery.DiscoveryLimits(max_bytes=10))
    assert result.error_code == "byte_limit" and len(chunks_read) == 1


async def test_injected_client_defaults_cannot_leak_across_providers(discovery):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json={"data": [{"id": "a"}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond),
        headers={"x-api-key": "wrong-provider-secret"}, params={"api_key": "wrong-secret"},
        cookies={"session": "wrong-session"}, auth=("wrong", "credentials")) as client:
        result = await discovery.discover_models("openai", SECRET, client=client)
    assert result.status == "complete"
    assert "wrong" not in str(seen[0].url) + repr(dict(seen[0].headers))


@pytest.mark.parametrize("rows", [[], [{"name": "models/a"}]])
async def test_terminal_page_without_progress_is_suspicious(discovery, rows):
    result, _ = await scan(discovery, "gemini", [
        {"models": [{"name": "models/a"}], "nextPageToken": "next"}, {"models": rows}])
    assert result.status == "partial" and result.error_code == "incomplete"


async def test_metadata_sanitization_cannot_reconstruct_a_secret(discovery):
    result, _ = await scan(discovery, "elevenlabs", [[{
        "model_id": "model", "name": SECRET[:5] + "\n" + SECRET[5:]}]])
    assert result.status == "complete"


async def test_anthropic_retains_allowlisted_capability_evidence(discovery):
    result, _ = await scan(discovery, "anthropic", [{"data": [{"id": "future",
        "capabilities": {"image_input": {"supported": True, "secret": SECRET},
                         "thinking": {"supported": False}, "untrusted": SECRET}}], "has_more": False}])
    assert result.models[0].metadata["capabilities"] == {
        "image_input": {"supported": True}, "thinking": {"supported": False}}


async def test_rejects_credential_encoded_in_cursor(discovery):
    encoded = "".join("%" + format(ord(c), "02X") for c in SECRET)
    result, requests = await scan(discovery, "gemini", [
        {"models": [{"name": "models/a"}], "nextPageToken": encoded},
        {"models": [{"name": "models/b"}]}])
    assert result.status != "complete" and len(requests) == 1


@pytest.mark.parametrize("body", [b"not json", b"{", b'{"data":[],"data":[{"id":"a"}]}'])
async def test_invalid_or_ambiguous_json_is_rejected(discovery, body):
    result, _ = await scan(discovery, "openai", [httpx.Response(200, content=body)])
    assert result.status == "failed" and result.error_code == "malformed"


@pytest.mark.parametrize("credential", ["", "bad\r\nheader", "non-ascii-\u00e9", None])
async def test_invalid_credentials_fail_without_http(discovery, credential):
    def unexpected(request):
        pytest.fail("invalid credentials must not leave the process")
    async with httpx.AsyncClient(transport=httpx.MockTransport(unexpected)) as client:
        result = await discovery.discover_models("openai", credential, client=client)
    assert result.status == "failed" and result.error_code == "auth_invalid"


async def test_byte_limit_covers_all_pages(discovery):
    result, _ = await scan(discovery, "gemini", [
        {"models": [{"name": "models/a"}], "nextPageToken": "next"},
        {"models": [{"name": "models/b"}]}], max_bytes=75)
    assert result.status == "partial" and result.error_code == "byte_limit"


async def test_transport_exception_text_never_escapes(discovery):
    result, _ = await scan(discovery, "openai", [httpx.ConnectError(SECRET)])
    assert result.status == "failed" and result.error_code == "transient"


async def test_caller_cancellation_propagates(discovery):
    async def cancelled(request):
        raise asyncio.CancelledError()
    async with httpx.AsyncClient(transport=httpx.MockTransport(cancelled)) as client:
        with pytest.raises(asyncio.CancelledError):
            await discovery.discover_models("openai", SECRET, client=client)


@pytest.mark.parametrize("body", [b'{"data":[{"id":"a"}],"number":NaN}',
    b'{"data":[{"id":"a"}],"number":Infinity}'])
async def test_nonstandard_json_numbers_cannot_authorize_complete_result(discovery, body):
    result, _ = await scan(discovery, "openai", [httpx.Response(200, content=body)])
    assert result.status == "failed" and result.error_code == "malformed"


@pytest.mark.parametrize(("provider", "body"), [
    ("fal", {"models": [{"endpoint_id": "a"}], "has_more": False, "next_cursor": False}),
    ("anthropic", {"data": [{"id": "a"}], "has_more": False, "last_id": 123}),
])
async def test_malformed_terminal_cursor_cannot_authorize_complete_result(discovery, provider, body):
    result, _ = await scan(discovery, provider, [body])
    assert result.status == "failed" and result.error_code == "malformed"
