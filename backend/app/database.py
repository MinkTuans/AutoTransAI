"""
Database engine and session management.

Uses SQLAlchemy 2.0 async with aiosqlite for SQLite.
WAL mode is enabled for better concurrent read performance.
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def _ensure_db_directory() -> None:
    """Ensure the database directory exists."""
    db_path = settings.DATA_DIR / settings.DB_FILENAME
    db_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_db_directory()

engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables and enable WAL mode."""
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrent read performance
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    """Dependency injection for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
