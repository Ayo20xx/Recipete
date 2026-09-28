"""Async database engine and session configuration."""

from collections.abc import AsyncGenerator
from typing import Annotated

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite+")
    else {},
)
AsyncSessionLocal = async_sessionmaker[AsyncSession](
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for a request."""

    async with AsyncSessionLocal() as db:
        yield db

Sessiondep= Annotated[AsyncSession,get_db]