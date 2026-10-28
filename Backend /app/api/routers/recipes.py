from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.recipe import (
    RecipeDetails,
    RecipeReviewCreate,
    RecipeReviewList,
    RecipeReviewRead,
    RecipeSummary,
    SavedRecipeRead,
)
from app.services.recipes import get_recipe_details, search_recipes
from app.services.user_content import (
    RecipeProvider,
    create_recipe_review,
    delete_recipe_review,
    list_recipe_reviews,
    list_saved_recipes,
    save_recipe,
    unsave_recipe,
    update_recipe_review,
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


@recipes_router.get("/{meal_id}", response_model=RecipeDetails)
async def details(meal_id: Annotated[str, Path(pattern=r"^\d+$")]):
    return await get_recipe_details(meal_id)


@recipes_router.get(
    "/{provider}/{recipe_id}/reviews",
    response_model=RecipeReviewList,
)
async def reviews(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await list_recipe_reviews(session, provider, recipe_id, limit, offset)


@recipes_router.post(
    "/{provider}/{recipe_id}/reviews",
    response_model=RecipeReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    review_input: RecipeReviewCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await create_recipe_review(
        session,
        current_user,
        provider,
        recipe_id,
        review_input,
    )


@recipes_router.put(
    "/{provider}/{recipe_id}/reviews/me",
    response_model=RecipeReviewRead,
)
async def update_review(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    review_input: RecipeReviewCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await update_recipe_review(
        session,
        current_user,
        provider,
        recipe_id,
        review_input,
    )


@recipes_router.delete(
    "/{provider}/{recipe_id}/reviews/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_review(
    provider: RecipeProvider,
    recipe_id: Annotated[str, Path(pattern=r"^\d+$")],
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await delete_recipe_review(session, current_user, provider, recipe_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
