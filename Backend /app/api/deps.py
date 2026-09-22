"""Shared API dependencies."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db as get_database_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session to API endpoints."""

    async for session in get_database_session():
        yield session
