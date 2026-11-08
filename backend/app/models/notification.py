from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Notification(SQLModel, table=True):
    __tablename__ = "notification"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "review_id",
            name="uq_notification_user_review",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    actor_user_id: UUID | None = Field(
        default=None,
        foreign_key="user.id",
        ondelete="SET NULL",
    )
    review_id: UUID | None = Field(
        default=None,
        foreign_key="recipe_review.id",
        ondelete="CASCADE",
    )
    provider: str | None = Field(default=None, max_length=32)
    recipe_id: str | None = Field(default=None, max_length=64)
    title: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=1000)
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
