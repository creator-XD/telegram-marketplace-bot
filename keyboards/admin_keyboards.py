"""
Keyboard builders for admin panel.
"""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get admin main menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📊 Панель управления", callback_data="admin_dashboard")
    builder.button(text="👥 Пользователи", callback_data="admin_users")
    builder.button(text="📝 Объявления", callback_data="admin_listings")
    builder.button(text="💳 Транзакции", callback_data="admin_transactions")
    builder.button(text="📈 Аналитика", callback_data="admin_analytics")
    builder.button(text="⭐ Отзывы", callback_data="admin_reviews")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.button(text="📋 Журнал действий", callback_data="admin_audit_log")

    builder.adjust(2, 2, 2, 2)

    return builder.as_markup()


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Get admin users management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Все пользователи", callback_data="admin_users:all")
    builder.button(text="✅ Активные", callback_data="admin_users:active")
    builder.button(text="🚫 Заблокированные", callback_data="admin_users:blocked")
    builder.button(text="✓ Верифицированные", callback_data="admin_users:verified")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(2, 2, 1)

    return builder.as_markup()


def get_admin_user_actions_keyboard(user_id: int, is_blocked: bool = False) -> InlineKeyboardMarkup:
    """Get actions keyboard for specific user."""
    builder = InlineKeyboardBuilder()

    if is_blocked:
        builder.button(text="✅ Разблокировать", callback_data=f"admin_user_unblock:{user_id}")
    else:
        builder.button(text="🚫 Заблокировать", callback_data=f"admin_user_block:{user_id}")

    builder.button(text="⚠️ Предупредить", callback_data=f"admin_user_warn:{user_id}")
    builder.button(text="📝 Объявления", callback_data=f"admin_user_listings:{user_id}")
    builder.button(text="⚠️ История предупреждений", callback_data=f"admin_user_warnings:{user_id}")
    builder.button(text="« Назад", callback_data="admin_users:all")

    builder.adjust(2, 2, 1, 1)

    return builder.as_markup()


def get_admin_listings_keyboard() -> InlineKeyboardMarkup:
    """Get admin listings management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Все объявления", callback_data="admin_listings:all")
    builder.button(text="🟢 Активные", callback_data="admin_listings:active")
    builder.button(text="🚩 Отмеченные", callback_data="admin_listings:flagged")
    builder.button(text="🗑️ Удаленные", callback_data="admin_listings:deleted")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(2, 2, 1)

    return builder.as_markup()


def get_admin_listing_actions_keyboard(listing_id: int, is_flagged: bool = False, status: str = "active") -> InlineKeyboardMarkup:
    """Get actions keyboard for specific listing."""
    builder = InlineKeyboardBuilder()

    if status == "active":
        if is_flagged:
            builder.button(text="✓ Снять отметку", callback_data=f"admin_listing_unflag:{listing_id}")
        else:
            builder.button(text="🚩 Отметить", callback_data=f"admin_listing_flag:{listing_id}")

    builder.button(text="✏️ Редактировать", callback_data=f"admin_listing_edit:{listing_id}")

    if status != "deleted":
        builder.button(text="🗑️ Удалить", callback_data=f"admin_listing_delete:{listing_id}")

    builder.button(text="👤 Продавец", callback_data=f"admin_view_user_from_listing:{listing_id}")
    builder.button(text="« Назад", callback_data="admin_listings:all")

    builder.adjust(2, 1, 1, 1)

    return builder.as_markup()


def get_admin_transactions_keyboard() -> InlineKeyboardMarkup:
    """Get admin transactions management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Все транзакции", callback_data="admin_transactions:all")
    builder.button(text="⏳ Ожидают", callback_data="admin_transactions:pending")
    builder.button(text="✅ Завершены", callback_data="admin_transactions:completed")
    builder.button(text="❌ Отменены", callback_data="admin_transactions:cancelled")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(2, 2, 1)

    return builder.as_markup()


def get_admin_analytics_keyboard() -> InlineKeyboardMarkup:
    """Get admin analytics keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="👥 Статистика пользователей", callback_data="admin_analytics:users")
    builder.button(text="📝 Статистика объявлений", callback_data="admin_analytics:listings")
    builder.button(text="💳 Статистика транзакций", callback_data="admin_analytics:transactions")
    builder.button(text="📊 Общая статистика", callback_data="admin_dashboard")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(2, 2, 1)

    return builder.as_markup()


def get_admin_audit_log_keyboard() -> InlineKeyboardMarkup:
    """Get admin audit log keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Все действия", callback_data="admin_audit:all")
    builder.button(text="🚫 Блокировки", callback_data="admin_audit:block")
    builder.button(text="⚠️ Предупреждения", callback_data="admin_audit:warn")
    builder.button(text="🗑️ Удаления", callback_data="admin_audit:delete")
    builder.button(text="✏️ Редактирования", callback_data="admin_audit:edit")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(2, 2, 1, 1)

    return builder.as_markup()


def get_admin_confirm_keyboard(action: str, target_id: int, confirm_text: str = "Подтвердить", cancel_text: str = "Отмена") -> InlineKeyboardMarkup:
    """Get confirmation keyboard for destructive actions."""
    builder = InlineKeyboardBuilder()

    builder.button(text=f"✅ {confirm_text}", callback_data=f"admin_confirm:{action}:{target_id}")
    builder.button(text=f"❌ {cancel_text}", callback_data=f"admin_cancel:{action}:{target_id}")

    builder.adjust(2)

    return builder.as_markup()


