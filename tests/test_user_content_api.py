import os
import sys
import unittest
from pathlib import Path

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


class RecipeApiSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_openapi_schema_lists_recipe_search(self) -> None:
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["info"]["title"], "Recipe API")
        self.assertIn("/api/v1/recipes/search", response.json()["paths"])

    def test_recipe_search_rejects_empty_query(self) -> None:
        response = self.client.get("/api/v1/recipes/search", params={"query": ""})

        self.assertEqual(response.status_code, 422)
