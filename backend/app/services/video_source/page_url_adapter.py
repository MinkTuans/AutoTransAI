"""
Video Page URL Source Adapter.

Handles video web pages (YouTube, Vimeo, TikTok, Google Drive, Dropbox, etc.).
Uses yt-dlp or native stream extractors when legally allowed and available.
Fails cleanly with clear messages if access is restricted, DRM protected, or private.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from urllib.parse import parse_qs, urlparse

import httpx

from app.config import get_settings
from app.core import get_logger
from app.core.security import safe_subprocess_run_async
from app.core.security_url import validate_url_security, SSRFValidationError
from app.media.ffprobe import get_video_metadata_async
from app.services.video_source.base import BaseVideoSourceAdapter

logger = get_logger(__name__)
settings = get_settings()


def resolve_download_timeout(seconds: int | float | None) -> float | None:
    """0 or negative means no wall-clock limit; keep downloading until complete or stall."""
    if seconds is None:
        return None
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return value

PAGE_DOMAINS = {
    "youtube.com", "youtu.be", "www.youtube.com",
    "vimeo.com", "www.vimeo.com",
    "tiktok.com", "www.tiktok.com",
    "facebook.com", "fb.watch", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "drive.google.com",
    "dropbox.com", "www.dropbox.com",
    "bilibili.com", "www.bilibili.com", "m.bilibili.com",
    "b23.tv",
}

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _is_bilibili_domain(domain: str) -> bool:
    d = (domain or "").lower()
    return "bilibili" in d or d == "b23.tv" or d.endswith(".b23.tv")


_SIZE_UNITS = {
    "B": 1,
    "KB": 1000,
    "KIB": 1024,
    "MB": 1000 * 1000,
    "MIB": 1024 * 1024,
    "GB": 1000 * 1000 * 1000,
    "GIB": 1024 * 1024 * 1024,
}

_YT_DLP_PROGRESS_RE = re.compile(
    r"\[download\]\s+(?P<pct>[\d.]+)%\s+of\s+~?(?P<size>[\d.]+)\s*(?P<sunit>KiB|MiB|GiB|kB|MB|GB|B)"
    r"(?:\s+at\s+(?P<speed>[\d.]+)\s*(?P<spunit>KiB|MiB|GiB|kB|MB|GB|B)/s)?"
    r"(?:\s+ETA\s+(?P<eta>\S+))?",
    re.IGNORECASE,
)


def _unit_to_bytes(value: float, unit: str) -> int:
    return int(value * _SIZE_UNITS.get((unit or "B").upper(), 1))


def parse_yt_dlp_progress_line(line: str) -> dict[str, Any] | None:
    """Parse a yt-dlp `--newline` download progress line."""
    if not line:
        return None
    match = _YT_DLP_PROGRESS_RE.search(line)
    if not match:
        return None
    pct = float(match.group("pct"))
    total = _unit_to_bytes(float(match.group("size")), match.group("sunit"))
    speed = None
    if match.group("speed") and match.group("spunit"):
        speed = f"{match.group('speed')}{match.group('spunit')}/s"
    downloaded = int(total * pct / 100.0) if total else 0
    return {
        "percent": pct,
        "downloaded_bytes": downloaded,
        "total_bytes": total,
        "speed": speed,
        "eta": match.group("eta"),
        "message": line.strip(),
    }


def build_yt_dlp_download_cmd(yt_dlp_bin: str, url: str, output_path: Path) -> list[str]:
    """Build yt-dlp args. Bilibili needs browser headers + merged DASH, not mp4-only `best`."""
    parsed = urlparse(url.strip())
    domain = (parsed.netloc or "").split(":")[0]
    cmd = [
        yt_dlp_bin,
        "-f", "bv*+ba/b[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "-c",
        "--retries", "30",
        "--fragment-retries", "30",
        "--retry-sleep", "2",
        "-N", "1",
        "--socket-timeout", "30",
        "--newline",
        "-o", str(output_path),
        "--max-filesize", f"{settings.VIDEO_MAX_SIZE_MB}M",
    ]
    if _is_bilibili_domain(domain):
        cmd.extend([
            "--user-agent", BROWSER_UA,
            "--referer", "https://www.bilibili.com/",
            "--add-header", "Origin:https://www.bilibili.com",
            "--http-chunk-size", "1048576",
        ])
    cmd.append(url)
    return cmd


def _yt_dlp_error_snippet(err_text: str, limit: int = 220) -> str:
    """Prefer the actual failure line over the extractor preamble."""
    lines = [ln.strip() for ln in (err_text or "").splitlines() if ln.strip()]
    for ln in reversed(lines):
        low = ln.lower()
        if "bytes read" in low or "more expected" in low or ln.startswith("ERROR") or "giving up" in low:
            return ln[:limit]
    return (err_text or "empty stderr")[:limit]


def raise_yt_dlp_download_error(source_display: str, stderr: str | None, returncode: int | None = None) -> None:
    """Map yt-dlp stderr to a user-facing ValueError. Never raise an empty message."""
    err_text = (stderr or "").strip()
    err_lower = err_text.lower()
    snippet = _yt_dlp_error_snippet(err_text)
    if "412" in err_text or "precondition failed" in err_lower or "风控" in err_text:
        raise ValueError(
            f"Bilibili chặn tải video (HTTP 412 / anti-bot). "
            f"Cần cookie đăng nhập Bilibili hoặc thử lại từ mạng khác. "
            f"Chi tiết: {snippet}"
        )
    if "bytes read" in err_lower and "more expected" in err_lower:
        raise ValueError(
            f"Mạng cắt file giữa chừng, video tải không hoàn chỉnh. {snippet}"
        )
    if "login" in err_lower or "private" in err_lower or "drm" in err_lower or "confirm your age" in err_lower:
        raise ValueError("Nguồn này không thể được xử lý trực tiếp (yêu cầu đăng nhập, riêng tư hoặc chứa DRM).")
    code = f" (exit {returncode})" if returncode not in (None, 0) else ""
    raise ValueError(f"Không thể download video từ {source_display}{code}: {snippet}")


_BVID_RE = re.compile(r"(BV[0-9A-Za-z]+)")
_AVID_RE = re.compile(r"(?:/video/|/)?av(\d+)", re.IGNORECASE)


def parse_bilibili_video_ref(url: str) -> dict[str, Any] | None:
    """Extract BV id or AV/aid and 1-indexed part. Query `t` is a timestamp, not a page."""
    if not url or not isinstance(url, str):
        return None
    parsed = urlparse(url.strip())
    query = parse_qs(parsed.query)
    page = 1
    if "p" in query:
        try:
            page = max(1, int(query["p"][0]))
        except (TypeError, ValueError):
            page = 1

    bv = _BVID_RE.search(parsed.path) or _BVID_RE.search(url)
    if bv:
        return {"bvid": bv.group(1), "aid": None, "page": page}

    aid = None
    av = _AVID_RE.search(parsed.path) or _AVID_RE.search(url)
    if av:
        aid = int(av.group(1))
    elif "aid" in query:
        try:
            aid = int(query["aid"][0])
        except (TypeError, ValueError):
            aid = None
    if not aid:
        return None
    return {"bvid": None, "aid": aid, "page": page}


def bilibili_pagelist_api(ref: dict[str, Any]) -> str:
    if ref.get("bvid"):
        return f"https://api.bilibili.com/x/player/pagelist?bvid={ref['bvid']}"
    if ref.get("aid"):
        return f"https://api.bilibili.com/x/player/pagelist?aid={int(ref['aid'])}"
    raise ValueError("Không nhận diện được mã video Bilibili từ URL.")


def _bilibili_id_query(ref: dict[str, Any] | None = None, *, bvid: str | None = None, aid: int | None = None) -> str:
    if ref:
        bvid = bvid or ref.get("bvid")
        aid = aid if aid is not None else ref.get("aid")
    if bvid:
        return f"bvid={bvid}"
    if aid:
        return f"aid={int(aid)}"
    raise ValueError("Thiếu bvid/aid Bilibili.")


def metadata_from_bilibili_pagelist(
    pages: list[dict[str, Any]],
    page: int,
    bvid: str | None = None,
    aid: int | None = None,
) -> dict[str, Any]:
    """Map Bilibili pagelist JSON to check-url metadata. Duration is seconds."""
    if not pages:
        raise ValueError("Bilibili không trả về danh sách phần video.")
    entry = next((p for p in pages if int(p.get("page") or 0) == page), None)
    if entry is None:
        entry = pages[0]
        page = int(entry.get("page") or 1)
    duration = float(entry.get("duration") or 0.0)
    if duration <= 0:
        raise ValueError("Bilibili không trả về thời lượng video.")
    dim = entry.get("dimension") or {}
    slug = bvid or (f"av{aid}" if aid else "video")
    title = (entry.get("part") or "").strip() or f"Bilibili {slug}"
    cid = entry.get("cid")
    return {
        "source": "Bilibili",
        "domain": "www.bilibili.com",
        "title": title,
        "duration": round(duration, 2),
        "width": int(dim.get("width") or 0),
        "height": int(dim.get("height") or 0),
        "format": "mp4",
        "file_size": None,
        "audio_available": True,
        "url": f"https://www.bilibili.com/video/{slug}?p={page}",
        "mime_type": "video/mp4",
        "bvid": bvid,
        "aid": aid,
        "page": page,
        "page_count": len(pages),
        "cid": cid,
    }


def extract_bilibili_playurl(payload: dict[str, Any]) -> dict[str, Any]:
    """Pick a single MP4 durl from playurl JSON (fnval=1)."""
    data = payload.get("data") or {}
    durl = data.get("durl") or []
    if not durl or not durl[0].get("url"):
        raise ValueError("Bilibili playurl không trả về file MP4.")
    item = durl[0]
    return {
        "url": item["url"],
        "size": int(item.get("size") or 0),
        "length_ms": int(item.get("length") or 0),
        "quality": data.get("quality"),
        "format": data.get("format") or "mp4",
    }


def _bili_http_headers() -> dict[str, str]:
    return {
        "User-Agent": BROWSER_UA,
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
    }


async def fetch_bilibili_mp4_playurl(
    cid: int,
    bvid: str | None = None,
    aid: int | None = None,
) -> dict[str, Any]:
    timeout = httpx.Timeout(20.0, connect=8.0)
    id_q = _bilibili_id_query(bvid=bvid, aid=aid)
    async with httpx.AsyncClient(timeout=timeout, headers=_bili_http_headers()) as client:
        last_err = "unknown"
        for qn in (64, 32, 16):
            api = (
                f"https://api.bilibili.com/x/player/playurl"
                f"?{id_q}&cid={cid}&qn={qn}&fnval=1&fnver=0"
            )
            res = await client.get(api)
            if res.status_code >= 400:
                last_err = f"HTTP {res.status_code}"
                continue
            payload = res.json()
            if payload.get("code") != 0:
                last_err = str(payload.get("message") or payload.get("code"))
                continue
            try:
                return extract_bilibili_playurl(payload)
            except ValueError as e:
                last_err = str(e)
                continue
    raise ValueError(f"Không lấy được playurl Bilibili: {last_err}")


async def download_http_with_resume(
    url: str,
    output_path: Path,
    *,
    headers: dict[str, str],
    expected_size: int = 0,
    timeout: int = 300,
    progress_callback: Optional[Callable[..., None]] = None,
) -> int:
    """Download a direct HTTP file with Range resume and progress callbacks."""
    part_path = output_path.with_suffix(output_path.suffix + ".part")
    downloaded = part_path.stat().st_size if part_path.exists() else 0
    total = expected_size
    limit = resolve_download_timeout(timeout)
    deadline = (asyncio.get_event_loop().time() + limit) if limit else None
    retries = 0
    max_retries = 30

    def _emit():
        if not progress_callback:
            return
        pct = round(100.0 * downloaded / total, 1) if total else 0.0
        info = {
            "percent": min(pct, 99.9),
            "downloaded_bytes": downloaded,
            "total_bytes": total,
            "speed": None,
            "eta": None,
            "message": f"Đang tải xuống {pct:.0f}%",
        }
        try:
            progress_callback(info)
        except TypeError:
            progress_callback(downloaded, total)
        except Exception:
            pass

    # No read timeout: a slow stream still making progress must not be killed.
    client_timeout = httpx.Timeout(None, connect=30.0)
    async with httpx.AsyncClient(timeout=client_timeout, follow_redirects=True, headers=headers) as client:
        while retries < max_retries:
            if deadline is not None and asyncio.get_event_loop().time() > deadline:
                raise ValueError("Hết thời gian tải video Bilibili.")
            req_headers = dict(headers)
            write_mode = "wb"
            if downloaded > 0:
                req_headers["Range"] = f"bytes={downloaded}-"
                write_mode = "ab"
            try:
                async with client.stream("GET", url, headers=req_headers) as res:
                    if res.status_code not in (200, 206):
                        raise ValueError(f"CDN Bilibili HTTP {res.status_code}")
                    if res.status_code == 200:
                        downloaded = 0
                        write_mode = "wb"
                    cr = res.headers.get("Content-Range") or ""
                    if "/" in cr:
                        try:
                            total = int(cr.rsplit("/", 1)[-1])
                        except ValueError:
                            pass
                    elif not total:
                        try:
                            cl = int(res.headers.get("Content-Length") or 0)
                            total = downloaded + cl if res.status_code == 206 else cl
                        except ValueError:
                            pass
                    with open(part_path, write_mode) as fh:
                        async for chunk in res.aiter_bytes(64 * 1024):
                            if not chunk:
                                continue
                            fh.write(chunk)
                            downloaded += len(chunk)
                            _emit()
                break
            except (httpx.HTTPError, ValueError) as exc:
                retries += 1
                logger.warning("Bilibili HTTP download retry", attempt=retries, error=str(exc))
                await asyncio.sleep(min(2 * retries, 8))
        else:
            raise ValueError(
                f"Mạng cắt file giữa chừng, video tải không hoàn chỉnh. "
                f"{downloaded} bytes read, {max(total - downloaded, 0)} more expected."
            )

    if downloaded < 100_000:
        part_path.unlink(missing_ok=True)
        raise ValueError("File Bilibili tải về quá nhỏ, có thể bị CDN chặn.")
    if total and downloaded < total * 0.95:
        raise ValueError(
            f"Mạng cắt file giữa chừng, video tải không hoàn chỉnh. "
            f"{downloaded} bytes read, {total - downloaded} more expected."
        )
    part_path.replace(output_path)
    if progress_callback:
        try:
            progress_callback({
                "percent": 100.0,
                "downloaded_bytes": downloaded,
                "total_bytes": total or downloaded,
                "speed": None,
                "eta": "00:00",
                "message": "Tải xong",
            })
        except Exception:
            pass
    return downloaded


async def download_bilibili_native(
    url: str,
    output_path: Path,
    progress_callback: Optional[Callable[..., None]] = None,
) -> dict[str, Any]:
    """Download one Bilibili part via official playurl MP4 + HTTP Range."""
    meta = await fetch_bilibili_page_metadata(url)
    cid = meta.get("cid")
    bvid = meta.get("bvid")
    aid = meta.get("aid")
    if not cid or not (bvid or aid):
        raise ValueError("Thiếu cid/bvid/aid Bilibili để lấy playurl.")
    play = await fetch_bilibili_mp4_playurl(int(cid), bvid=bvid, aid=aid)
    size = await download_http_with_resume(
        play["url"],
        output_path,
        headers=_bili_http_headers(),
        expected_size=int(play.get("size") or 0),
        timeout=0,
        progress_callback=progress_callback,
    )
    probe = await get_video_metadata_async(output_path)
    max_duration_sec = settings.VIDEO_MAX_DURATION_MINUTES * 60
    if probe.get("duration", 0.0) > max_duration_sec:
        output_path.unlink(missing_ok=True)
        raise ValueError(
            f"Thời lượng video ({probe['duration']/60:.1f} phút) vượt quá giới hạn tối đa "
            f"({settings.VIDEO_MAX_DURATION_MINUTES} phút)."
        )
    return {
        "source": "Bilibili",
        "domain": "www.bilibili.com",
        "title": meta.get("title") or output_path.stem,
        "duration": probe["duration"],
        "width": probe["width"],
        "height": probe["height"],
        "format": probe["format"],
        "file_size": size,
        "audio_available": probe["has_audio"],
        "local_path": str(output_path),
        "mime_type": "video/mp4",
    }


async def fetch_bilibili_page_metadata(url: str) -> dict[str, Any]:
    """Fetch title/duration from Bilibili pagelist API (works when view API is 412)."""
    ref = parse_bilibili_video_ref(url)
    if not ref:
        raise ValueError("Không nhận diện được mã video Bilibili từ URL.")
    api = bilibili_pagelist_api(ref)
    timeout = httpx.Timeout(15.0, connect=8.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.get(
            api,
            headers={
                "User-Agent": BROWSER_UA,
                "Referer": "https://www.bilibili.com/",
            },
        )
        if res.status_code >= 400:
            raise ValueError(f"Không lấy được metadata Bilibili (HTTP {res.status_code}).")
        payload = res.json()
    if payload.get("code") != 0 or not payload.get("data"):
        raise ValueError(
            f"Bilibili pagelist lỗi: {payload.get('message') or payload.get('code')}"
        )
    return metadata_from_bilibili_pagelist(
        payload["data"], ref["page"], bvid=ref.get("bvid"), aid=ref.get("aid")
    )


async def run_yt_dlp_with_progress_async(
    cmd: list[str],
    timeout: int,
    progress_callback: Optional[Callable[..., None]] = None,
) -> tuple[int, str]:
    """Run yt-dlp via Popen (Windows uvicorn SelectorEventLoop cannot create_subprocess_exec)."""
    try:
        popen_kwargs: dict[str, Any] = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "bufsize": 1,
            "encoding": "utf-8",
            "errors": "replace",
        }
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        process = subprocess.Popen(cmd, **popen_kwargs)
    except NotImplementedError as e:
        raise ValueError(
            "Không chạy được yt-dlp trên event loop hiện tại (Windows). "
            "Dùng subprocess.Popen thay vì asyncio subprocess."
        ) from e

    logs: list[str] = []
    loop = asyncio.get_running_loop()

    def _emit(parsed: dict[str, Any]) -> None:
        if not progress_callback:
            return
        try:
            progress_callback(parsed)
        except TypeError:
            progress_callback(parsed["downloaded_bytes"], parsed["total_bytes"])
        except Exception:
            pass

    def _read_worker() -> int:
        if process.stdout:
            for line in process.stdout:
                text = (line or "").rstrip()
                if text:
                    logs.append(text)
                parsed = parse_yt_dlp_progress_line(text)
                if parsed:
                    loop.call_soon_threadsafe(_emit, parsed)
        return process.wait()

    limit = resolve_download_timeout(timeout)
    try:
        if limit is None:
            returncode = await asyncio.to_thread(_read_worker)
        else:
            returncode = await asyncio.wait_for(asyncio.to_thread(_read_worker), timeout=limit)
    except asyncio.TimeoutError:
        process.kill()
        await asyncio.to_thread(process.wait)
        raise ValueError("Hết thời gian tải video.")
    return int(returncode), "\n".join(logs)


def _get_yt_dlp_executable() -> str | None:
    """Find yt-dlp executable in system PATH or python environment."""
    found = shutil.which("yt-dlp")
    if found:
        return found
    return None


class PageURLAdapter(BaseVideoSourceAdapter):
    """Adapter for video web page URLs."""

    @property
    def source_name(self) -> str:
        return "Video Page"

    def can_handle(self, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urlparse(url.strip())
            if parsed.scheme.lower() not in ("http", "https"):
                return False
            domain = parsed.netloc.lower().split(":")[0]
            # Match known domains or fallback web URLs
            if any(domain.endswith(d) for d in PAGE_DOMAINS):
                return True
            # Also handle any generic page URL (not a direct file extension)
            path = parsed.path.lower()
            return not path.endswith((".mp4", ".webm", ".mov", ".mkv", ".avi", ".flv"))
        except Exception:
            return False

    def _get_domain_display(self, domain: str) -> str:
        domain_lower = domain.lower()
        if "youtube" in domain_lower or "youtu.be" in domain_lower:
            return "YouTube"
        if "vimeo" in domain_lower:
            return "Vimeo"
        if "tiktok" in domain_lower:
            return "TikTok"
        if "facebook" in domain_lower or "fb.watch" in domain_lower:
            return "Facebook"
        if "instagram" in domain_lower:
            return "Instagram"
        if "drive.google" in domain_lower:
            return "Google Drive"
        if "dropbox" in domain_lower:
            return "Dropbox"
        if _is_bilibili_domain(domain_lower):
            return "Bilibili"
        return domain.capitalize()

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata for video page URL using yt-dlp or head check."""
        safe_url = validate_url_security(url)
        parsed = urlparse(safe_url)
        domain = parsed.netloc.split(":")[0]
        source_display = self._get_domain_display(domain)

        if _is_bilibili_domain(domain):
            try:
                return await fetch_bilibili_page_metadata(safe_url)
            except Exception as bili_err:
                logger.warning("Bilibili pagelist metadata failed, falling back to yt-dlp", error=str(bili_err))

        yt_dlp_bin = _get_yt_dlp_executable()
        if not yt_dlp_bin:
            if _is_bilibili_domain(domain):
                raise ValueError(
                    "Không lấy được thời lượng Bilibili. Kiểm tra mạng hoặc cài yt-dlp."
                )
            # Fallback metadata when yt-dlp binary is not installed
            return {
                "source": source_display,
                "domain": domain,
                "title": f"Video từ {source_display}",
                "duration": 0.0,
                "width": 1920,
                "height": 1080,
                "format": "mp4",
                "file_size": None,
                "audio_available": True,
                "url": safe_url,
                "mime_type": "video/mp4",
            }

        cmd = [
            yt_dlp_bin,
            "--dump-single-json",
            "--no-playlist",
            "--skip-download",
        ]
        if _is_bilibili_domain(domain):
            cmd.extend([
                "--user-agent", BROWSER_UA,
                "--referer", "https://www.bilibili.com/",
            ])
        cmd.append(safe_url)

        try:
            res = await safe_subprocess_run_async(cmd, timeout=20, check=False)
            if res.returncode != 0:
                err_text = (res.stderr or "").lower()
                if "412" in err_text or "precondition failed" in err_text:
                    raise ValueError(
                        f"Bilibili chặn truy cập metadata (HTTP 412). Cần cookie hoặc thử lại từ mạng khác."
                    )
                if "login" in err_text or "private" in err_text or "drm" in err_text or "confirm your age" in err_text:
                    raise ValueError("Nguồn này không thể được xử lý trực tiếp (yêu cầu đăng nhập, riêng tư hoặc chứa DRM).")
                raise ValueError(f"Không thể truy cập nguồn video ({source_display}). Video có thể không tồn tại.")

            data = json.loads(res.stdout)
            title = data.get("title", "Video từ " + source_display)
            duration = float(data.get("duration") or 0.0)
            width = int(data.get("width") or 0)
            height = int(data.get("height") or 0)
            ext = data.get("ext", "mp4")

            return {
                "source": source_display,
                "domain": domain,
                "title": title,
                "duration": round(duration, 2),
                "width": width,
                "height": height,
                "format": ext,
                "file_size": data.get("filesize") or data.get("filesize_approx"),
                "audio_available": True,
                "url": safe_url,
                "mime_type": f"video/{ext}",
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.warning("yt-dlp metadata extraction failed", url=safe_url, error=str(e))
            if _is_bilibili_domain(domain):
                raise ValueError(f"Không lấy được metadata Bilibili: {e}") from e
            return {
                "source": source_display,
                "domain": domain,
                "title": f"Video từ {source_display}",
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "format": "mp4",
                "file_size": None,
                "audio_available": True,
                "url": safe_url,
                "mime_type": "video/mp4",
            }

    async def download(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Download video page content using yt-dlp or direct stream resolution."""
        safe_url = validate_url_security(url)
        parsed = urlparse(safe_url)
        domain = parsed.netloc.split(":")[0]
        source_display = self._get_domain_display(domain)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        native_err: Exception | None = None
        if _is_bilibili_domain(domain):
            try:
                return await download_bilibili_native(safe_url, output_path, progress_callback)
            except Exception as exc:
                native_err = exc
                logger.warning("Bilibili native playurl download failed, falling back to yt-dlp", error=str(exc))

        yt_dlp_bin = _get_yt_dlp_executable()

        if not yt_dlp_bin:
            if native_err:
                raise native_err
            raise ValueError(
                f"Nguồn video '{source_display}' yêu cầu bộ tải media. Vui lòng cài đặt yt-dlp hoặc sử dụng Direct MP4 URL."
            )

        cmd = build_yt_dlp_download_cmd(yt_dlp_bin, safe_url, output_path)

        returncode, combined_log = await run_yt_dlp_with_progress_async(
            cmd,
            timeout=0,
            progress_callback=progress_callback,
        )
        file_ok = output_path.exists() and output_path.stat().st_size >= 100_000
        if returncode != 0 or not file_ok:
            if output_path.exists() and output_path.stat().st_size < 100_000:
                output_path.unlink(missing_ok=True)
            raise_yt_dlp_download_error(source_display, combined_log, returncode)

        # Probe metadata of downloaded file
        meta = await get_video_metadata_async(output_path)
        max_duration_sec = settings.VIDEO_MAX_DURATION_MINUTES * 60
        if meta.get("duration", 0.0) > max_duration_sec:
            output_path.unlink(missing_ok=True)
            raise ValueError(
                f"Thời lượng video ({meta['duration']/60:.1f} phút) vượt quá giới hạn tối đa ({settings.VIDEO_MAX_DURATION_MINUTES} phút)."
            )

        return {
            "source": source_display,
            "domain": domain,
            "title": output_path.stem,
            "duration": meta["duration"],
            "width": meta["width"],
            "height": meta["height"],
            "format": meta["format"],
            "file_size": output_path.stat().st_size,
            "audio_available": meta["has_audio"],
            "local_path": str(output_path),
            "mime_type": "video/mp4",
        }
