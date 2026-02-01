"""
Decorator utilities for admin authentication and authorization.
"""
from functools import wraps
from aiogram import types
from config import ADMIN_TELEGRAM_IDS, ADMIN_ROLES
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)


def require_admin(handler):
    """
    Decorator to require admin authentication.
    Checks if user's Telegram ID is in the admin whitelist.
    """
    @wraps(handler)
    async def wrapper(event: types.Message | types.CallbackQuery, *args, **kwargs):
        # Get user from event
        user = event.from_user

        # Check if user is in admin whitelist
        if user.id not in ADMIN_TELEGRAM_IDS:
            logger.warning(f"Unauthorized admin access attempt by user {user.id}")
            if isinstance(event, types.Message):
                await event.answer("⛔ У вас нет доступа к админ-панели.")
            else:
                await event.answer("⛔ У вас нет доступа к админ-панели.", show_alert=True)
            return

        # Check if user has active admin role in database
        admin = await AdminUser.get_by_telegram_id(user.id)
        if not admin or not admin.is_active:
            logger.warning(f"Admin user {user.id} is not active in database")
            if isinstance(event, types.Message):
                await event.answer("⛔ Ваш админ-аккаунт не активен.")
            else:
                await event.answer("⛔ Ваш админ-аккаунт не активен.", show_alert=True)
            return

        # Remove admin from kwargs if it exists (added by middleware)
        # to avoid duplicate argument error
        kwargs.pop('admin', None)

        # Pass admin object to handler
        return await handler(event, admin, *args, **kwargs)

    return wrapper


def require_permission(permission: str):
    """
    Decorator to require specific admin permission.
    Must be used together with @require_admin.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(event: types.Message | types.CallbackQuery, admin: AdminUser, *args, **kwargs):
            # Check if admin has the required permission
            if not admin.has_permission(permission):
                logger.warning(
                    f"Admin {admin.user_id} attempted to access {permission} without permission"
                )
                if isinstance(event, types.Message):
                    await event.answer(f"⛔ У вас нет разрешения: {permission}")
                else:
                    await event.answer(f"⛔ У вас нет разрешения: {permission}", show_alert=True)
                return

            return await handler(event, admin, *args, **kwargs)

        return wrapper
    return decorator


async def is_admin(user_id: int) -> bool:
    """
    Check if a user is an admin.
    Returns True if user is in whitelist and has active admin role.
    """
    if user_id not in ADMIN_TELEGRAM_IDS:
        return False

    admin = await AdminUser.get_by_telegram_id(user_id)
    return admin is not None and admin.is_active


async def get_admin_user(telegram_id: int) -> AdminUser | None:
    """
    Get admin user by Telegram ID.
    Returns None if user is not an admin or not active.
    """
    if telegram_id not in ADMIN_TELEGRAM_IDS:
        return None

    admin = await AdminUser.get_by_telegram_id(telegram_id)
    if admin and admin.is_active:
        return admin

    return None
