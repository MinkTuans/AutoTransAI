"""
Structured logging configuration.

Uses structlog for JSON-formatted, structured logs.
Each log entry includes context like project_id, segment_id, provider, etc.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(log_level: str = "INFO", log_dir: Path | None = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR).
        log_dir: Optional directory for file-based logs.
    """
    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        if hasattr(sys.stderr, "reconfigure"):
            try:
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    # Configure stdlib logging as the base
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Structlog processors pipeline
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Use JSON or safe console renderer
    processors.append(
        structlog.dev.ConsoleRenderer(colors=False)
        if log_level.upper() == "DEBUG"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with the given name."""
    return structlog.get_logger(name)
