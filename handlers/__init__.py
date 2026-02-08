"""
Handlers module for the Telegram Marketplace Bot.
"""
from aiogram import Router

from .common import router as common_router
from .listings import router as listings_router
from .search import router as search_router
from .messages import router as messages_router
from .reviews import router as reviews_router
from .profile import router as profile_router
from .admin import admin_router


def get_all_routers() -> list[Router]:
    """Get all routers for registration."""
    return [
        admin_router,  # Admin router first for priority
        listings_router,
        search_router,
        messages_router,
        reviews_router,
        profile_router,
        common_router,
    ]


__all__ = [
    "get_all_routers",
    "admin_router",
    "common_router",
    "listings_router",
    "search_router",
    "messages_router",
    "reviews_router",
    "profile_router",
]
