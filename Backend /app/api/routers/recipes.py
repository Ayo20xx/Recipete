from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.schemas.recipe import RecipeDetails, RecipeSummary
from app.services.recipes import get_recipe_details, search_recipes


recipes_router = APIRouter(prefix="/recipes", tags=["recipes"])


@recipes_router.get("/search", response_model=list[RecipeSummary])
async def search(
    query: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    ingredient: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    category: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    area: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
):
    return await search_recipes(
        query=query,
        ingredient=ingredient,
        category=category,
        area=area,
    )


@recipes_router.get("/{meal_id}", response_model=RecipeDetails)
async def details(meal_id: Annotated[str, Path(pattern=r"^\d+$")]):
    return await get_recipe_details(meal_id)
