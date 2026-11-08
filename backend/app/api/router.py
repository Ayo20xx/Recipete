"""Top-level API router."""

from fastapi import APIRouter

from app.api.routers.notifications import notifications_router
from app.api.routers.recipes import recipes_router
from app.api.routers.reviews import reviews_router
from app.api.routers.user import user_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/api/v1")
api_router.include_router(recipes_router, prefix="/api/v1")
api_router.include_router(reviews_router, prefix="/api/v1")
api_router.include_router(notifications_router, prefix="/api/v1")
