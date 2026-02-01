"""
Helper utility functions for admin panel.
"""
from datetime import datetime
from typing import Optional
from database.models import User, Listing
from database.admin_models import UserWarning, AdminAuditLog
from utils.helpers import escape_html, format_price, get_category_name


def format_admin_user_text(user: User, detailed: bool = True) -> str:
    """
    Format user information for admin view.

    Args:
        user: The user to format
        detailed: Whether to show full details

    Returns:
        Formatted HTML string
    """
    if detailed:
        text = f"""
👤 <b>Пользователь #{user.id}</b>

<b>Имя:</b> {escape_html(user.display_name)}
<b>Telegram ID:</b> <code>{user.telegram_id}</code>
"""
        if user.username:
            text += f"<b>Username:</b> @{escape_html(user.username)}\n"

        if user.phone:
            text += f"<b>Телефон:</b> {escape_html(user.phone)}\n"

        if user.location:
            text += f"<b>Местоположение:</b> {escape_html(user.location)}\n"

        status_emoji = "✅" if user.is_active else "🚫"
        status_text = "Активен" if user.is_active else "Заблокирован"
        text += f"\n<b>Статус:</b> {status_emoji} {status_text}\n"

        if not user.is_active and user.suspension_reason:
            text += f"<b>Причина блокировки:</b> {escape_html(user.suspension_reason)}\n"

        if user.is_verified:
            text += "✓ <b>Верифицирован</b>\n"

        if user.rating > 0:
            text += f"⭐ <b>Рейтинг:</b> {user.rating:.1f} ({user.rating_count})\n"

        if user.warning_count > 0:
            text += f"⚠️ <b>Предупреждения:</b> {user.warning_count}\n"

        text += f"\n<b>Зарегистрирован:</b> {format_datetime(user.created_at)}"

    else:
        # Short format for lists
        status = "🚫" if not user.is_active else ("✓" if user.is_verified else "")
        warn = f"⚠️{user.warning_count}" if user.warning_count > 0 else ""
        text = f"{status} <b>{escape_html(user.display_name)}</b> (ID: {user.id}) {warn}"

    return text


def format_admin_listing_text(listing: Listing, user: Optional[User] = None, detailed: bool = True) -> str:
    """
    Format listing information for admin view.

    Args:
        listing: The listing to format
        user: Optional seller user object
        detailed: Whether to show full details

    Returns:
        Formatted HTML string
    """
    if detailed:
        text = f"""
📝 <b>Объявление #{listing.id}</b>

<b>Название:</b> {escape_html(listing.title)}
<b>Цена:</b> {format_price(listing.price)}
<b>Категория:</b> {get_category_name(listing.category)}
"""

        if listing.location:
            text += f"<b>Местоположение:</b> {escape_html(listing.location)}\n"

        text += f"\n<b>Описание:</b>\n{escape_html(listing.description or 'Нет описания')}\n"

        # Status
        status_map = {
            "active": ("🟢", "Активно"),
            "sold": ("✅", "Продано"),
            "reserved": ("🔒", "Зарезервировано"),
            "deleted": ("🗑️", "Удалено"),
        }
        emoji, status_text = status_map.get(listing.status, ("", listing.status))
        text += f"\n<b>Статус:</b> {emoji} {status_text}\n"

        # Flagged
        if listing.flagged:
            text += f"🚩 <b>ОТМЕЧЕНО</b>\n"
            if listing.flag_reason:
                text += f"<b>Причина:</b> {escape_html(listing.flag_reason)}\n"

        # Stats
        text += f"<b>Просмотров:</b> {listing.views}\n"

        # Seller
        if user:
            text += f"\n<b>Продавец:</b> {escape_html(user.display_name)} (ID: {user.id})\n"
        else:
            text += f"\n<b>Продавец ID:</b> {listing.user_id}\n"

        text += f"<b>Создано:</b> {format_datetime(listing.created_at)}"

    else:
        # Short format for lists
        status_icon = "🚩" if listing.flagged else ("🗑️" if listing.status == "deleted" else "")
        text = f"{status_icon} <b>{escape_html(listing.title[:40])}</b> - {format_price(listing.price)} (ID: {listing.id})"

    return text


