from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.user import (
    AuthTokenResponse,
    GoogleTokenRequest,
    RefreshTokenRequest,
    UserCreate,
    UserLogin,
    UserNameUpdate,
    UserRead,
)
from app.services.auth import Authentication

user_router = APIRouter()


@user_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthTokenResponse,
)
async def registration(input: UserCreate, session: SessionDep):
    return await Authentication.register(input,session)


@user_router.post("/login", response_model=AuthTokenResponse)
async def login(input: UserLogin, session: SessionDep):
    return await Authentication.login(input,session)


@user_router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUserDep):
    return current_user


@user_router.patch("/me", response_model=UserRead)
async def update_me(
    input: UserNameUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await Authentication.update_name(input.name, current_user, session)


@user_router.post("/google", response_model=AuthTokenResponse)
async def google_login(input: GoogleTokenRequest, session: SessionDep):
    return await Authentication.google_login(input.id_token, session)


@user_router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_tokens(input: RefreshTokenRequest, session: SessionDep):
    return await Authentication.refresh(input.refresh_token, session)


@user_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(input: RefreshTokenRequest, session: SessionDep):
    await Authentication.logout(input.refresh_token, session)


@user_router.post("/google/link")
async def link_google(
    input: GoogleTokenRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await Authentication.link_google(input.id_token, current_user, session)
