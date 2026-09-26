from fastapi import APIRouter

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import Authentication

router = APIRouter()

router.post("/register")
async def registration(input:UserCreate,session:User ):
    return await Authentication.register(input,session)

    