import httpx

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.recipe import RecipeDetails, RecipeIngredient, RecipeSummary


BASE_URL = "https://www.themealdb.com/api/json/v1"


async def _fetch_meals(endpoint: str, params: dict[str, str]) -> list[dict]:
    if settings.mealdb_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recipe search is not configured",
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/{settings.mealdb_api_key}/{endpoint}",
                params=params,
            )
        response.raise_for_status()
        payload = response.json()
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Recipe provider timed out",
        ) from error
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe provider request failed",
        ) from error

    if not isinstance(payload, dict) or "meals" not in payload:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe provider returned an invalid response",
        )

    meals = payload["meals"]
    if meals is None:
        return []
    if not isinstance(meals, list) or not all(isinstance(meal, dict) for meal in meals):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Recipe provider returned an invalid response",
        )
    return meals


async def search_recipes(
    *,
    query: str | None = None,
    ingredient: str | None = None,
    category: str | None = None,
    area: str | None = None,
) -> list[RecipeSummary]:
    filters = {
        "s": query,
        "i": ingredient,
        "c": category,
        "a": area,
    }
    selected_filters = {
        parameter: value.strip()
        for parameter, value in filters.items()
        if value is not None and value.strip()
    }
    if len(selected_filters) != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Provide exactly one of query, ingredient, category, or area",
        )

    meals = await _fetch_meals(
        "search.php" if "s" in selected_filters else "filter.php",
        selected_filters,
    )
    return [
        RecipeSummary(
            id=meal["idMeal"],
            name=meal["strMeal"],
            image_url=meal.get("strMealThumb"),
        )
        for meal in meals
        if isinstance(meal.get("idMeal"), str)
        and isinstance(meal.get("strMeal"), str)
    ]


async def get_recipe_details(meal_id: str) -> RecipeDetails:
    meals = await _fetch_meals("lookup.php", {"i": meal_id})
    if not meals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    meal = meals[0]
    ingredients = []
    for index in range(1, 21):
        name = meal.get(f"strIngredient{index}")
        if isinstance(name, str) and name.strip():
            ingredients.append(
                RecipeIngredient(
                    name=name.strip(),
                    measure=(meal.get(f"strMeasure{index}") or "").strip(),
                )
            )

    return RecipeDetails(
        id=meal["idMeal"],
        name=meal["strMeal"],
        image_url=meal.get("strMealThumb"),
        category=meal.get("strCategory"),
        area=meal.get("strArea"),
        instructions=meal.get("strInstructions"),
        source_url=meal.get("strSource"),
        ingredients=ingredients,
    )
