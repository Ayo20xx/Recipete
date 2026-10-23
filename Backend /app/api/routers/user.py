from fastapi import APIRouter

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import Authentication

router = APIRouter()

@router.post("/register")
async def registration(input:UserCreate,session:get_db ):
    return await Authentication.register(input,session)
@router.post("/login")
async def login(input:UserCreate,session:get_db):
    return await Authentication.login(input,session)

    