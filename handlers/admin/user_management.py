"""
User management handlers for admin panel.
"""
from math import ceil
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.models import User
from database.admin_models import AdminUser, AdminAuditLog, UserWarning
from keyboards.admin_keyboards import (
    get_admin_users_keyboard,
    get_admin_user_actions_keyboard,
    get_admin_user_list_keyboard,
    get_admin_confirm_keyboard,
    get_admin_warning_severity_keyboard,
    get_back_to_admin_keyboard,
)
from utils.decorators import require_admin, require_permission
from utils.admin_helpers import format_admin_user_text, format_admin_warning_text
from utils.helpers import safe_edit_or_answer
from states.states import AdminStates
from config import ADMIN_PAGE_SIZE
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_users")

# ---------- Filter menu ----------

USER_FILTER_MAP = {
    "all": None,
    "active": "active",
    "blocked": "blocked",
    "verified": "verified",
}

FILTER_TITLES = {
    "all": "Все пользователи",
    "active": "Активные пользователи",
    "blocked": "Заблокированные пользователи",
    "verified": "Верифицированные пользователи",
}


@router.callback_query(F.data == "admin_users")
@require_admin
async def admin_users_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin users management menu."""
    await safe_edit_or_answer(
        callback,
        "👥 <b>Управление пользователями</b>\n\nВыберите фильтр:",
        reply_markup=get_admin_users_keyboard(),
    )
    await callback.answer()


async def _render_user_list(callback: CallbackQuery, filter_type: str, page: int):
    """Fetch and display a paginated user list."""
    status = USER_FILTER_MAP.get(filter_type)
    title = FILTER_TITLES.get(filter_type, filter_type)

    total = await User.count_all(status=status)
    total_pages = max(1, ceil(total / ADMIN_PAGE_SIZE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * ADMIN_PAGE_SIZE

    users = await User.get_all(status=status, limit=ADMIN_PAGE_SIZE, offset=offset)

    text = f"👥 <b>{title}</b>\nВсего: {total}\n\n"

    if not users:
        text += "<i>Пользователи не найдены.</i>"
        await safe_edit_or_answer(callback, text, reply_markup=get_back_to_admin_keyboard())
        return

    text += "Нажмите на пользователя для подробностей:"

    keyboard = get_admin_user_list_keyboard(users, page, total_pages, filter_type)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin_users:"))
@require_admin
async def admin_users_filter(callback: CallbackQuery, admin: AdminUser):
    """Handle user list filtering (page 1)."""
    filter_type = callback.data.split(":")[-1]
    if filter_type not in USER_FILTER_MAP:
        await callback.answer("Неизвестный фильтр", show_alert=True)
        return
    await _render_user_list(callback, filter_type, page=1)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_users_pg:"))
@require_admin
async def admin_users_page(callback: CallbackQuery, admin: AdminUser):
    """Handle user list pagination."""
    # admin_users_pg:<filter>:page:<num>
    parts = callback.data.split(":")
    if len(parts) < 4 or parts[2] != "page":
        await callback.answer()
        return
    filter_type = parts[1]
    try:
        page = int(parts[3])
    except (ValueError, IndexError):
        page = 1
    await _render_user_list(callback, filter_type, page=page)
    await callback.answer()


# ---------- User detail ----------

@router.callback_query(F.data.startswith("admin_view_user:"))
@require_admin
async def admin_view_user(callback: CallbackQuery, admin: AdminUser):
    """Show detailed view for a single user."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = format_admin_user_text(user, detailed=True)
    keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=not user.is_active)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_user_from_listing:"))
@require_admin
async def admin_view_user_from_listing(callback: CallbackQuery, admin: AdminUser):
    """View listing seller from listing detail."""
    from database.models import Listing

    try:
        listing_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return

    user = await User.get_by_id(listing.user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = format_admin_user_text(user, detailed=True)
    keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=not user.is_active)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- User listings ----------

