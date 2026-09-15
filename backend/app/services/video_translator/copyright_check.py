"""Copyright risk check for ingested videos — metadata + audio fingerprint, no LLM."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any, Callable, Optional

from app.core import get_logger

logger = get_logger(__name__)

LEVEL_RANK = {"green": 0, "yellow": 1, "red": 2, "skipped": -1}
FILM_MIN_DURATION_SEC = 20 * 60
ACOUSTID_MIN_SCORE = 0.8
FPCALC_SECONDS = 60

_FILM_TITLE_RE = re.compile(
    r"(电影完整版|完整版电影|电视剧|全集|高清抢先|院线|映画|ドラマ|"
    r"full\s*movie|full\s*episode|complete\s*series)",
    re.IGNORECASE,
)
_TV_PARTITION_RE = re.compile(r"(电影|电视剧|影视|documentary|film|movie|tv\s*series)", re.IGNORECASE)


def _as_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes", "on")
    return False


def score_metadata(meta: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Score platform metadata. Other-uploader/repost is yellow; film/licensed is red."""
    data = meta or {}
    reasons: list[str] = []
    level = "green"

    title = str(data.get("title") or "")
    duration = float(data.get("duration") or 0.0)
    tname = str(data.get("tname") or data.get("category") or "")
    license_id = str(data.get("license") or "")

    if _as_bool(data.get("licensedContent")) and license_id.lower() != "creativecommon":
        level = "red"
        reasons.append("YouTube đánh dấu licensedContent (nội dung có bản quyền thương mại).")

    copyright_val = data.get("copyright")
    try:
        copyright_n = int(copyright_val) if copyright_val is not None and copyright_val != "" else None
    except (TypeError, ValueError):
        copyright_n = None

    filmish = bool(_FILM_TITLE_RE.search(title) or _TV_PARTITION_RE.search(tname))
    long_form = duration >= FILM_MIN_DURATION_SEC

    if filmish and long_form:
        level = "red"
        reasons.append(
            f"Title/phân khu giống phim hoặc TV full ({duration / 60:.0f} phút): {title[:80]}"
        )
    elif copyright_n == 2 and filmish:
        level = "red"
        reasons.append("Bilibili chuyển tải (copyright=2) trong phân khu phim/TV.")
    elif copyright_n == 2:
        if LEVEL_RANK[level] < LEVEL_RANK["yellow"]:
            level = "yellow"
        reasons.append("Bilibili đánh dấu 转载/chuyển tải (copyright=2) — video của người khác.")

    return {"level": level, "reasons": reasons, "enabled": True}


def parse_acoustid_payload(payload: Any) -> list[dict[str, Any]]:
    """Keep high-confidence AcoustID recordings only."""
    if not isinstance(payload, dict) or payload.get("status") != "ok":
        return []
    hits: list[dict[str, Any]] = []
    for result in payload.get("results") or []:
        try:
            score = float(result.get("score") or 0.0)
        except (TypeError, ValueError):
            continue
        if score < ACOUSTID_MIN_SCORE:
            continue
        for rec in result.get("recordings") or []:
            title = str(rec.get("title") or "").strip()
            if not title:
                continue
            artists = rec.get("artists") or []
            artist = ""
            if artists and isinstance(artists[0], dict):
                artist = str(artists[0].get("name") or "").strip()
            hits.append({"title": title, "artist": artist, "score": score})
            break
    return hits


