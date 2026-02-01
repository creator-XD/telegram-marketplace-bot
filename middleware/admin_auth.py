"""
Admin authentication middleware.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import ADMIN_TELEGRAM_IDS
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)


class AdminAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate admin users.
    Adds admin object to handler data if user is an admin.
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check if user is admin and add admin object to handler data.
        Only adds admin/is_admin to data dict if user is actually an admin.
        """
        user = event.from_user

        # Check if user is in admin whitelist
        if user.id in ADMIN_TELEGRAM_IDS:
            # Get admin from database
            admin = await AdminUser.get_by_telegram_id(user.id)
            if admin and admin.is_active:
                # Only add to data if user is an active admin
                data["admin"] = admin
                data["is_admin"] = True

        # Call the handler
        return await handler(event, data)
