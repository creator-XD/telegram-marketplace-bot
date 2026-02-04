"""
Audit log handlers for admin panel.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.admin_models import AdminAuditLog, AdminUser
from keyboards.admin_keyboards import get_admin_audit_log_keyboard, get_back_to_admin_keyboard
from utils.decorators import require_admin
from utils.helpers import safe_edit_or_answer
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_audit")


@router.callback_query(F.data == "admin_audit_log")
@require_admin
async def admin_audit_log_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin audit log menu."""
    await safe_edit_or_answer(callback,
        "📋 <b>Журнал действий администраторов</b>\n\n"
        "Выберите фильтр:",
        reply_markup=get_admin_audit_log_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_audit:"))
@require_admin
async def admin_audit_log_filter(callback: CallbackQuery, admin: AdminUser):
    """Show filtered audit log."""
    filter_type = callback.data.split(":")[-1]

    # Placeholder - audit log functionality not fully implemented yet
    text = f"📋 <b>Журнал аудита</b>\n\n"
    text += "Функционал журнала аудита находится в разработке.\n\n"
    text += f"Выбран фильтр: {filter_type}"

    await safe_edit_or_answer(callback,
        text,
        reply_markup=get_back_to_admin_keyboard()
    )
    await callback.answer()
