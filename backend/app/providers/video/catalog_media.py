"""Bounded video retrieval and atomic writes for keyed generation adapters."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import httpx

from app.providers.image.catalog_media import CatalogImageError, validate_public_https_url
from app.services.ai_routing import RoutePending

MAX_VIDEO_BYTES = 100 * 1024 * 1024


class VideoBoundaryError(Exception):
    """Safe local error; provider body and exception text are never retained."""

    def __init__(self, code: str, status_code: int | None = None, *, definitive: bool = False):
        self.code = code
        self.status_code = status_code
        self.definitive = definitive
        super().__init__(f"Video generation failed: {code}")


class VideoRoutePending(RoutePending):
    """Accepted or uncertain task; outcome is a local classification only."""

    def __init__(self, outcome: str = "pending"):
        self.outcome = outcome
        super().__init__("Video generation pending")


def validated_video_path(path: Path, data_root: Path) -> Path:
    if not isinstance(path, Path):
        raise VideoBoundaryError("invalid_output_path")
    root = data_root.resolve()
    result = path.resolve()
    if result == root or not result.is_relative_to(root) or result.suffix.lower() != ".mp4":
        raise VideoBoundaryError("invalid_output_path")
    return result


async def provider_url(value: object, *, host: str, path: str) -> str:
    if not isinstance(value, str):
        raise VideoBoundaryError("invalid_output")
    try:
        await validate_public_https_url(value, expected_host=host)
        parsed = httpx.URL(value)
        if parsed.path != path or parsed.query:
            raise VideoBoundaryError("invalid_output")
    except CatalogImageError:
        raise VideoBoundaryError("invalid_output") from None
    return value


async def request_json(client: httpx.AsyncClient, method: str, url: str, *, headers: dict,
                       payload: dict | None = None, accepted: tuple[int, ...] = (200,)) -> dict:
    try:
        async with client.stream(method, url, headers=headers, json=payload,
                                 follow_redirects=False) as response:
            if response.status_code not in accepted:
                raise VideoBoundaryError("provider_unavailable", response.status_code)
            if response.headers.get("content-type", "").split(";", 1)[0].lower() != "application/json":
                raise VideoBoundaryError("invalid_output")
            size = response.headers.get("content-length")
            if size is not None and (not size.isdigit() or int(size) > 1024 * 1024):
                raise VideoBoundaryError("invalid_output")
            content = bytearray()
            async for chunk in response.aiter_bytes():
                content.extend(chunk)
                if len(content) > 1024 * 1024:
                    raise VideoBoundaryError("invalid_output")
        import json
        result = json.loads(content)
        if not isinstance(result, dict):
            raise VideoBoundaryError("invalid_output")
        return result
    except VideoBoundaryError:
        raise
    except (ValueError, TypeError):
        raise VideoBoundaryError("invalid_output") from None
    except httpx.HTTPError:
        raise VideoBoundaryError("provider_unavailable") from None


async def download_video(client: httpx.AsyncClient, url: str, output_path: Path) -> int:
    """Public HTTPS only, no provider headers; unique temporary output is always removed."""
    temporary: Path | None = None
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=f".{output_path.name}.", suffix=".part",
                                         dir=output_path.parent, delete=False) as handle:
            temporary = Path(handle.name)
        current = url
        for hop in range(4):
            try:
                await validate_public_https_url(current)
            except CatalogImageError:
                raise VideoBoundaryError("invalid_output") from None
            async with client.stream("GET", current, headers={"Accept": "video/mp4"},
                                     follow_redirects=False) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if hop == 3 or not location:
                        raise VideoBoundaryError("invalid_output")
                    current = urljoin(current, location)
                    continue
                if response.status_code != 200:
                    raise VideoBoundaryError("download_failed", response.status_code)
                if response.headers.get("content-type", "").split(";", 1)[0].lower() != "video/mp4":
                    raise VideoBoundaryError("invalid_output")
                length = response.headers.get("content-length")
                if length is not None and (not length.isdigit() or int(length) > MAX_VIDEO_BYTES):
                    raise VideoBoundaryError("invalid_output")
                count = 0
                first = bytearray()
                with temporary.open("wb") as file:
                    async for chunk in response.aiter_bytes():
                        count += len(chunk)
                        if count > MAX_VIDEO_BYTES:
                            raise VideoBoundaryError("invalid_output")
                        if len(first) < 12:
                            first.extend(chunk[:12 - len(first)])
                        file.write(chunk)
                if count < 12 or first[4:8] != b"ftyp":
                    raise VideoBoundaryError("invalid_output")
                os.replace(temporary, output_path)
                temporary = None
                return count
        raise VideoBoundaryError("invalid_output")
    except httpx.HTTPError:
        raise VideoBoundaryError("provider_unavailable") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
