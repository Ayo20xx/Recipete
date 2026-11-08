from typing import Annotated

from fastapi import APIRouter, Path, Query, Response, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.recipe import (
    RecipeReviewCreate,
    RecipeReviewList,
    RecipeReviewRead,
)
from app.services.user_content import (
    RecipeProvider,
    create_recipe_review,
    delete_recipe_review,
    list_recipe_reviews,
    update_recipe_review,
)

reviews_router = APIRouter(tags=["reviews"])


@reviews_router.get(
    "/recipes/{provider}/{recipe_id}/reviews",
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


@reviews_router.post(
    "/recipes/{provider}/{recipe_id}/reviews",
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


@reviews_router.put(
    "/recipes/{provider}/{recipe_id}/reviews/me",
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


@reviews_router.delete(
    "/recipes/{provider}/{recipe_id}/reviews/me",
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
