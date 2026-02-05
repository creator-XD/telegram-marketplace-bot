"""
Audit log handlers for admin panel.
"""
from math import ceil
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.admin_models import AdminAuditLog, AdminUser
from keyboards.admin_keyboards import (
    get_admin_audit_log_keyboard,
    get_admin_pagination_keyboard,
    get_back_to_admin_keyboard,
)
from utils.decorators import require_admin
from utils.admin_helpers import format_admin_audit_log_text
from utils.helpers import safe_edit_or_answer
from config import ADMIN_PAGE_SIZE
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_audit")

# Maps keyboard filter buttons to database action types
AUDIT_FILTER_MAP = {
    "all": None,
    "block": ["user_block", "user_unblock"],
    "warn": ["user_warn"],
    "delete": ["listing_delete"],
    "edit": ["listing_edit", "listing_flag", "listing_unflag", "profile_edit"],
}

FILTER_LABELS = {
    "all": "Все действия",
    "block": "Блокировки",
    "warn": "Предупреждения",
    "delete": "Удаления",
    "edit": "Редактирования",
}


async def _render_audit_page(
    callback: CallbackQuery,
    filter_type: str,
    page: int,
):
    """Fetch and display a page of audit log entries."""
    actions = AUDIT_FILTER_MAP.get(filter_type)
    label = FILTER_LABELS.get(filter_type, filter_type)

    total = await AdminAuditLog.count(actions=actions)
    total_pages = max(1, ceil(total / ADMIN_PAGE_SIZE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * ADMIN_PAGE_SIZE

    logs = await AdminAuditLog.get_recent(
        actions=actions,
        limit=ADMIN_PAGE_SIZE,
        offset=offset,
    )

    text = f"📋 <b>Журнал действий — {label}</b>\n"
    text += f"Всего записей: {total}\n\n"

    if not logs:
        text += "<i>Записей не найдено.</i>"
        await safe_edit_or_answer(
            callback,
            text,
            reply_markup=get_back_to_admin_keyboard(),
        )
        return

    for log in logs:
        text += format_admin_audit_log_text(log) + "\n\n"

    if total_pages > 1:
        keyboard = get_admin_pagination_keyboard(
            prefix=f"admin_audit_pg:{filter_type}",
            current_page=page,
            total_pages=total_pages,
            back_callback="admin_audit_log",
        )
    else:
        keyboard = get_back_to_admin_keyboard()

    await safe_edit_or_answer(callback, text, reply_markup=keyboard)


@router.callback_query(F.data == "admin_audit_log")
@require_admin
async def admin_audit_log_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin audit log menu."""
    await safe_edit_or_answer(
        callback,
        "📋 <b>Журнал действий администраторов</b>\n\n"
        "Выберите фильтр:",
        reply_markup=get_admin_audit_log_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_audit:"))
@require_admin
async def admin_audit_log_filter(callback: CallbackQuery, admin: AdminUser):
    """Show filtered audit log (page 1)."""
    filter_type = callback.data.split(":")[-1]

    if filter_type not in AUDIT_FILTER_MAP:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return

    await _render_audit_page(callback, filter_type, page=1)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_audit_pg:"))
@require_admin
async def admin_audit_log_page(callback: CallbackQuery, admin: AdminUser):
    """Handle audit log pagination."""
    # Callback format: admin_audit_pg:<filter>:page:<num>
    parts = callback.data.split(":")
    if len(parts) < 4 or parts[2] != "page":
        await callback.answer()
        return

    filter_type = parts[1]
    try:
        page = int(parts[3])
    except (ValueError, IndexError):
        page = 1

    if filter_type not in AUDIT_FILTER_MAP:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return

    await _render_audit_page(callback, filter_type, page=page)
    await callback.answer()