def format_admin_warning_text(warning: UserWarning) -> str:
    """Format warning for admin view."""
    severity_map = {
        "low": ("⚠️", "Низкая"),
        "medium": ("⚠️⚠️", "Средняя"),
        "high": ("⚠️⚠️⚠️", "Высокая"),
    }
    emoji, severity_text = severity_map.get(warning.severity, ("⚠️", warning.severity))

    text = f"""
{emoji} <b>Предупреждение #{warning.id}</b>

<b>Уровень:</b> {severity_text}
<b>Причина:</b> {escape_html(warning.reason)}
<b>Статус:</b> {"🟢 Активно" if warning.is_active else "⚫ Снято"}
"""

    if warning.admin_user:
        text += f"<b>Выдал:</b> {escape_html(warning.admin_user.display_name)}\n"

    text += f"<b>Дата:</b> {format_datetime(warning.created_at)}"

    if warning.expires_at:
        text += f"\n<b>Истекает:</b> {format_datetime(warning.expires_at)}"

    return text


def format_admin_audit_log_text(log: AdminAuditLog) -> str:
    """Format audit log entry for admin view."""
    action_icons = {
        "user_block": "🚫",
        "user_unblock": "✅",
        "user_warn": "⚠️",
        "listing_flag": "🚩",
        "listing_unflag": "✓",
        "listing_edit": "✏️",
        "listing_delete": "🗑️",
        "profile_edit": "👤",
    }

    icon = action_icons.get(log.action, "📝")

    text = f"{icon} <b>{log.action.replace('_', ' ').title()}</b>\n"

    if log.admin_user:
        text += f"👤 {escape_html(log.admin_user.display_name)}\n"

    if log.target_type and log.target_id:
        text += f"🎯 {log.target_type.title()} #{log.target_id}\n"

    # Add details
    if log.details:
        if "reason" in log.details:
            text += f"📝 {escape_html(log.details['reason'])}\n"

    text += f"🕐 {format_datetime(log.created_at)}"

    return text


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if dt is None:
        return "N/A"

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except Exception:
            return dt

    return dt.strftime("%d.%m.%Y %H:%M")


def format_admin_dashboard(stats: dict) -> str:
    """
    Format admin dashboard statistics.

    Args:
        stats: Dictionary with user_stats, listing_stats, transaction_stats

    Returns:
        Formatted HTML string
    """
    user_stats = stats.get("user_stats", {})
    listing_stats = stats.get("listing_stats", {})
    transaction_stats = stats.get("transaction_stats", {})

    text = """
📊 <b>Админ-панель - Главная</b>

<b>👥 Пользователи:</b>
• Всего: {total_users}
• Активных: {active_users}
• Заблокированных: {blocked_users}
• Верифицированных: {verified_users}
• Новых сегодня: {new_users_today}
• Новых за неделю: {new_users_week}

<b>📝 Объявления:</b>
• Всего: {total_listings}
• Активных: {active_listings}
• Продано: {sold_listings}
• Отмечено флагами: {flagged_listings}
• Новых сегодня: {new_listings_today}
• Новых за неделю: {new_listings_week}

<b>💳 Транзакции:</b>
• Всего: {total_transactions}
• Ожидают: {pending_transactions}
• Завершено: {completed_transactions}
""".format(
        total_users=user_stats.get("total", 0),
        active_users=user_stats.get("active", 0),
        blocked_users=user_stats.get("blocked", 0),
        verified_users=user_stats.get("verified", 0),
        new_users_today=user_stats.get("new_today", 0),
        new_users_week=user_stats.get("new_week", 0),
        total_listings=listing_stats.get("total", 0),
        active_listings=listing_stats.get("active", 0),
        sold_listings=listing_stats.get("sold", 0),
        flagged_listings=listing_stats.get("flagged", 0),
        new_listings_today=listing_stats.get("new_today", 0),
        new_listings_week=listing_stats.get("new_week", 0),
        total_transactions=transaction_stats.get("total", 0),
        pending_transactions=transaction_stats.get("pending", 0),
        completed_transactions=transaction_stats.get("completed", 0),
    )

    return text
