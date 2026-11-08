import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


os.environ.update(
    {
        "APP_NAME": "Recipete test",
        "ENVIRONMENT": "test",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "SECRET": "test-secret-with-more-than-thirty-two-bytes",
    }
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app
from app.core.config import Settings


class RecipeApiSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_openapi_schema_lists_recipe_search(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["info"]["title"], "Recipe API")
        self.assertIn("/api/v1/recipes/search", response.json()["paths"])
        self.assertIn(
            "/api/v1/recipes/{provider}/{recipe_id}/reviews",
            response.json()["paths"],
        )
        self.assertIn("/api/v1/me/notifications", response.json()["paths"])
        self.assertIn("/api/v1/refresh", response.json()["paths"])

    def test_recipe_search_rejects_empty_query(self) -> None:
        response = self.client.get("/api/v1/recipes/search", params={"query": ""})

        self.assertEqual(response.status_code, 422)

    def test_settings_default_app_name_when_environment_variable_is_missing(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "test",
                "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
                "SECRET": "test-secret-with-more-than-thirty-two-bytes",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)

        self.assertEqual(settings.app_name, "Recipete")

    def test_settings_normalize_render_postgresql_urls_for_async_driver(self) -> None:
        for database_url in (
            "postgres://user:password@localhost/recipete",
            "postgresql://user:password@localhost/recipete",
        ):
            with self.subTest(database_url=database_url.split(":", 1)[0]):
                settings = Settings(
                    app_name="Recipete",
                    environment="test",
                    database_url=database_url,
                    secret="test-secret-with-more-than-thirty-two-bytes",
                    _env_file=None,
                )

                self.assertEqual(
                    settings.database_url,
                    database_url.replace(
                        database_url.split("://", 1)[0],
                        "postgresql+asyncpg",
                        1,
                    ),
                )
