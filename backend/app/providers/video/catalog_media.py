"""Bounded video retrieval and atomic writes for keyed generation adapters."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import BinaryIO, Iterator
from urllib.parse import urljoin

import httpx

from app.providers.image.catalog_media import CatalogImageError, validate_public_https_url
from app.services.ai_routing import RoutePending

MAX_VIDEO_BYTES = 100 * 1024 * 1024
_VIDEO_SAMPLE_ENTRIES = frozenset({b"avc1", b"avc3", b"hvc1", b"hev1", b"av01", b"vp09", b"mp4v"})


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


def _boxes(file: BinaryIO, start: int, end: int) -> Iterator[tuple[bytes, int, int]]:
    """Walk bounded ISO-BMFF boxes; never trust a size beyond the enclosing box."""
    position = start
    count = 0
    while position < end:
        count += 1
        if count > 10_000 or end - position < 8:
            raise VideoBoundaryError("invalid_output")
        file.seek(position)
        header = file.read(8)
        size = int.from_bytes(header[:4], "big")
        kind = header[4:8]
        header_size = 8
        if size == 1:
            if end - position < 16:
                raise VideoBoundaryError("invalid_output")
            size = int.from_bytes(file.read(8), "big")
            header_size = 16
        elif size == 0:
            size = end - position
        if size < header_size or size > end - position:
            raise VideoBoundaryError("invalid_output")
        box_end = position + size
        yield kind, position + header_size, box_end
        position = box_end


def _video_track(file: BinaryIO, start: int, end: int) -> bool:
    for kind, mdia_start, mdia_end in _boxes(file, start, end):
        if kind != b"mdia":
            continue
        is_video = False
        sample_desc = False
        for child, child_start, child_end in _boxes(file, mdia_start, mdia_end):
            if child == b"hdlr":
                if child_end - child_start < 12:
                    raise VideoBoundaryError("invalid_output")
                file.seek(child_start + 8)
                is_video = file.read(4) == b"vide"
            elif child == b"minf":
                for subkind, sub_start, sub_end in _boxes(file, child_start, child_end):
                    if subkind != b"stbl":
                        continue
                    for leaf, leaf_start, leaf_end in _boxes(file, sub_start, sub_end):
                        if leaf != b"stsd":
                            continue
                        if leaf_end - leaf_start < 16:
                            raise VideoBoundaryError("invalid_output")
                        file.seek(leaf_start + 4)
                        entries = int.from_bytes(file.read(4), "big")
                        if not 1 <= entries <= 64:
                            raise VideoBoundaryError("invalid_output")
                        descriptions = list(_boxes(file, leaf_start + 8, leaf_end))
                        if len(descriptions) != entries:
                            raise VideoBoundaryError("invalid_output")
                        sample_desc = any(entry in _VIDEO_SAMPLE_ENTRIES and stop - begin >= 78
                                          for entry, begin, stop in descriptions)
        if is_video and sample_desc:
            return True
    return False


def validate_mp4_file(path: Path, size: int) -> None:
    """Check container boundaries and a video sample description, not codec decode."""
    if size < 32 or size > MAX_VIDEO_BYTES:
        raise VideoBoundaryError("invalid_output")
    try:
        with path.open("rb") as file:
            top = list(_boxes(file, 0, size))
            if not top or top[0][0] != b"ftyp" or top[0][2] - top[0][1] < 8:
                raise VideoBoundaryError("invalid_output")
            if not any(kind == b"mdat" and stop > begin for kind, begin, stop in top):
                raise VideoBoundaryError("invalid_output")
            for kind, begin, stop in top:
                if kind == b"moov":
                    for child, child_begin, child_stop in _boxes(file, begin, stop):
                        if child == b"trak" and _video_track(file, child_begin, child_stop):
                            return
    except OSError:
        raise VideoBoundaryError("invalid_output") from None
    raise VideoBoundaryError("invalid_output")


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
                validate_mp4_file(temporary, count)
                os.replace(temporary, output_path)
                temporary = None
                return count
        raise VideoBoundaryError("invalid_output")
    except httpx.HTTPError:
        raise VideoBoundaryError("provider_unavailable") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
