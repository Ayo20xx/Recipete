from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def is_exists(
    session: AsyncSession,
    email: str
) -> bool:
    statement = select(
        exists().where(session.email == email)
    )

    is_exists = await session.scalar(statement)

    return is_exists






class Authentication:

    async def register(input:UserCreate,session: AsyncSession ):
        if is_exists(User,input.email):
            raise HTTPException (status_code=status.HTTP_409_CONFLICT,detail="this email already exists")
        pwd_hash= hash_password(input.password)
        new_User = User(
            email= input.email,
            password_hash= pwd_hash
        )
        session.add(new_User)
        await session.commit()
        await session.refresh(new_User)
        return {"message":"succesfully registered"}

    async def login(input:,session )