@router.callback_query(F.data.startswith("admin_user_listings:"))
@require_admin
async def admin_user_listings(callback: CallbackQuery, admin: AdminUser):
    """Show listings belonging to a user."""
    from database.models import Listing

    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    listings = await Listing.get_by_user(user_id)

    text = f"📝 <b>Объявления пользователя {user.display_name}</b>\n\n"
    if not listings:
        text += "<i>Нет объявлений.</i>"
    else:
        for lst in listings[:10]:
            status_icon = {"active": "🟢", "sold": "✅", "reserved": "🔒", "deleted": "🗑️"}.get(lst.status, "")
            text += f"{status_icon} {lst.title} (ID:{lst.id})\n"
        if len(listings) > 10:
            text += f"\n<i>... и ещё {len(listings) - 10}</i>"

    keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=not user.is_active)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- Block / Unblock ----------

@router.callback_query(F.data.startswith("admin_user_block:"))
@require_admin
@require_permission("block_users")
async def admin_user_block_start(callback: CallbackQuery, admin: AdminUser):
    """Ask for confirmation before blocking a user."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = (
        f"🚫 <b>Блокировка пользователя</b>\n\n"
        f"Вы уверены, что хотите заблокировать "
        f"<b>{user.display_name}</b> (ID: {user.id})?"
    )
    keyboard = get_admin_confirm_keyboard("user_block", user.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm:user_block:"))
@require_admin
@require_permission("block_users")
async def admin_user_block_confirm(callback: CallbackQuery, admin: AdminUser, state: FSMContext):
    """Confirmed — ask for block reason."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    await state.set_state(AdminStates.blocking_user)
    await state.update_data(target_user_id=user_id)

    await safe_edit_or_answer(
        callback,
        "📝 Введите причину блокировки:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.blocking_user)
@require_admin
async def admin_user_block_reason(message: Message, admin: AdminUser, state: FSMContext):
    """Receive block reason and execute the block."""
    data = await state.get_data()
    user_id = data.get("target_user_id")
    await state.clear()

    if not user_id:
        await message.answer("Ошибка: пользователь не найден.")
        return

    user = await User.get_by_id(user_id)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    reason = message.text.strip()

    await user.update(is_active=False, suspension_reason=reason)

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="user_block",
        target_type="user",
        target_id=user.id,
        details={"reason": reason, "user_name": user.display_name},
    )

    logger.info(f"Admin {admin.user_id} blocked user {user.id}: {reason}")

    await message.answer(
        f"🚫 Пользователь <b>{user.display_name}</b> заблокирован.\n"
        f"Причина: {reason}",
        reply_markup=get_back_to_admin_keyboard(),
    )


@router.callback_query(F.data.startswith("admin_user_unblock:"))
@require_admin
@require_permission("block_users")
async def admin_user_unblock_start(callback: CallbackQuery, admin: AdminUser):
    """Ask for confirmation before unblocking a user."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = (
        f"✅ <b>Разблокировка пользователя</b>\n\n"
        f"Разблокировать <b>{user.display_name}</b> (ID: {user.id})?"
    )
    keyboard = get_admin_confirm_keyboard("user_unblock", user.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm:user_unblock:"))
@require_admin
@require_permission("block_users")
async def admin_user_unblock_confirm(callback: CallbackQuery, admin: AdminUser):
    """Execute unblock immediately."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    await user.update(is_active=True, suspension_reason=None)

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="user_unblock",
        target_type="user",
        target_id=user.id,
        details={"user_name": user.display_name},
    )

    logger.info(f"Admin {admin.user_id} unblocked user {user.id}")

    text = f"✅ Пользователь <b>{user.display_name}</b> разблокирован."
    keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=False)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- Cancel confirmation ----------

