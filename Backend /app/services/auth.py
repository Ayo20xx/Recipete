from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def is_exists(
    session: AsyncSession,
    email: str
) -> bool:
    statement = select(exists().where(User.email == email))  # noqa: F823

    exists = await session.scalar(statement)

    return exists


async def get_user_by_email(email:str,session:AsyncSession):
    statement=select(User).where(User.email == email)

    result=await(session.execute(statement)).scalar_one_or_none()
    return result




class Authentication:

    async def register(input:UserCreate,session: AsyncSession ):
        if await is_exists(User,input.email):
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

    async def login(input:UserCreate,session: AsyncSession):
       user=get_user_by_email(input.email)
       if user is None or verify_password(input.password,user.password_hash) is False:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,details="Incorrect email or password.")
       