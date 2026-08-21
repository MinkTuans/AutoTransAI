"""
Job-specific Logger Module.

Provides clean, structured, timestamped log recording per Job ID
for the UI Log Viewer and server-side troubleshooting.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from app.config import get_settings

settings = get_settings()

_JOB_LOG_BUFFERS: Dict[str, list[str]] = {}


def log_job_event(job_id: str, stage: str, message: str) -> str:
    """
    Log a timestamped event for a specific job ID.

    Sanitizes API keys and writes to data/translator/jobs/{job_id}/job.log.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Mask sensitive API keys
    safe_msg = message
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5:
        safe_msg = safe_msg.replace(settings.GEMINI_API_KEY, "***GEMINI_KEY***")
    if settings.ELEVENLABS_API_KEY and len(settings.ELEVENLABS_API_KEY) > 5:
        safe_msg = safe_msg.replace(settings.ELEVENLABS_API_KEY, "***ELEVENLABS_KEY***")

    entry = f"[{now_str}] [{job_id}] [{stage}] {safe_msg}"

    # Append to memory buffer
    if job_id not in _JOB_LOG_BUFFERS:
        _JOB_LOG_BUFFERS[job_id] = []
    _JOB_LOG_BUFFERS[job_id].append(entry)

    # Append to disk log file
    job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    log_file = job_dir / "job.log"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

    return entry


def get_job_logs(job_id: str) -> str:
    """
    Fetch full log content for a given job ID.
    Reads from disk log file if available, falling back to memory buffer.
    """
    job_dir = settings.DATA_DIR / "translator" / "jobs" / job_id
    log_file = job_dir / "job.log"
    if log_file.exists():
        try:
            return log_file.read_text(encoding="utf-8")
        except Exception:
            pass

    buffer = _JOB_LOG_BUFFERS.get(job_id, [])
    return "\n".join(buffer)
