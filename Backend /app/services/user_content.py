from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.notification import Notification
from app.models.recipe_review import RecipeReview
from app.models.saved_recipe import SavedRecipe
from app.models.user import User
from app.schemas.recipe import (
    NotificationInbox,
    NotificationRead,
    RecipeReviewCreate,
    RecipeReviewList,
    RecipeReviewRead,
    SavedRecipeRead,
)


RecipeProvider = Literal["themealdb"]


async def list_saved_recipes(
    session: AsyncSession,
    user: User,
) -> list[SavedRecipeRead]:
    result = await session.execute(
        select(SavedRecipe)
        .where(SavedRecipe.user_id == user.id)
        .order_by(SavedRecipe.created_at.desc())
    )
    return [SavedRecipeRead.model_validate(item) for item in result.scalars()]


async def save_recipe(
    session: AsyncSession,
    user: User,
    provider: RecipeProvider,
    recipe_id: str,
) -> SavedRecipeRead:
    existing = await session.scalar(
        select(SavedRecipe).where(
            SavedRecipe.user_id == user.id,
            SavedRecipe.provider == provider,
            SavedRecipe.recipe_id == recipe_id,
        )
    )
    if existing is not None:
        return SavedRecipeRead.model_validate(existing)

    saved = SavedRecipe(
        user_id=user.id,
        provider=provider,
        recipe_id=recipe_id,
    )
    session.add(saved)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(
            select(SavedRecipe).where(
                SavedRecipe.user_id == user.id,
                SavedRecipe.provider == provider,
                SavedRecipe.recipe_id == recipe_id,
            )
        )
        if existing is None:
            raise
        saved = existing
    else:
        await session.refresh(saved)
    return SavedRecipeRead.model_validate(saved)


async def unsave_recipe(
    session: AsyncSession,
    user: User,
    provider: RecipeProvider,
    recipe_id: str,
) -> None:
    saved = await session.scalar(
        select(SavedRecipe).where(
            SavedRecipe.user_id == user.id,
            SavedRecipe.provider == provider,
            SavedRecipe.recipe_id == recipe_id,
        )
    )
    if saved is not None:
        await session.delete(saved)
        await session.commit()


async def list_recipe_reviews(
    session: AsyncSession,
    provider: RecipeProvider,
    recipe_id: str,
    limit: int,
    offset: int,
) -> RecipeReviewList:
    conditions = (
        RecipeReview.provider == provider,
        RecipeReview.recipe_id == recipe_id,
    )
    average, count = (
        await session.execute(
            select(func.avg(RecipeReview.rating), func.count(RecipeReview.id))
            .where(*conditions)
        )
    ).one()
    reviews = (
        await session.execute(
            select(RecipeReview)
            .where(*conditions)
            .order_by(RecipeReview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars()
    return RecipeReviewList(
        average_rating=round(float(average), 2) if average is not None else None,
        review_count=count,
        reviews=[RecipeReviewRead.model_validate(review) for review in reviews],
    )


async def create_recipe_review(
    session: AsyncSession,
    user: User,
    provider: RecipeProvider,
    recipe_id: str,
    review_input: RecipeReviewCreate,
) -> RecipeReviewRead:
    existing = await session.scalar(
        select(RecipeReview).where(
            RecipeReview.user_id == user.id,
            RecipeReview.provider == provider,
            RecipeReview.recipe_id == recipe_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this recipe",
        )

    review = RecipeReview(
        user_id=user.id,
        provider=provider,
        recipe_id=recipe_id,
        rating=review_input.rating,
        text=review_input.text,
    )
    session.add(review)
    await session.flush()

    recipients = await session.execute(
        select(SavedRecipe.user_id).where(
            SavedRecipe.provider == provider,
            SavedRecipe.recipe_id == recipe_id,
            SavedRecipe.user_id != user.id,
        )
    )
    session.add_all(
        Notification(
            user_id=recipient_id,
            actor_user_id=user.id,
            review_id=review.id,
            provider=provider,
            recipe_id=recipe_id,
        )
        for recipient_id in recipients.scalars().all()
    )

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await session.scalar(
            select(RecipeReview.id).where(
                RecipeReview.user_id == user.id,
                RecipeReview.provider == provider,
                RecipeReview.recipe_id == recipe_id,
            )
        )
        if existing is None:
            raise
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this recipe",
        )
    await session.refresh(review)
    return RecipeReviewRead.model_validate(review)


async def update_recipe_review(
    session: AsyncSession,
    user: User,
    provider: RecipeProvider,
    recipe_id: str,
    review_input: RecipeReviewCreate,
) -> RecipeReviewRead:
    review = await session.scalar(
        select(RecipeReview).where(
            RecipeReview.user_id == user.id,
            RecipeReview.provider == provider,
            RecipeReview.recipe_id == recipe_id,
        )
    )
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    review.rating = review_input.rating
    review.text = review_input.text
    review.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(review)
    return RecipeReviewRead.model_validate(review)


async def delete_recipe_review(
    session: AsyncSession,
    user: User,
    provider: RecipeProvider,
    recipe_id: str,
) -> None:
    review = await session.scalar(
        select(RecipeReview).where(
            RecipeReview.user_id == user.id,
            RecipeReview.provider == provider,
            RecipeReview.recipe_id == recipe_id,
        )
    )
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    await session.execute(
        delete(Notification).where(Notification.review_id == review.id)
    )
    await session.delete(review)
    await session.commit()


async def list_notifications(
    session: AsyncSession,
    user: User,
) -> NotificationInbox:
    rows = (
        await session.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(20)
        )
    ).scalars()
    unread_count = await session.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
    )
    return NotificationInbox(
        notifications=[
            NotificationRead.model_validate(notification) for notification in rows
        ],
        unread_count=unread_count or 0,
    )


async def mark_notification_read(
    session: AsyncSession,
    user: User,
    notification_id: UUID,
) -> None:
    notification = await session.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    notification.is_read = True
    await session.commit()


async def mark_all_notifications_read(
    session: AsyncSession,
    user: User,
) -> None:
    await session.execute(
        update(Notification)
        .where(
            Notification.user_id == user.id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True)
    )
    await session.commit()
