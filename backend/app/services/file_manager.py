"""
File manager — handles project directory structure and file operations.

All media files are stored locally in a deterministic structure.
Filenames are never user-supplied — always generated from segment numbers.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.config import get_settings
from app.core import get_logger
from app.core.exceptions import StorageError
from app.core.security import validate_path_within

logger = get_logger(__name__)
settings = get_settings()


def get_project_dir(project_id: str) -> Path:
    """Get the root directory for a project."""
    return settings.PROJECTS_DIR / project_id


def ensure_project_structure(project_id: str) -> dict[str, Path]:
    """
    Create the full directory structure for a project.

    Returns:
        Dict mapping directory names to their paths.
    """
    base = get_project_dir(project_id)
    dirs = {
        "root": base,
        "script": base / "script",
        "audio": base / "audio",
        "video": base / "video",
        "tmp": base / "tmp",
        "output": base / "output",
        "logs": base / "logs",
    }

    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory", path=str(path), name=name)

    return dirs


def ensure_segment_dirs(project_id: str, segment_number: int) -> dict[str, Path]:
    """
    Create segment-specific subdirectories.

    Returns:
        Dict with 'audio' and 'video' paths for this segment.
    """
    base = get_project_dir(project_id)
    seg_name = f"segment_{segment_number:03d}"

    dirs = {
        "audio": base / "audio" / seg_name,
        "video": base / "video" / seg_name,
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return dirs


def get_segment_audio_path(project_id: str, segment_number: int) -> Path:
    """Get the deterministic audio file path for a segment."""
    seg_name = f"segment_{segment_number:03d}"
    return (
        get_project_dir(project_id)
        / "audio"
        / seg_name
        / f"{seg_name}_audio.{settings.AUDIO_FORMAT}"
    )


def get_segment_video_path(project_id: str, segment_number: int) -> Path:
    """Get the deterministic video file path for a segment."""
    seg_name = f"segment_{segment_number:03d}"
    return (
        get_project_dir(project_id)
        / "video"
        / seg_name
        / f"{seg_name}_video.{settings.VIDEO_FORMAT}"
    )


def get_segment_merged_path(project_id: str, segment_number: int) -> Path:
    """Get the deterministic merged file path for a segment."""
    seg_name = f"segment_{segment_number:03d}"
    return (
        get_project_dir(project_id)
        / "output"
        / f"{seg_name}_final.{settings.VIDEO_FORMAT}"
    )


def get_final_output_path(project_id: str) -> Path:
    """Get the final video output path."""
    return (
        get_project_dir(project_id)
        / "output"
        / f"final_video.{settings.VIDEO_FORMAT}"
    )


def get_manifest_path(project_id: str) -> Path:
    """Get the manifest.json path for a project."""
    return get_project_dir(project_id) / "manifest.json"


def get_project_log_path(project_id: str) -> Path:
    """Get the log file path for a project."""
    return get_project_dir(project_id) / "logs" / "workflow.log"


def check_storage_writable(project_id: str) -> bool:
    """Check if the project storage directory is writable."""
    try:
        base = get_project_dir(project_id)
        base.mkdir(parents=True, exist_ok=True)
        test_file = base / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        return True
    except OSError as e:
        logger.error("Storage not writable", project_id=project_id, error=str(e))
        return False


def get_disk_space_mb(project_id: str) -> float | None:
    """Get available disk space in MB for the project directory."""
    try:
        base = get_project_dir(project_id)
        base.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(base)
        return usage.free / (1024 * 1024)
    except OSError:
        return None


def clean_temp_files(project_id: str) -> int:
    """
    Clean temporary files for a project. Never deletes completed assets.

    Returns:
        Number of files deleted.
    """
    tmp_dir = get_project_dir(project_id) / "tmp"
    if not tmp_dir.exists():
        return 0

    count = 0
    for f in tmp_dir.iterdir():
        if f.is_file():
            f.unlink()
            count += 1

    logger.info("Cleaned temp files", project_id=project_id, files_deleted=count)
    return count


def delete_project_files(project_id: str) -> None:
    """Delete all files for a project. Use with caution."""
    project_dir = get_project_dir(project_id)
    if project_dir.exists():
        # Validate path is within data directory to prevent traversal
        validate_path_within(project_dir, settings.DATA_DIR)
        shutil.rmtree(project_dir)
        logger.info("Deleted project files", project_id=project_id)
