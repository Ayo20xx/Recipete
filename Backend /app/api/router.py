"""Top-level API router."""

from fastapi import APIRouter

from app.api.routers.user import user_router

api_router = APIRouter()
api_router.include_router(user_router,prefix="/api/v1")
