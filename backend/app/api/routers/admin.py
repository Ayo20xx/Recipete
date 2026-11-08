from uuid import UUID

from fastapi import APIRouter

from app.api.deps import AdminUserDep, SessionDep
from app.models.user import User
from app.schemas.user import AdminUserRead
from app.services.admin import promote_user_to_admin

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post(
    "/users/{user_id}/promote",
    response_model=AdminUserRead,
)
async def promote_user(
    user_id: UUID,
    _admin: AdminUserDep,
    session: SessionDep,
) -> User:
    return await promote_user_to_admin(session, user_id)
