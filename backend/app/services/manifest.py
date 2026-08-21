from __future__ import annotations

"""
Manifest manager — reads/writes manifest.json for project recovery.

The manifest is the single source of truth for project state recovery.
It is updated after every significant state change (segment completion, etc.).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.core import get_logger
from app.services.file_manager import get_manifest_path

logger = get_logger(__name__)


def create_manifest(project_id: str, project_data: dict) -> None:
    """Create a new manifest.json for a project."""
    manifest = {
        "version": "1.0",
        "project_id": project_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **project_data,
    }
    _write_manifest(project_id, manifest)


def update_manifest(project_id: str, updates: dict) -> None:
    """Update specific fields in the manifest."""
    manifest = read_manifest(project_id)
    if manifest is None:
        manifest = {"version": "1.0", "project_id": project_id}

    manifest.update(updates)
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_manifest(project_id, manifest)


def update_segment_in_manifest(
    project_id: str,
    segment_number: int,
    segment_data: dict,
) -> None:
    """Update a specific segment's data in the manifest."""
    manifest = read_manifest(project_id) or {
        "version": "1.0",
        "project_id": project_id,
        "segments": [],
    }

    segments = manifest.get("segments", [])

    # Find and update or append
    found = False
    for seg in segments:
        if seg.get("number") == segment_number:
            seg.update(segment_data)
            found = True
            break

    if not found:
        segment_data["number"] = segment_number
        segments.append(segment_data)

    manifest["segments"] = segments
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_manifest(project_id, manifest)


def read_manifest(project_id: str) -> dict | None:
    """Read the manifest for a project. Returns None if not found."""
    path = get_manifest_path(project_id)
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(
            "Failed to read manifest",
            project_id=project_id,
            error=str(e),
        )
        return None


def _write_manifest(project_id: str, manifest: dict) -> None:
    """Write manifest to disk atomically (write-then-rename)."""
    path = get_manifest_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first, then rename for atomicity
    tmp_path = path.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)
        logger.debug("Manifest updated", project_id=project_id)
    except OSError as e:
        logger.error(
            "Failed to write manifest",
            project_id=project_id,
            error=str(e),
        )
        # Clean up temp file if it exists
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise
