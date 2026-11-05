from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SavedRecipeRead(BaseModel):
    provider: str
    recipe_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    text: str | None = Field(default=None, max_length=1000)


class RecipeReviewRead(BaseModel):
    id: UUID
    user_id: UUID
    provider: str
    recipe_id: str
    rating: int
    text: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeReviewList(BaseModel):
    average_rating: float | None
    review_count: int
    reviews: list[RecipeReviewRead]


class NotificationRead(BaseModel):
    id: UUID
    actor_user_id: UUID | None
    review_id: UUID
    provider: str
    recipe_id: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationInbox(BaseModel):
    notifications: list[NotificationRead]
    unread_count: int


class RecipeSummary(BaseModel):
    id: str
    name: str
    image_url: str | None


class RecipeIngredient(BaseModel):
    name: str
    measure: str


class RecipeDetails(RecipeSummary):
    category: str | None
    area: str | None
    instructions: str | None
    source_url: str | None
    ingredients: list[RecipeIngredient]