def merge_copyright_report(
    meta_report: dict[str, Any],
    acoustid_hits: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    level = meta_report.get("level") or "green"
    reasons = list(meta_report.get("reasons") or [])
    for hit in acoustid_hits or []:
        level = "red"
        who = f"{hit.get('artist')} — {hit.get('title')}".strip(" —")
        reasons.append(f"Chromaprint/AcoustID khớp nhạc: {who} (score {hit.get('score'):.2f}).")
    return {
        "level": level,
        "reasons": reasons,
        "enabled": True,
        "acoustid_hits": list(acoustid_hits or []),
    }


def _run_fpcalc(audio_path: str, seconds: int = FPCALC_SECONDS) -> tuple[Optional[str], Optional[int]]:
    binary = shutil.which("fpcalc")
    if not binary:
        return None, None
    try:
        proc = subprocess.run(
            [binary, "-json", "-length", str(seconds), audio_path],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("fpcalc failed", error=str(exc))
        return None, None
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return None, None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, None
    fingerprint = data.get("fingerprint")
    duration = data.get("duration")
    try:
        dur_i = int(float(duration)) if duration is not None else None
    except (TypeError, ValueError):
        dur_i = None
    if not fingerprint:
        return None, None
    return str(fingerprint), dur_i


async def _lookup_acoustid(
    fingerprint: str,
    duration: int,
    api_key: str,
    http_get: Optional[Callable[..., Any]] = None,
) -> list[dict[str, Any]]:
    params = {
        "client": api_key,
        "meta": "recordings+releasegroups",
        "duration": str(duration),
        "fingerprint": fingerprint,
    }
    url = "https://api.acoustid.org/v2/lookup"
    try:
        if http_get is not None:
            payload = await http_get(url, params)
        else:
            import httpx

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url, params=params)
                payload = res.json() if res.status_code == 200 else {}
    except Exception as exc:
        logger.warning("AcoustID lookup failed", error=str(exc))
        return []
    return parse_acoustid_payload(payload)


def format_copyright_notice(report: dict[str, Any]) -> str:
    level = report.get("level") or "green"
    reasons = report.get("reasons") or []
    if level == "skipped":
        return "Bỏ qua kiểm tra bản quyền."
    if level == "green":
        return "Kiểm tra bản quyền: không khớp nguồn đã biết (không chứng minh sạch bản quyền)."
    head = "Rủi ro bản quyền CAO" if level == "red" else "Cảnh báo bản quyền"
    body = " ".join(reasons[:3]) if reasons else ""
    return f"{head}: {body}".strip()


def metadata_from_asset(asset: Any, extra: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    data = dict(extra or {})
    if asset is None:
        return data
    data.setdefault("title", getattr(asset, "title", None))
    data.setdefault("duration", getattr(asset, "duration", None))
    data.setdefault("domain", getattr(asset, "source_domain", None))
    data.setdefault("url", getattr(asset, "source_url", None))
    data.setdefault("source_url", getattr(asset, "source_url", None))
    return data


async def enrich_bilibili_view(meta: dict[str, Any]) -> dict[str, Any]:
    """Best-effort Bilibili view API for copyright/tname. Failures leave meta unchanged."""
    url = str(meta.get("url") or meta.get("source_url") or "")
    domain = str(meta.get("domain") or "")
    if "bilibili" not in domain.lower() and "bilibili.com" not in url.lower() and "b23.tv" not in url.lower():
        return meta
    try:
        from app.services.video_source.page_url_adapter import parse_bilibili_video_ref, BROWSER_UA

        ref = parse_bilibili_video_ref(url)
        if not ref:
            return meta
        import httpx

        if ref.get("bvid"):
            api = f"https://api.bilibili.com/x/web-interface/view?bvid={ref['bvid']}"
        else:
            api = f"https://api.bilibili.com/x/web-interface/view?aid={int(ref['aid'])}"
        async with httpx.AsyncClient(timeout=12.0) as client:
            res = await client.get(
                api,
                headers={"User-Agent": BROWSER_UA, "Referer": "https://www.bilibili.com/"},
            )
        if res.status_code >= 400:
            return meta
        payload = res.json()
        view = payload.get("data") or {}
        if payload.get("code") != 0 or not view:
            return meta
        if view.get("copyright") is not None:
            meta["copyright"] = view.get("copyright")
        if view.get("tname"):
            meta["tname"] = view.get("tname")
        if view.get("title") and not meta.get("title"):
            meta["title"] = view.get("title")
    except Exception as exc:
        logger.info("Bilibili view enrich skipped", error=str(exc))
    return meta


async def run_copyright_check(
    metadata: Optional[dict[str, Any]] = None,
    audio_path: Optional[str] = None,
    enabled: bool = True,
    acoustid_api_key: Optional[str] = None,
    http_get: Optional[Callable[..., Any]] = None,
) -> dict[str, Any]:
    if not enabled:
        return {
            "level": "skipped",
            "reasons": [],
            "enabled": False,
            "acoustid_hits": [],
            "notice": format_copyright_notice({"level": "skipped"}),
        }

    meta = dict(metadata or {})
    meta = await enrich_bilibili_view(meta)
    meta_report = score_metadata(meta)
    hits: list[dict[str, Any]] = []
    key = (acoustid_api_key or "").strip()
    if audio_path and key:
        fingerprint, duration = _run_fpcalc(audio_path)
        if fingerprint and duration:
            hits = await _lookup_acoustid(fingerprint, duration, key, http_get=http_get)
        elif not shutil.which("fpcalc"):
            logger.info("fpcalc not on PATH; skipping AcoustID")

    report = merge_copyright_report(meta_report, hits)
    report["notice"] = format_copyright_notice(report)
    report["hold"] = report["level"] == "red"
    return report
