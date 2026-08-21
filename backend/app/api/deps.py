"""
FastAPI dependency injection.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.providers.registry import get_registry


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Get a database session (alias for get_session)."""
    async for session in get_session():
        yield session
