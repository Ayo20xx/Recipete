from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import Authentication

user_router = APIRouter()

@user_router.post("/register",status_code=status.HTTP_201_CREATED)
async def registration(input:UserCreate,session:SessionDep ):
    return await Authentication.register(input,session)
@user_router.post("/login")
async def login(input:UserCreate,session:SessionDep):
    return await Authentication.login(input,session)

    