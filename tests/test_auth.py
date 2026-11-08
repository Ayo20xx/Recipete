import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select


os.environ.update(
    {
        "APP_NAME": "Recipete test",
        "ENVIRONMENT": "test",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "SECRET": "test-secret-with-more-than-thirty-two-bytes",
    }
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.security import decode_jwt
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import Authentication


class AuthenticationTokenTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()

    async def test_registration_returns_tokens_and_refresh_rotates_once(self) -> None:
        async with self.session_factory() as session:
            tokens = await Authentication.register(
                UserCreate(
                    email="maria@example.com",
                    password="correct-horse-battery",
                    name="Maria Recipe",
                ),
                session,
            )

            self.assertTrue(tokens["access_token"])
            self.assertTrue(tokens["refresh_token"])
            self.assertEqual(tokens["token_type"], "bearer")
            self.assertEqual(tokens["expires_in"], 900)

            stored_token = await session.scalar(select(RefreshToken))
            self.assertIsNotNone(stored_token)
            self.assertNotEqual(stored_token.token_hash, tokens["refresh_token"])

            rotated_tokens = await Authentication.refresh(
                tokens["refresh_token"],
                session,
            )
            self.assertNotEqual(
                rotated_tokens["refresh_token"],
                tokens["refresh_token"],
            )

            with self.assertRaises(HTTPException) as error:
                await Authentication.refresh(tokens["refresh_token"], session)
            self.assertEqual(error.exception.status_code, 401)

    async def test_google_login_saves_google_name_and_returns_access_token(self) -> None:
        with patch(
            "app.services.auth.verify_google_id_token",
            return_value=("google-subject", "google@example.com", "Google User"),
        ):
            async with self.session_factory() as session:
                tokens = await Authentication.google_login("google-id-token", session)
                user = await session.scalar(
                    select(User).where(User.google_sub == "google-subject")
                )

        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Google User")
        self.assertEqual(decode_jwt(tokens["access_token"])["type"], "access")
