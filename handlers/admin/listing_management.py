"""
Listing management handlers for admin panel.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import Listing
from keyboards.admin_keyboards import get_admin_listings_keyboard, get_back_to_admin_keyboard
from utils.decorators import require_admin
from utils.helpers import safe_edit_or_answer
from database.admin_models import AdminUser
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_listings")


@router.callback_query(F.data == "admin_listings")
@require_admin
async def admin_listings_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin listings management menu."""
    await safe_edit_or_answer(callback,
        "📝 <b>Управление объявлениями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_listings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_listings:"))
@require_admin
async def admin_listings_filter(callback: CallbackQuery, admin: AdminUser):
    """Handle listing filtering."""
    filter_type = callback.data.split(":")[-1]

    # Get listings based on filter using available methods
    if filter_type == "all":
        listings = await Listing.get_all_admin(limit=100)
        title = "Все объявления"
    elif filter_type == "active":
        listings = await Listing.search(status="active", limit=100)
        title = "Активные объявления"
    elif filter_type == "flagged":
        listings = []  # Placeholder - flagged listings not implemented yet
        title = "Отмеченные объявления"
    elif filter_type == "deleted":
        listings = await Listing.search(status="deleted", limit=100)
        title = "Удаленные объявления"
    else:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return

    if not listings:
        await safe_edit_or_answer(callback,
            f"📝 <b>{title}</b>\n\n"
            "Объявления не найдены.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await callback.answer()
        return

    text = f"📝 <b>{title}</b> ({len(listings)})\n\n"
    for listing in listings[:10]:  # Show first 10
        text += f"• {listing.title} (ID: {listing.id})\n"

    if len(listings) > 10:
        text += f"\n<i>... и еще {len(listings) - 10}</i>"

    await safe_edit_or_answer(callback,
        text,
        reply_markup=get_back_to_admin_keyboard()
    )
    await callback.answer()
