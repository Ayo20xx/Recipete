from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.recipe import NotificationInbox
from app.schemas.user import GoogleTokenRequest, UserCreate, UserRead
from app.services.auth import Authentication
from app.services.user_content import (
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

user_router = APIRouter()

@user_router.post("/register",status_code=status.HTTP_201_CREATED)
async def registration(input:UserCreate,session:SessionDep ):
    return await Authentication.register(input,session)
@user_router.post("/login")
async def login(input:UserCreate,session:SessionDep):
    return await Authentication.login(input,session)


@user_router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUserDep):
    return current_user


@user_router.post("/google")
async def google_login(input: GoogleTokenRequest, session: SessionDep):
    return await Authentication.google_login(input.id_token, session)


@user_router.post("/google/link")
async def link_google(
    input: GoogleTokenRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await Authentication.link_google(input.id_token, current_user, session)


@user_router.get("/me/notifications", response_model=NotificationInbox)
async def notifications(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await list_notifications(session, current_user)


@user_router.post(
    "/me/notifications/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def read_all_notifications(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await mark_all_notifications_read(session, current_user)
    return None


@user_router.post(
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