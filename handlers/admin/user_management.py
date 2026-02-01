"""
User management handlers for admin panel.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import User
from keyboards.admin_keyboards import get_admin_users_keyboard, get_back_to_admin_keyboard
from utils.decorators import require_admin
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_users")


@router.callback_query(F.data == "admin_users")
@require_admin
async def admin_users_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin users management menu."""
    await callback.message.edit_text(
        "👥 <b>Управление пользователями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_users_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users:"))
@require_admin
async def admin_users_filter(callback: CallbackQuery, admin: AdminUser):
    """Handle user filtering."""
    filter_type = callback.data.split(":")[-1]

    # Get users - using available methods
    users = await User.get_all(limit=100)

    if filter_type == "all":
        title = "Все пользователи"
    elif filter_type == "active":
        title = "Активные пользователи (все пользователи)"
    elif filter_type == "blocked":
        users = []  # Placeholder - blocked users filtering not implemented yet
        title = "Заблокированные пользователи"
    elif filter_type == "verified":
        users = []  # Placeholder - verified users filtering not implemented yet
        title = "Верифицированные пользователи"
    else:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return

    if not users:
        await callback.message.edit_text(
            f"👥 <b>{title}</b>\n\n"
            "Пользователи не найдены.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await callback.answer()
        return

    text = f"👥 <b>{title}</b> ({len(users)})\n\n"
    for user in users[:10]:  # Show first 10
        text += f"• {user.display_name} (ID: {user.telegram_id})\n"

    if len(users) > 10:
        text += f"\n<i>... и еще {len(users) - 10}</i>"

    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_admin_keyboard()
    )
    await callback.answer()
