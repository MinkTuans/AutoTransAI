"""
FFmpeg Real-time Process Manager.

Spawns FFmpeg subprocesses with `-progress pipe:1` to stream real-time
progress stats (out_time, speed, fps, PID) without blocking the asyncio loop.
Supports Windows, Linux, and macOS natively using robust thread-safe process execution.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List

from app.core import get_logger
from app.media.ffprobe import get_ffmpeg_executable, is_ffmpeg_installed

# Ensure Windows ProactorEventLoopPolicy if possible
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

logger = get_logger(__name__)


class FFmpegExecutionError(RuntimeError):
    """Raised when an FFmpeg process fails to start or exits with a non-zero exit code."""
    def __init__(self, message: str, exit_code: int = -1, stderr_text: str = "", cmd: Optional[List[str]] = None):
        msg = message or f"FFmpeg execution failed with exit code {exit_code}"
        super().__init__(msg)
        self.message = msg
        self.exit_code = exit_code
        self.stderr_text = stderr_text
        self.cmd = cmd or []

    def __str__(self) -> str:
        err_detail = f" (STDERR: {self.stderr_text[:300]})" if self.stderr_text else ""
        return f"{self.message}{err_detail}"


async def run_ffmpeg_with_progress_async(
    cmd_args: List[str],
    total_duration: float = 0.0,
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_pid: Optional[Callable[[int], None]] = None,
    timeout: float = 600.0,
) -> Dict[str, Any]:
    """
    Run an FFmpeg command asynchronously, streaming real-time progress stats.
    Uses native subprocess execution to guarantee 100% compatibility across Windows event loops.

    Args:
        cmd_args: FFmpeg arguments list (e.g. ["ffmpeg", "-i", ...])
        total_duration: Total video/audio duration in seconds (if known)
        on_progress: Callback invoked whenever new progress stats arrive
        on_pid: Callback invoked when PID is created
        timeout: Maximum execution timeout in seconds

    Returns:
        Dict with execution summary (duration, stats, exit_code)
    """
    # Verify FFmpeg executable existence
    ffmpeg_bin = get_ffmpeg_executable()
    if not is_ffmpeg_installed():
        err_msg = (
            f"Không tìm thấy công cụ FFmpeg. "
            f"Đường dẫn đã kiểm tra: '{ffmpeg_bin}'. Vui lòng đảm bảo FFmpeg đã được cài đặt trong PATH hoặc venv."
        )
        logger.error("FFmpeg process failed to start", error=err_msg)
        raise FFmpegExecutionError(err_msg, exit_code=-1, stderr_text=err_msg, cmd=[ffmpeg_bin])

    # Build complete command with progress args inserted
    full_cmd = [ffmpeg_bin, "-hide_banner", "-loglevel", "error", "-progress", "pipe:1", "-nostats"]

    # Replace initial "ffmpeg" with binary path
    if cmd_args and cmd_args[0] in ("ffmpeg", "ffmpeg.exe"):
        full_cmd.extend(cmd_args[1:])
    else:
        full_cmd.extend(cmd_args)

    logger.info("Starting FFmpeg subprocess", binary=ffmpeg_bin, cmd=" ".join(full_cmd[:6]))

    # Spawn process using Popen for universal cross-platform and cross-event loop support
    try:
        process = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
        logger.info("FFmpeg process started successfully", pid=process.pid)
    except Exception as e:
        err_msg = f"Không thể khởi chạy tiến trình FFmpeg: {type(e).__name__}: {str(e) or repr(e)}"
        logger.error("FFmpeg process failed to start", error=err_msg)
        raise FFmpegExecutionError(err_msg, exit_code=-1, stderr_text=err_msg, cmd=full_cmd) from e

    if on_pid and process.pid:
        try:
            on_pid(process.pid)
        except Exception:
            pass

    stderr_lines: List[str] = []
    current_stats: Dict[str, Any] = {
        "pid": process.pid,
        "out_time": "00:00:00.00",
        "processed_seconds": 0.0,
        "total_duration": total_duration,
        "progress_pct": 0.0,
        "speed": "N/A",
        "fps": "N/A",
        "status": "RUNNING",
    }

    loop = asyncio.get_running_loop()

    def _read_process_worker() -> int:
        nonlocal current_stats
        last_callback_time = 0.0

        # Read stderr stream concurrently in background thread to prevent pipe buffer deadlock
        def _read_stderr():
            if process.stderr:
                for line in process.stderr:
                    l_str = line.strip()
                    if l_str:
                        stderr_lines.append(l_str)

        import threading
        stderr_thread = threading.Thread(target=_read_stderr, daemon=True)
        stderr_thread.start()

        # Read stdout stream for real-time progress
        if process.stdout:
            for line in process.stdout:
                line_str = line.strip()
                if not line_str or "=" not in line_str:
                    continue

                key, _, val = line_str.partition("=")
                key = key.strip()
                val = val.strip()

                if key == "out_time_us" and val.isdigit():
                    us = int(val)
                    sec = round(us / 1000000.0, 2)
                    current_stats["processed_seconds"] = sec
                    if total_duration > 0:
                        current_stats["progress_pct"] = min(99.9, round((sec / total_duration) * 100.0, 1))
                elif key == "out_time":
                    current_stats["out_time"] = val[:11]
                elif key == "speed":
                    current_stats["speed"] = val
                elif key == "fps":
                    current_stats["fps"] = val
                elif key == "progress" and val == "end":
                    current_stats["progress_pct"] = 100.0
                    current_stats["status"] = "COMPLETED"

                now = time.time()
                if on_progress and (now - last_callback_time >= 0.3 or val == "end"):
                    last_callback_time = now
                    snap = dict(current_stats)
                    loop.call_soon_threadsafe(on_progress, snap)

        stderr_thread.join(timeout=5.0)

        try:
            return process.wait(timeout=timeout)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
            return -1

    try:
        returncode = await asyncio.to_thread(_read_process_worker)
    except Exception as ex:
        try:
            process.kill()
        except Exception:
            pass
        err_msg = f"FFmpeg execution timed out or failed: {str(ex)}"
        raise FFmpegExecutionError(err_msg, exit_code=-1, stderr_text=err_msg, cmd=full_cmd) from ex

    if returncode != 0:
        err_msg = "\n".join(stderr_lines[-50:]) if stderr_lines else f"FFmpeg error exit code {returncode}"
        logger.error("FFmpeg process failed", pid=process.pid, returncode=returncode, error=err_msg[:300])
        raise FFmpegExecutionError(
            f"FFmpeg thất bại với mã lỗi (exit code {returncode})",
            exit_code=returncode or -1,
            stderr_text=err_msg,
            cmd=full_cmd,
        )

    current_stats["progress_pct"] = 100.0
    current_stats["status"] = "COMPLETED"
    if on_progress:
        try:
            on_progress(dict(current_stats))
        except Exception:
            pass

    return current_stats
