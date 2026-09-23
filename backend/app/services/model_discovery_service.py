"""Bounded, read-only discovery. Callers own credentials, reconciliation and persistence.

Only COMPLETE nonempty results are complete listings. Catalog scope never establishes
key entitlement. Even credential scope indicates listing visibility, not successful usage.
An injected client must have trusted transport/event hooks: hooks can observe auth headers.
"""
import asyncio
import json

import httpx

from app.providers.discovery.adapters import ADAPTERS, DiscoveryError
from app.providers.discovery.types import DiscoveryLimits, DiscoveryResult


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DiscoveryError("malformed")
        result[key] = value
    return result


def _reject_constant(value):
    raise DiscoveryError("malformed")


async def discover_models(
    provider_id: str, credential: str | None, *, client: httpx.AsyncClient | None = None,
    limits: DiscoveryLimits | None = None,
) -> DiscoveryResult:
    adapter = ADAPTERS.get(provider_id)
    if adapter is None:
        return DiscoveryResult("unsupported", error_code="unsupported")
    limits = limits or DiscoveryLimits()
    scope = adapter.access_scope
    if (credential is not None and (not isinstance(credential, str) or not credential
            or len(credential) > 8192 or any(not 33 <= ord(c) <= 126 for c in credential))
            or not credential and scope == "credential"):
        return DiscoveryResult("failed", error_code="auth_invalid", access_scope=scope)
    if client is None:
        async with httpx.AsyncClient(trust_env=False) as owned_client:
            return await discover_models(provider_id, credential, client=owned_client, limits=limits)

    models = {}
    pages = 0
    bytes_read = 0
    rows_read = 0
    cursors = set()
    cursor = None
    error = None
    try:
        async with asyncio.timeout(limits.total_timeout):
            while True:
                if pages >= limits.max_pages:
                    raise DiscoveryError("page_limit")
                params = {adapter.page_size_param: 100} if adapter.page_size_param else {}
                if cursor:
                    params[adapter.cursor_param] = cursor
                # Build directly to exclude injected client defaults (auth, cookies, query params).
                request = httpx.Request("GET", adapter.url, headers=adapter.headers(credential), params=params,
                    extensions={"timeout": httpx.Timeout(limits.request_timeout).as_dict()})
                response = await client.send(request, stream=True, auth=None, follow_redirects=False)
                try:
                    if response.status_code != 200:
                        code = {401: "auth_invalid", 403: "permission_denied", 429: "rate_limited"}.get(
                            response.status_code, "transient" if response.status_code >= 500 else
                            "redirect_rejected" if 300 <= response.status_code < 400 else "request_rejected")
                        raise DiscoveryError(code)
                    # Request identity encoding and reject compression to bound decoded memory, too.
                    if response.headers.get("content-encoding", "identity") != "identity":
                        raise DiscoveryError("malformed")
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        bytes_read += len(chunk)
                        if bytes_read > limits.max_bytes:
                            raise DiscoveryError("byte_limit")
                        body.extend(chunk)
                finally:
                    await response.aclose()
                try:
                    payload = json.loads(body, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
                except (ValueError, UnicodeError, RecursionError):
                    raise DiscoveryError("malformed") from None
                rows, next_cursor = adapter.page(payload, credential)
                pages += 1
                previous_count = len(models)
                for row in rows:
                    rows_read += 1
                    if rows_read > limits.max_models:
                        raise DiscoveryError("model_limit")
                    model = adapter.model(row, credential)
                    models.setdefault(model.remote_model_id, model)
                if pages > 1 and len(models) == previous_count:
                    raise DiscoveryError("incomplete")
                if not next_cursor:
                    if not models:
                        raise DiscoveryError("empty_result")
                    return DiscoveryResult("complete", tuple(models.values()), pages_fetched=pages, access_scope=scope)
                if next_cursor in cursors or len(models) == previous_count:
                    raise DiscoveryError("incomplete")
                cursors.add(next_cursor)
                cursor = next_cursor
    except DiscoveryError as exc:
        error = str(exc)
    except (httpx.TimeoutException, TimeoutError):
        error = "timeout"
    except httpx.HTTPError:
        error = "transient"
    status = "partial" if models or error == "empty_result" else "failed"
    return DiscoveryResult(status, tuple(models.values()), error, pages, scope)
