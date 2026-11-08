from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.recipe import NotificationInbox
from app.services.user_content import (
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

notifications_router = APIRouter(tags=["notifications"])


@notifications_router.get("/me/notifications", response_model=NotificationInbox)
async def notifications(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await list_notifications(session, current_user)


@notifications_router.post(
    "/me/notifications/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def read_all_notifications(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await mark_all_notifications_read(session, current_user)


@notifications_router.post(
    "/me/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def read_notification(
    notification_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await mark_notification_read(
        session,
        current_user,
        notification_id,
    )
