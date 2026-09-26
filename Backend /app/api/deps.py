"""Shared API dependencies."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db as get_database_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session to API endpoints."""

    async for session in get_database_session():
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
