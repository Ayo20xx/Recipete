import asyncio

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.core.security import (
    encode_jwt,
    hash_password,
    verify_google_id_token,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate


async def is_exists(
    session: AsyncSession,
    email: str
) -> bool:
    statement = select(exists().where(User.email == email))  

    user_exists = await session.scalar(statement)

    return user_exists


async def get_user_by_email(email:str,session:AsyncSession):
    statement=select(User).where(User.email == email)

    result = await session.execute(statement)
    return result.scalar_one_or_none()




class Authentication:

    async def register(input:UserCreate,session: AsyncSession ):
        if await is_exists(session,input.email):
            raise HTTPException (status_code=status.HTTP_409_CONFLICT,detail="this email already exists")
        pwd_hash= hash_password(input.password)
        new_User = User(
            email= input.email,
            password_hash= pwd_hash
        )
        try:
            session.add(new_User)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="this email already exists",
            )

        await session.refresh(new_User)
        return {"message":"successfully registered"}

    async def login(input:UserCreate,session: AsyncSession):
       user=await get_user_by_email(input.email, session)
       if (
           user is None
           or user.password_hash is None
           or not verify_password(input.password, user.password_hash)
       ):
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Incorrect email or password.",
           )
       jwt=encode_jwt(user.id)
       return {"access_token": jwt, "token_type": "bearer"}

    async def google_login(id_token: str, session: AsyncSession):
        google_sub, email = await asyncio.to_thread(verify_google_id_token, id_token)
        user = await session.scalar(
            select(User).where(User.google_sub == google_sub)
        )
        if user is not None:
            return {"access_token": encode_jwt(user.id), "token_type": "bearer"}

        existing_email = await session.scalar(
            select(User).where(User.email == email)
        )
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists; sign in and link Google",
            )

        user = User(email=email, google_sub=google_sub)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            user = await session.scalar(
                select(User).where(User.google_sub == google_sub)
            )
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Unable to create Google account",
                )

        return {"access_token": encode_jwt(user.id), "token_type": "bearer"}

    async def link_google(
        id_token: str,
        current_user: User,
        session: AsyncSession,
    ):
        google_sub, _email = await asyncio.to_thread(
            verify_google_id_token,
            id_token,
        )
        if current_user.google_sub == google_sub:
            return {"message": "Google account already linked"}
        if current_user.google_sub is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A Google account is already linked",
            )

        linked_user = await session.scalar(
            select(User).where(User.google_sub == google_sub)
        )
        if linked_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is linked to another user",
            )

        current_user.google_sub = google_sub
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is linked to another user",
            )

        return {"message": "Google account linked"}