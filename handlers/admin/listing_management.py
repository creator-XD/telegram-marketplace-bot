"""
Listing management handlers for admin panel.
"""
from math import ceil
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.models import Listing, User
from database.admin_models import AdminUser, AdminAuditLog
from keyboards.admin_keyboards import (
    get_admin_listings_keyboard,
    get_admin_listing_actions_keyboard,
    get_admin_listing_list_keyboard,
    get_admin_confirm_keyboard,
    get_back_to_admin_keyboard,
)
from utils.decorators import require_admin, require_permission
from utils.admin_helpers import format_admin_listing_text
from utils.helpers import safe_edit_or_answer
from states.states import AdminStates
from config import ADMIN_PAGE_SIZE
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_listings")

# ---------- Filter menu ----------

LISTING_FILTER_MAP = {
    "all": {"status": None, "flagged_only": False},
    "active": {"status": "active", "flagged_only": False},
    "flagged": {"status": None, "flagged_only": True},
    "deleted": {"status": "deleted", "flagged_only": False},
}

FILTER_TITLES = {
    "all": "Все объявления",
    "active": "Активные объявления",
    "flagged": "Отмеченные объявления",
    "deleted": "Удалённые объявления",
}


@router.callback_query(F.data == "admin_listings")
@require_admin
async def admin_listings_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin listings management menu."""
    await safe_edit_or_answer(
        callback,
        "📝 <b>Управление объявлениями</b>\n\nВыберите фильтр:",
        reply_markup=get_admin_listings_keyboard(),
    )
    await callback.answer()


async def _render_listing_list(callback: CallbackQuery, filter_type: str, page: int):
    """Fetch and display a paginated listing list."""
    filt = LISTING_FILTER_MAP.get(filter_type, LISTING_FILTER_MAP["all"])
    title = FILTER_TITLES.get(filter_type, filter_type)

    total = await Listing.count_all_admin(
        status=filt["status"],
        flagged_only=filt["flagged_only"],
    )
    total_pages = max(1, ceil(total / ADMIN_PAGE_SIZE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * ADMIN_PAGE_SIZE

    listings = await Listing.get_all_admin(
        status=filt["status"],
        flagged_only=filt["flagged_only"],
        limit=ADMIN_PAGE_SIZE,
        offset=offset,
    )

    text = f"📝 <b>{title}</b>\nВсего: {total}\n\n"

    if not listings:
        text += "<i>Объявления не найдены.</i>"
        await safe_edit_or_answer(callback, text, reply_markup=get_back_to_admin_keyboard())
        return

    text += "Нажмите на объявление для подробностей:"

    keyboard = get_admin_listing_list_keyboard(listings, page, total_pages, filter_type)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin_listings:"))
@require_admin
async def admin_listings_filter(callback: CallbackQuery, admin: AdminUser):
    """Handle listing list filtering (page 1)."""
    filter_type = callback.data.split(":")[-1]
    if filter_type not in LISTING_FILTER_MAP:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return
    await _render_listing_list(callback, filter_type, page=1)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_listings_pg:"))
@require_admin
async def admin_listings_page(callback: CallbackQuery, admin: AdminUser):
    """Handle listing list pagination."""
    # admin_listings_pg:<filter>:page:<num>
    parts = callback.data.split(":")
    if len(parts) < 4 or parts[2] != "page":
        await callback.answer()
        return
    filter_type = parts[1]
    try:
        page = int(parts[3])
    except (ValueError, IndexError):
        page = 1
    await _render_listing_list(callback, filter_type, page=page)
    await callback.answer()


# ---------- Listing detail ----------

@router.callback_query(F.data.startswith("admin_view_listing:"))
@require_admin
async def admin_view_listing(callback: CallbackQuery, admin: AdminUser):
    """Show detailed view for a single listing."""
    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id, with_user=True)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    text = format_admin_listing_text(listing, user=listing.user, detailed=True)
    keyboard = get_admin_listing_actions_keyboard(
        listing.id,
        is_flagged=bool(listing.flagged),
        status=listing.status,
    )
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- Flag / Unflag ----------

@router.callback_query(F.data.startswith("admin_listing_flag:"))
@require_admin
@require_permission("manage_listings")
async def admin_listing_flag_start(callback: CallbackQuery, admin: AdminUser, state: FSMContext):
    """Ask for a flag reason."""
    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    await state.set_state(AdminStates.flagging_listing)
    await state.update_data(target_listing_id=listing_id)

    await safe_edit_or_answer(
        callback,
        f"🚩 <b>Отметить объявление #{listing.id}</b>\n\n"
        "Введите причину отметки:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.flagging_listing)
@require_admin
async def admin_listing_flag_reason(message: Message, admin: AdminUser, state: FSMContext):
    """Receive flag reason and flag the listing."""
    data = await state.get_data()
    listing_id = data.get("target_listing_id")
    await state.clear()

    if not listing_id:
        await message.answer("Ошибка: объявление не найдено.")
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await message.answer("Объявление не найдено.")
        return

    reason = message.text.strip()

    await listing.update(flagged=1, flag_reason=reason)

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="listing_flag",
        target_type="listing",
        target_id=listing.id,
        details={"reason": reason, "listing_title": listing.title},
    )

    logger.info(f"Admin {admin.user_id} flagged listing {listing.id}: {reason}")

    await message.answer(
        f"🚩 Объявление <b>{listing.title}</b> отмечено.\n"
        f"Причина: {reason}",
        reply_markup=get_back_to_admin_keyboard(),
    )


@router.callback_query(F.data.startswith("admin_listing_unflag:"))
@require_admin
@require_permission("manage_listings")
async def admin_listing_unflag(callback: CallbackQuery, admin: AdminUser):
    """Remove flag from a listing."""
    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    await listing.update(flagged=0, flag_reason=None)

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="listing_unflag",
        target_type="listing",
        target_id=listing.id,
        details={"listing_title": listing.title},
    )

    logger.info(f"Admin {admin.user_id} unflagged listing {listing.id}")

    text = f"✓ Отметка снята с объявления <b>{listing.title}</b>."
    keyboard = get_admin_listing_actions_keyboard(listing.id, is_flagged=False, status=listing.status)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- Delete listing ----------

@router.callback_query(F.data.startswith("admin_listing_delete:"))
@require_admin
@require_permission("delete_any_listing")
async def admin_listing_delete_start(callback: CallbackQuery, admin: AdminUser):
    """Ask for confirmation before deleting a listing."""
    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    text = (
        f"🗑️ <b>Удаление объявления</b>\n\n"
        f"Вы уверены, что хотите удалить "
        f"<b>{listing.title}</b> (ID: {listing.id})?"
    )
    keyboard = get_admin_confirm_keyboard("listing_delete", listing.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm:listing_delete:"))
@require_admin
@require_permission("delete_any_listing")
async def admin_listing_delete_confirm(callback: CallbackQuery, admin: AdminUser):
    """Execute listing deletion."""
    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    title = listing.title
    await listing.delete()

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="listing_delete",
        target_type="listing",
        target_id=listing.id,
        details={"listing_title": title, "seller_id": listing.user_id},
    )

    logger.info(f"Admin {admin.user_id} deleted listing {listing.id}")

    await safe_edit_or_answer(
        callback,
        f"🗑️ Объявление <b>{title}</b> удалено.",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


# ---------- Cancel listing confirmation ----------

@router.callback_query(F.data.startswith("admin_cancel:listing_"))
@require_admin
async def admin_cancel_listing_action(callback: CallbackQuery, admin: AdminUser):
    """Cancel a pending listing confirmation — return to listing detail."""
    parts = callback.data.split(":")
    if len(parts) >= 3:
        try:
            listing_id = int(parts[-1])
        except ValueError:
            listing_id = None

        if listing_id:
            listing = await Listing.get_by_id(listing_id, with_user=True)
            if listing:
                text = format_admin_listing_text(listing, user=listing.user, detailed=True)
                keyboard = get_admin_listing_actions_keyboard(
                    listing.id, is_flagged=bool(listing.flagged), status=listing.status,
                )
                await safe_edit_or_answer(callback, text, reply_markup=keyboard)
                await callback.answer()
                return

    await safe_edit_or_answer(
        callback,
        "Действие отменено.",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()