@router.callback_query(F.data.startswith("admin_cancel:user_"))
@require_admin
async def admin_cancel_user_action(callback: CallbackQuery, admin: AdminUser):
    """Cancel a pending user confirmation — return to user detail."""
    # admin_cancel:user_<action>:<target_id>
    parts = callback.data.split(":")
    if len(parts) >= 3:
        try:
            target_id = int(parts[-1])
        except ValueError:
            target_id = None

        if target_id:
            user = await User.get_by_id(target_id)
            if user:
                text = format_admin_user_text(user, detailed=True)
                keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=not user.is_active)
                await safe_edit_or_answer(callback, text, reply_markup=keyboard)
                await callback.answer()
                return

    await safe_edit_or_answer(
        callback,
        "Действие отменено.",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


# ---------- Warn user ----------

@router.callback_query(F.data.startswith("admin_user_warn:"))
@require_admin
@require_permission("warn_users")
async def admin_user_warn_start(callback: CallbackQuery, admin: AdminUser):
    """Show severity selection for a warning."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    text = (
        f"⚠️ <b>Предупреждение для {user.display_name}</b>\n\n"
        "Выберите уровень серьёзности:"
    )
    keyboard = get_admin_warning_severity_keyboard(user.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_warn_severity:"))
@require_admin
@require_permission("warn_users")
async def admin_user_warn_severity(callback: CallbackQuery, admin: AdminUser, state: FSMContext):
    """Severity selected — ask for reason text."""
    # admin_warn_severity:<user_id>:<severity>
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer()
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await callback.answer("Неверный ID", show_alert=True)
        return

    severity = parts[2]
    if severity not in ("low", "medium", "high"):
        await callback.answer("Неверный уровень", show_alert=True)
        return

    await state.set_state(AdminStates.warning_user)
    await state.update_data(target_user_id=user_id, severity=severity)

    severity_label = {"low": "Низкая", "medium": "Средняя", "high": "Высокая"}[severity]
    await safe_edit_or_answer(
        callback,
        f"⚠️ Уровень: <b>{severity_label}</b>\n\n"
        "Введите причину предупреждения:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


@router.message(AdminStates.warning_user)
@require_admin
async def admin_user_warn_reason(message: Message, admin: AdminUser, state: FSMContext):
    """Receive warning reason and create the warning."""
    data = await state.get_data()
    user_id = data.get("target_user_id")
    severity = data.get("severity", "low")
    await state.clear()

    if not user_id:
        await message.answer("Ошибка: пользователь не найден.")
        return

    user = await User.get_by_id(user_id)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    reason = message.text.strip()

    warning = await UserWarning.create(
        user_id=user.id,
        admin_id=admin.user_id,
        reason=reason,
        severity=severity,
    )

    await AdminAuditLog.create(
        admin_id=admin.user_id,
        action="user_warn",
        target_type="user",
        target_id=user.id,
        details={
            "reason": reason,
            "severity": severity,
            "warning_id": warning.id,
            "user_name": user.display_name,
        },
    )

    logger.info(f"Admin {admin.user_id} warned user {user.id} ({severity}): {reason}")

    severity_label = {"low": "Низкая", "medium": "Средняя", "high": "Высокая"}[severity]
    await message.answer(
        f"⚠️ Предупреждение выдано пользователю <b>{user.display_name}</b>\n"
        f"Уровень: {severity_label}\n"
        f"Причина: {reason}",
        reply_markup=get_back_to_admin_keyboard(),
    )


# ---------- Warning history ----------

@router.callback_query(F.data.startswith("admin_user_warnings:"))
@require_admin
async def admin_user_warnings(callback: CallbackQuery, admin: AdminUser):
    """Show warning history for a user."""
    try:
        user_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    user = await User.get_by_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    warnings = await UserWarning.get_by_user_id(user.id, active_only=False)

    text = f"⚠️ <b>История предупреждений — {user.display_name}</b>\n\n"
    if not warnings:
        text += "<i>Предупреждений нет.</i>"
    else:
        for w in warnings[:10]:
            text += format_admin_warning_text(w) + "\n\n"
        if len(warnings) > 10:
            text += f"<i>... и ещё {len(warnings) - 10}</i>"

    keyboard = get_admin_user_actions_keyboard(user.id, is_blocked=not user.is_active)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()
