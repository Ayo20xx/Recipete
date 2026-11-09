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
from app.api.deps import get_admin_user
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.admin import promote_user_to_admin
from app.services.auth import Authentication
from app.services.recipes import get_random_recipe
from app.services.user_content import broadcast_notification


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
        self.assertEqual(RefreshToken.__tablename__, "refresh_token")

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

    async def test_broadcast_creates_a_notice_for_each_user(self) -> None:
        async with self.session_factory() as session:
            session.add_all(
                [
                    User(email="one@example.com"),
                    User(email="two@example.com"),
                ]
            )
            await session.commit()

            result = await broadcast_notification(
                session,
                "App update",
                "Please update the app.",
            )
            self.assertEqual(result["recipient_count"], 2)

            notices = list(await session.scalars(select(Notification)))
            self.assertEqual(len(notices), 2)
            self.assertTrue(all(notice.title == "App update" for notice in notices))
            self.assertTrue(all(notice.review_id is None for notice in notices))

    async def test_random_recipe_uses_random_provider_result(self) -> None:
        meal = {
            "idMeal": "42",
            "strMeal": "Test Dish",
            "strMealThumb": None,
            "strCategory": "Dinner",
            "strArea": "Test",
            "strInstructions": "Cook it.",
            "strSource": None,
            "strIngredient1": "Rice",
            "strMeasure1": "1 cup",
        }
        with patch(
            "app.services.recipes._fetch_meals",
            return_value=[meal],
        ) as fetch:
            recipe = await get_random_recipe()

        self.assertEqual(recipe.id, "42")
        self.assertEqual(recipe.name, "Test Dish")
        self.assertEqual(recipe.ingredients[0].name, "Rice")
        fetch.assert_awaited_once_with("random.php", {})

    async def test_name_update_persists_and_admin_guard_rejects_regular_users(self) -> None:
        async with self.session_factory() as session:
            user = User(email="profile@example.com", name="Old Name")
            session.add(user)
            await session.commit()

            updated_user = await Authentication.update_name(
                "Updated Name",
                user,
                session,
            )
            self.assertEqual(updated_user.name, "Updated Name")

            with self.assertRaises(HTTPException) as error:
                await get_admin_user(updated_user)
            self.assertEqual(error.exception.status_code, 403)

            updated_user.is_admin = True
            self.assertIs(await get_admin_user(updated_user), updated_user)

    async def test_existing_admin_can_promote_a_registered_user(self) -> None:
        async with self.session_factory() as session:
            user = User(email="promoted@example.com", name="Promoted User")
            session.add(user)
            await session.commit()

            promoted_user = await promote_user_to_admin(session, user.id)
            self.assertTrue(promoted_user.is_admin)

            repeated_promotion = await promote_user_to_admin(session, user.id)
            self.assertTrue(repeated_promotion.is_admin)
