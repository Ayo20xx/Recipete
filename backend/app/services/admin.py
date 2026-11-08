from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def promote_user_to_admin(
    session: AsyncSession,
    user_id: UUID,
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_admin:
        user.is_admin = True
        await session.commit()
        await session.refresh(user)
    return user
