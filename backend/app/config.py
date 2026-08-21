"""
Application configuration using Pydantic Settings.

All configurable values are centralized here. Override via .env file or
environment variables. No magic numbers should exist outside this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE_PATH = ROOT_DIR / ".env" if (ROOT_DIR / ".env").exists() else ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Paths ──────────────────────────────────────────────────────────
    DATA_DIR: Path = Path("data")
    DB_FILENAME: str = "workflow.db"

    @property
    def DB_URL(self) -> str:
        db_path = self.DATA_DIR / self.DB_FILENAME
        return f"sqlite+aiosqlite:///{db_path}"

    @property
    def PROJECTS_DIR(self) -> Path:
        return self.DATA_DIR / "projects"

    # ── Video ──────────────────────────────────────────────────────────
    VIDEO_TARGET_DURATION: int = 8  # seconds per segment clip
    VIDEO_OUTPUT_RESOLUTION: str = "1080p"
    VIDEO_FORMAT: str = "mp4"
    VIDEO_MAX_SIZE_MB: int = 500
    VIDEO_MAX_DURATION_MINUTES: int = 60
    VIDEO_DOWNLOAD_TIMEOUT: int = 300

    # ── Audio ──────────────────────────────────────────────────────────
    AUDIO_FORMAT: str = "wav"
    AUDIO_SAMPLE_RATE: int = 24000

    # ── Workflow ───────────────────────────────────────────────────────
    MAX_CONCURRENCY: int = 2
    MAX_RETRIES: int = 3
    RETRY_INITIAL_DELAY: float = 2.0  # seconds
    RETRY_MAX_DELAY: float = 60.0  # seconds
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_JITTER: bool = True

    # ── Sync ───────────────────────────────────────────────────────────
    DEFAULT_SYNC_STRATEGY: Literal[
        "trim_video", "loop_video", "pad_video", "speed_video"
    ] = "trim_video"
    SYNC_TOLERANCE_SECONDS: float = 0.5

    # ── Provider API Keys ──────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GOOGLE_CLOUD_TTS_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    KLING_API_KEY: str = ""
    KLING_API_SECRET: str = ""
    FAL_API_KEY: str = ""

    # ── Server ─────────────────────────────────────────────────────────
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False


def get_settings() -> Settings:
    """Factory function for settings. Enables dependency injection in tests."""
    return Settings()
