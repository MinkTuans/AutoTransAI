"""
Security utilities.

Handles filename sanitization, path validation, and subprocess safety.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath, PureWindowsPath

from app.core import get_logger

logger = get_logger(__name__)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for safe use as a filename.

    Removes path separators, null bytes, and other dangerous characters.
    Returns a safe, deterministic filename component.
    """
    # Remove null bytes
    name = name.replace("\x00", "")
    # Replace path separators and other dangerous chars
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Remove leading/trailing dots and spaces
    name = name.strip(". ")
    # Limit length
    if len(name) > 200:
        name = name[:200]
    # Fallback if empty
    if not name:
        name = "unnamed"
    return name


def validate_path_within(path: Path, base_dir: Path) -> Path:
    """
    Validate that a path is within the expected base directory.
    Prevents path traversal attacks.

    Args:
        path: The path to validate.
        base_dir: The directory the path must be within.

    Returns:
        The resolved, validated path.

    Raises:
        ValueError: If the path escapes the base directory.
    """
    resolved = path.resolve()
    base_resolved = base_dir.resolve()

    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError(
            f"Path traversal detected: {path} resolves outside {base_dir}"
        )

    return resolved


def safe_subprocess_run(
    args: list[str],
    *,
    timeout: int = 300,
    capture_output: bool = True,
    check: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    Run a subprocess safely with list arguments.

    NEVER use shell=True or string interpolation for commands.

    Args:
        args: Command and arguments as a list of strings.
        timeout: Maximum execution time in seconds.
        capture_output: Whether to capture stdout/stderr.
        check: Whether to raise on non-zero exit code.
        cwd: Working directory for the command.

    Returns:
        CompletedProcess result.

    Raises:
        subprocess.CalledProcessError: On non-zero exit code (if check=True).
        subprocess.TimeoutExpired: If command exceeds timeout.
    """
    logger.debug(
        "Running subprocess",
        command=args[0] if args else "empty",
        arg_count=len(args),
    )

    return subprocess.run(
        args,
        capture_output=capture_output,
        text=True,
        timeout=timeout,
        check=check,
        cwd=cwd,
        shell=False,  # Explicit: NEVER use shell=True
    )
