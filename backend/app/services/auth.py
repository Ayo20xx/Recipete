import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import exists, select

from app.core.security import (
    ACCESS_TOKEN_TTL_SECONDS,
    create_refresh_token,
    encode_jwt,
    hash_password,
    hash_refresh_token,
    verify_google_id_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

REFRESH_TOKEN_TTL = timedelta(days=30)


def _unauthorized_refresh_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )


async def _issue_token_pair(
    user: User,
    session: AsyncSession,
) -> dict[str, str | int]:
    now = datetime.now(timezone.utc)
    refresh_token, refresh_token_hash = create_refresh_token()
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=now + REFRESH_TOKEN_TTL,
        )
    )
    await session.commit()
    return {
        "access_token": encode_jwt(user.id),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_TTL_SECONDS,
    }


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
            name=input.name,
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
        return await _issue_token_pair(new_User, session)

    async def login(input: UserLogin, session: AsyncSession):
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
       return await _issue_token_pair(user, session)

    async def google_login(id_token: str, session: AsyncSession):
        google_sub, email, name = await asyncio.to_thread(
            verify_google_id_token,
            id_token,
        )
        user = await session.scalar(
            select(User).where(User.google_sub == google_sub)
        )
        if user is not None:
            if user.name is None and name is not None:
                user.name = name
                await session.commit()
            return await _issue_token_pair(user, session)

        existing_email = await session.scalar(
            select(User).where(User.email == email)
        )
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists; sign in and link Google",
            )

        user = User(email=email, name=name, google_sub=google_sub)
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

        return await _issue_token_pair(user, session)

    async def refresh(refresh_token: str, session: AsyncSession):
        now = datetime.now(timezone.utc)
        result = await session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == hash_refresh_token(refresh_token),
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
            .values(revoked_at=now)
            .returning(RefreshToken.user_id)
        )
        user_id = result.scalar_one_or_none()
        if user_id is None:
            await session.rollback()
            raise _unauthorized_refresh_token()

        user = await session.get(User, user_id)
        if user is None:
            await session.rollback()
            raise _unauthorized_refresh_token()

        return await _issue_token_pair(user, session)

    async def logout(refresh_token: str, session: AsyncSession) -> None:
        await session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == hash_refresh_token(refresh_token),
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await session.commit()

    async def link_google(
        id_token: str,
        current_user: User,
        session: AsyncSession,
    ):
        google_sub, _email, google_name = await asyncio.to_thread(
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
        if current_user.name is None and google_name is not None:
            current_user.name = google_name
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is linked to another user",
            )

        return {"message": "Google account linked"}