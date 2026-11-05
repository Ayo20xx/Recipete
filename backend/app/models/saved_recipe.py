from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, SQLModel


class SavedRecipe(SQLModel, table=True):
    __tablename__ = "saved_recipe"

    user_id: UUID = Field(
        foreign_key="user.id",
        ondelete="CASCADE",
        primary_key=True,
    )
    provider: str = Field(max_length=32, primary_key=True)
    recipe_id: str = Field(max_length=64, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
