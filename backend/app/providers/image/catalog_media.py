"""Bounded, unauthenticated retrieval of catalog-generated image bytes.

DNS checks are best-effort: a hostname can rebind between validation and the
HTTP connection. Callers must never forward provider authorization headers.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import ipaddress
import json
import socket
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from app.core.security_url import is_ip_private_or_blocked

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_JSON_BYTES = 14 * 1024 * 1024
_MIME = {"image/png", "image/jpeg", "image/webp"}


class CatalogImageError(Exception):
    """Safe local code and optional HTTP status, never upstream content."""

    def __init__(self, code: str, *, status_code: int | None = None):
        self.code = code
        self.status_code = status_code
        super().__init__(f"Image generation failed: {code}")


def _image_mime(content: bytes) -> str | None:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_image_bytes(content: bytes, declared_mime: str | None = None) -> bytes:
    if not 32 <= len(content) <= MAX_IMAGE_BYTES:
        raise CatalogImageError("invalid_output")
    detected = _image_mime(content)
    if detected is None or (declared_mime is not None and declared_mime != detected):
        raise CatalogImageError("invalid_output")
    return content


def decode_image_base64(value: str) -> bytes:
    if not isinstance(value, str) or len(value) > ((MAX_IMAGE_BYTES + 2) // 3) * 4 + 8:
        raise CatalogImageError("invalid_output")
    try:
        content = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        raise CatalogImageError("invalid_output") from None
    return validate_image_bytes(content)


def validated_output_path(value: object, data_root: Path) -> Path | None:
    """Legacy optional file output is limited to the application's data root."""
    if value is None:
        return None
    if not isinstance(value, (str, Path)):
        raise CatalogImageError("invalid_output_path")
    root = data_root.resolve()
    path = Path(value).resolve()
    if (path == root or not path.is_relative_to(root)
            or path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp")):
        raise CatalogImageError("invalid_output_path")
    return path


async def validate_public_https_url(url: str, *, expected_host: str | None = None) -> str:
    if not isinstance(url, str) or len(url) > 4096:
        raise CatalogImageError("invalid_output")
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise CatalogImageError("invalid_output") from None
    if (parsed.scheme != "https" or not host or parsed.username or parsed.password
            or port not in (None, 443) or parsed.fragment
            or (expected_host is not None and host != expected_host)):
        raise CatalogImageError("invalid_output")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if is_ip_private_or_blocked(host):
            raise CatalogImageError("invalid_output")
    try:
        addresses = await asyncio.wait_for(
            asyncio.to_thread(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM),
            5.0,
        )
    except (OSError, ValueError, asyncio.TimeoutError):
        raise CatalogImageError("invalid_output") from None
    if not addresses or any(is_ip_private_or_blocked(item[4][0]) for item in addresses):
        raise CatalogImageError("invalid_output")
    return url


async def download_image(client: httpx.AsyncClient, url: str) -> bytes:
    await validate_public_https_url(url)
    try:
        async with client.stream("GET", url, follow_redirects=False,
                                 headers={"Accept": "image/png, image/jpeg, image/webp"}) as response:
            if response.status_code != 200:
                raise CatalogImageError("download_failed", status_code=response.status_code)
            mime = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if mime not in _MIME:
                raise CatalogImageError("invalid_output")
            size = response.headers.get("content-length")
            if size is not None and (not size.isdigit() or int(size) > MAX_IMAGE_BYTES):
                raise CatalogImageError("invalid_output")
            chunks = []
            total = 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > MAX_IMAGE_BYTES:
                    raise CatalogImageError("invalid_output")
                chunks.append(chunk)
            return validate_image_bytes(b"".join(chunks), mime)
    except CatalogImageError:
        raise
    except (httpx.HTTPError, ValueError):
        raise CatalogImageError("provider_unavailable") from None


async def request_json(
    client: httpx.AsyncClient, method: str, url: str, *, headers: dict[str, str],
    payload: dict | None = None, accepted: tuple[int, ...] = (200,),
) -> dict:
    """Bound provider JSON bodies, including base64 image payloads, before parsing."""
    try:
        async with client.stream(method, url, headers=headers, json=payload,
                                 follow_redirects=False) as response:
            if response.status_code not in accepted:
                raise CatalogImageError("provider_unavailable", status_code=response.status_code)
            mime = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if mime != "application/json":
                raise CatalogImageError("invalid_output")
            size = response.headers.get("content-length")
            if size is not None and (not size.isdigit() or int(size) > MAX_JSON_BYTES):
                raise CatalogImageError("invalid_output")
            chunks = []
            total = 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > MAX_JSON_BYTES:
                    raise CatalogImageError("invalid_output")
                chunks.append(chunk)
        parsed = json.loads(b"".join(chunks))
        if not isinstance(parsed, dict):
            raise CatalogImageError("invalid_output")
        return parsed
    except CatalogImageError:
        raise
    except json.JSONDecodeError:
        raise CatalogImageError("invalid_output") from None
    except (httpx.HTTPError, ValueError, TypeError):
        raise CatalogImageError("provider_unavailable") from None
