"""
Shared Configuration Manager for WorkflowVdAi.

Centralizes project root determination and root .env loading across
all core services and external sub-applications.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """
    Find the root directory of the WorkflowVdAi project.
    Searches upward from this file location until finding .env or README.md.
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".env").exists() or (current / "README.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()
ROOT_ENV_PATH = PROJECT_ROOT / ".env"


def parse_env_file(filepath: Path) -> Dict[str, str]:
    """Parse a simple .env file into key-value pairs without modifying os.environ."""
    env_vars: Dict[str, str] = {}
    if not filepath.exists():
        return env_vars

    try:
        content = filepath.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key:
                env_vars[key] = value
    except Exception as e:
        print(f"[SharedConfig] Warning: Failed to parse {filepath}: {e}")

    return env_vars


def load_root_env(override: bool = True) -> Dict[str, str]:
    """
    Load environment variables from PROJECT_ROOT/.env into os.environ.

    Args:
        override: If True, overwrite existing os.environ keys with values from .env.
    """
    parsed = parse_env_file(ROOT_ENV_PATH)
    for k, v in parsed.items():
        if override or k not in os.environ:
            os.environ[k] = v
    return parsed


# Auto-load on import
load_root_env(override=True)
