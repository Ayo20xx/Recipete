from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class RecipeReview(SQLModel, table=True):
    __tablename__ = "recipe_review"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider",
            "recipe_id",
            name="uq_recipe_review_user_provider_recipe",
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_recipe_review_rating"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    provider: str = Field(max_length=32)
    recipe_id: str = Field(max_length=64)
    rating: int
    text: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
