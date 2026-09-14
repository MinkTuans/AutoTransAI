"""In-memory URL/file transfer progress (local-first ingest)."""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

_transfers: dict[str, dict[str, Any]] = {}


def create_transfer(kind: str, message: str) -> str:
    transfer_id = uuid.uuid4().hex[:12]
    _transfers[transfer_id] = {
        "id": transfer_id,
        "kind": kind,
        "status": "queued",
        "percent": 0.0,
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "speed": None,
        "eta": None,
        "message": message,
        "error": None,
        "asset": None,
        "updated_at": time.time(),
    }
    return transfer_id


def update_transfer(transfer_id: str, **fields: Any) -> Optional[dict[str, Any]]:
    rec = _transfers.get(transfer_id)
    if not rec:
        return None
    rec.update(fields)
    rec["updated_at"] = time.time()
    return rec


def apply_yt_dlp_progress(transfer_id: str, info: Any) -> None:
    rec = _transfers.get(transfer_id)
    if not rec:
        return
    if isinstance(info, dict):
        rec["status"] = "running"
        rec["percent"] = float(info.get("percent") or 0)
        rec["downloaded_bytes"] = int(info.get("downloaded_bytes") or 0)
        rec["total_bytes"] = int(info.get("total_bytes") or 0)
        rec["speed"] = info.get("speed")
        rec["eta"] = info.get("eta")
        rec["message"] = info.get("message") or rec.get("message")
    elif isinstance(info, (tuple, list)) and len(info) >= 2:
        downloaded, total = int(info[0]), int(info[1])
        rec["downloaded_bytes"] = downloaded
        rec["total_bytes"] = total
        rec["percent"] = round(100.0 * downloaded / total, 1) if total else 0.0
        rec["status"] = "running"
    rec["updated_at"] = time.time()


def get_transfer(transfer_id: str) -> Optional[dict[str, Any]]:
    return _transfers.get(transfer_id)