def get_admin_warning_severity_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get warning severity selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="⚠️ Низкая", callback_data=f"admin_warn_severity:{user_id}:low")
    builder.button(text="⚠️⚠️ Средняя", callback_data=f"admin_warn_severity:{user_id}:medium")
    builder.button(text="⚠️⚠️⚠️ Высокая", callback_data=f"admin_warn_severity:{user_id}:high")
    builder.button(text="❌ Отмена", callback_data="admin_users:all")

    builder.adjust(3, 1)

    return builder.as_markup()


def get_admin_pagination_keyboard(
    prefix: str,
    current_page: int,
    total_pages: int,
    back_callback: str = "admin_menu"
) -> InlineKeyboardMarkup:
    """Get pagination keyboard for admin lists."""
    builder = InlineKeyboardBuilder()

    # Navigation buttons
    if current_page > 1:
        builder.button(text="⬅️ Назад", callback_data=f"{prefix}:page:{current_page - 1}")
    else:
        builder.button(text=" ", callback_data="noop")

    builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

    if current_page < total_pages:
        builder.button(text="Вперед ➡️", callback_data=f"{prefix}:page:{current_page + 1}")
    else:
        builder.button(text=" ", callback_data="noop")

    # Back button
    builder.button(text="« К списку", callback_data=back_callback)

    builder.adjust(3, 1)

    return builder.as_markup()


def get_admin_user_list_keyboard(
    users,
    current_page: int,
    total_pages: int,
    filter_type: str,
) -> InlineKeyboardMarkup:
    """Get keyboard with clickable user list and pagination."""
    builder = InlineKeyboardBuilder()

    for user in users:
        status = "🚫" if not user.is_active else ""
        label = f"{status} {user.display_name} (ID:{user.id})"
        builder.button(text=label[:50], callback_data=f"admin_view_user:{user.id}")

    # Pagination row
    if total_pages > 1:
        if current_page > 1:
            builder.button(text="⬅️", callback_data=f"admin_users_pg:{filter_type}:page:{current_page - 1}")
        else:
            builder.button(text=" ", callback_data="noop")

        builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

        if current_page < total_pages:
            builder.button(text="➡️", callback_data=f"admin_users_pg:{filter_type}:page:{current_page + 1}")
        else:
            builder.button(text=" ", callback_data="noop")

    builder.button(text="« Фильтры", callback_data="admin_users")

    # 1 button per row for users, then 3 for pagination, 1 for back
    rows = [1] * len(users)
    if total_pages > 1:
        rows.append(3)
    rows.append(1)
    builder.adjust(*rows)

    return builder.as_markup()


def get_admin_listing_list_keyboard(
    listings,
    current_page: int,
    total_pages: int,
    filter_type: str,
) -> InlineKeyboardMarkup:
    """Get keyboard with clickable listing list and pagination."""
    builder = InlineKeyboardBuilder()

    for listing in listings:
        flag = "🚩 " if listing.flagged else ""
        label = f"{flag}{listing.title[:35]} (ID:{listing.id})"
        builder.button(text=label[:50], callback_data=f"admin_view_listing:{listing.id}")

    # Pagination row
    if total_pages > 1:
        if current_page > 1:
            builder.button(text="⬅️", callback_data=f"admin_listings_pg:{filter_type}:page:{current_page - 1}")
        else:
            builder.button(text=" ", callback_data="noop")

        builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

        if current_page < total_pages:
            builder.button(text="➡️", callback_data=f"admin_listings_pg:{filter_type}:page:{current_page + 1}")
        else:
            builder.button(text=" ", callback_data="noop")

    builder.button(text="« Фильтры", callback_data="admin_listings")

    rows = [1] * len(listings)
    if total_pages > 1:
        rows.append(3)
    rows.append(1)
    builder.adjust(*rows)

    return builder.as_markup()


def get_admin_reviews_keyboard() -> InlineKeyboardMarkup:
    """Get admin reviews management keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(text="📋 Все отзывы", callback_data="admin_reviews:all")
    builder.button(text="« Назад", callback_data="admin_menu")

    builder.adjust(1, 1)

    return builder.as_markup()


def get_admin_review_actions_keyboard(review_id: int) -> InlineKeyboardMarkup:
    """Get actions keyboard for a specific review."""
    builder = InlineKeyboardBuilder()

    builder.button(text="🗑️ Удалить", callback_data=f"admin_review_delete:{review_id}")
    builder.button(text="« Назад", callback_data="admin_reviews:all")

    builder.adjust(1, 1)

    return builder.as_markup()


def get_admin_review_list_keyboard(
    reviews,
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Get keyboard with clickable review list and pagination."""
    builder = InlineKeyboardBuilder()

    for review in reviews:
        stars = "⭐" * review.rating
        label = f"{stars} ID:{review.id} (от #{review.reviewer_id})"
        builder.button(text=label[:50], callback_data=f"admin_view_review:{review.id}")

    # Pagination row
    if total_pages > 1:
        if current_page > 1:
            builder.button(text="⬅️", callback_data=f"admin_reviews_pg:all:page:{current_page - 1}")
        else:
            builder.button(text=" ", callback_data="noop")

        builder.button(text=f"{current_page}/{total_pages}", callback_data="noop")

        if current_page < total_pages:
            builder.button(text="➡️", callback_data=f"admin_reviews_pg:all:page:{current_page + 1}")
        else:
            builder.button(text=" ", callback_data="noop")

    builder.button(text="« Назад", callback_data="admin_reviews")

    rows = [1] * len(reviews)
    if total_pages > 1:
        rows.append(3)
    rows.append(1)
    builder.adjust(*rows)

    return builder.as_markup()


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Simple back to admin menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="« Админ-панель", callback_data="admin_menu")
    return builder.as_markup()
