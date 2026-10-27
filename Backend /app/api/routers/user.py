from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.user import UserCreate, UserRead
from app.services.auth import Authentication

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