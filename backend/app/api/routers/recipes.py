from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.recipe import (
    RecipeDetails,
    RecipeSummary,
    SavedRecipeRead,
)
from app.services.recipes import (
    get_random_recipe,
    get_recipe_details,
    search_recipes,
)
from app.services.user_content import (
    RecipeProvider,
    list_saved_recipes,
    save_recipe,
    unsave_recipe,
)

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


@recipes_router.get("/random", response_model=RecipeDetails)
async def random_recipe():
    return await get_random_recipe()


@recipes_router.get("/{meal_id}", response_model=RecipeDetails)
async def details(meal_id: Annotated[str, Path(pattern=r"^\d+$")]):
    return await get_recipe_details(meal_id)


@recipes_router.get("/me/saved", response_model=list[SavedRecipeRead])
async def saved_recipes(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await list_saved_recipes(session, current_user)


@recipes_router.put(
    "/me/saved/{provider}/{recipe_id}",
    response_model=SavedRecipeRead,
)
async def save(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await save_recipe(session, current_user, provider, recipe_id)


@recipes_router.delete(
    "/me/saved/{provider}/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unsave(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await unsave_recipe(session, current_user, provider, recipe_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
