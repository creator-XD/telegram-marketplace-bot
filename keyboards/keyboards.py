"""
Inline and Reply keyboards for the Telegram Marketplace Bot.
"""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Optional
from config import CATEGORIES, CURRENCY


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu inline keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔍 Обзор объявлений", callback_data="browse"),
        InlineKeyboardButton(text="🔎 Поиск", callback_data="search"),
    )
    builder.row(
        InlineKeyboardButton(text="📝 Мои объявления", callback_data="my_listings"),
        InlineKeyboardButton(text="❤️ Избранное", callback_data="favorites"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить объявление", callback_data="add_listing"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
    )
    
    return builder.as_markup()


def get_categories_keyboard(
    callback_prefix: str = "category",
    include_all: bool = True,
    include_back: bool = True,
) -> InlineKeyboardMarkup:
    """Get categories selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    if include_all:
        builder.row(
            InlineKeyboardButton(text="📋 Все категории", callback_data=f"{callback_prefix}:all")
        )
    
    # Add categories in pairs
    for i in range(0, len(CATEGORIES), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(CATEGORIES):
                cat = CATEGORIES[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=cat["name"],
                        callback_data=f"{callback_prefix}:{cat['id']}"
                    )
                )
        builder.row(*row_buttons)
    
    if include_back:
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
        )
    
    return builder.as_markup()


def get_listing_actions_keyboard(listing_id: int, is_owner: bool = False) -> InlineKeyboardMarkup:
    """Get actions keyboard for a listing."""
    builder = InlineKeyboardBuilder()
    
    if is_owner:
        builder.row(
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_listing:{listing_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_listing:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text="✅ Отметить как продано", callback_data=f"mark_sold:{listing_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="💬 Связаться с продавцом", callback_data=f"contact_seller:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text="❤️ В избранное", callback_data=f"add_favorite:{listing_id}"),
        )

    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_listings"),
    )
    
    return builder.as_markup()


def get_my_listings_keyboard() -> InlineKeyboardMarkup:
    """Get My Listings menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Активные объявления", callback_data="my_active"),
    )
    builder.row(
        InlineKeyboardButton(text="✅ Проданные товары", callback_data="my_sold"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Добавить объявление", callback_data="add_listing"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu"),
    )
    
    return builder.as_markup()


def get_search_keyboard() -> InlineKeyboardMarkup:
    """Get search options keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔤 Поиск по ключевым словам", callback_data="search_keywords"),
    )
    builder.row(
        InlineKeyboardButton(text="📁 Обзор по категориям", callback_data="search_category"),
    )
    builder.row(
        InlineKeyboardButton(text="💰 Фильтр по цене", callback_data="search_price"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu"),
    )
    
    return builder.as_markup()


def get_confirm_keyboard(confirm_callback: str, cancel_callback: str = "cancel") -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_callback),
        InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_callback),
    )
    
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_back_keyboard(callback_data: str = "back_to_menu") -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data),
    )
    return builder.as_markup()


def get_skip_keyboard(skip_callback: str = "skip") -> InlineKeyboardMarkup:
    """Get skip button keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=skip_callback),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    extra_data: str = "",
) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    builder = InlineKeyboardBuilder()
    
    row_buttons = []
    
    # Previous button
    if current_page > 1:
        row_buttons.append(
            InlineKeyboardButton(
                text="◀️ Пред.",
                callback_data=f"{callback_prefix}:page:{current_page - 1}:{extra_data}"
            )
        )

    # Page indicator
    row_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="noop"
        )
    )

    # Next button
    if current_page < total_pages:
        row_buttons.append(
            InlineKeyboardButton(
                text="След. ▶️",
                callback_data=f"{callback_prefix}:page:{current_page + 1}:{extra_data}"
            )
        )

    builder.row(*row_buttons)
    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu"),
    )
    
    return builder.as_markup()


def get_listing_detail_keyboard(
    listing_id: int,
    is_owner: bool = False,
    is_favorite: bool = False,
    seller_id: int = None,
) -> InlineKeyboardMarkup:
    """Get detailed listing view keyboard."""
    builder = InlineKeyboardBuilder()

    if is_owner:
        builder.row(
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_listing:{listing_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_listing:{listing_id}"),
        )
        builder.row(
            InlineKeyboardButton(text="✅ Отметить как продано", callback_data=f"mark_sold:{listing_id}"),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="💬 Связаться с продавцом",
                callback_data=f"contact_seller:{listing_id}"
            ),
        )

        fav_text = "💔 Удалить из избранного" if is_favorite else "❤️ В избранное"
        fav_callback = f"remove_favorite:{listing_id}" if is_favorite else f"add_favorite:{listing_id}"
        builder.row(
            InlineKeyboardButton(text=fav_text, callback_data=fav_callback),
        )
        builder.row(
            InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=f"leave_review:{listing_id}"),
        )

    if seller_id is not None:
        builder.row(
            InlineKeyboardButton(
                text="📝 Отзывы о продавце",
                callback_data=f"seller_reviews:{seller_id}"
            ),
        )

    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_listings"),
    )

    return builder.as_markup()


def get_edit_listing_keyboard(listing_id: int) -> InlineKeyboardMarkup:
    """Get edit listing options keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Название", callback_data=f"edit_field:title:{listing_id}"),
        InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_field:description:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="💰 Цена", callback_data=f"edit_field:price:{listing_id}"),
        InlineKeyboardButton(text="📁 Категория", callback_data=f"edit_field:category:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📷 Фото", callback_data=f"edit_field:photos:{listing_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"view_listing:{listing_id}"),
    )
    
    return builder.as_markup()


def get_listings_keyboard(
    listings: List,
    callback_prefix: str = "view_listing",
    show_price: bool = True,
) -> InlineKeyboardMarkup:
    """Get keyboard with listing buttons."""
    builder = InlineKeyboardBuilder()
    
    for listing in listings:
        text = listing.title[:30]
        if show_price:
            text += f" - {CURRENCY}{listing.price:.2f}"
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"{callback_prefix}:{listing.id}"
            )
        )
    
    return builder.as_markup()


def get_price_range_keyboard() -> InlineKeyboardMarkup:
    """Get predefined price range options."""
    builder = InlineKeyboardBuilder()
    
    ranges = [
        ("До $25", "0:25"),
        ("$25 - $50", "25:50"),
        ("$50 - $100", "50:100"),
        ("$100 - $500", "100:500"),
        ("$500+", "500:0"),
        ("Свой диапазон", "custom"),
    ]
    
    for i in range(0, len(ranges), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(ranges):
                text, data = ranges[i + j]
                row_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=f"price_range:{data}")
                )
        builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="search"),
    )

    return builder.as_markup()


def get_done_keyboard(done_callback: str = "done") -> InlineKeyboardMarkup:
    """Get done button keyboard (for multi-item selections like photos)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Готово", callback_data=done_callback),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


# Reply keyboard for sharing contact/location
def get_share_contact_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for sharing contact."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📱 Поделиться контактом", request_contact=True))
    builder.row(KeyboardButton(text="⏭️ Пропустить"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_share_location_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for sharing location."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📍 Поделиться локацией", request_location=True))
    builder.row(KeyboardButton(text="⏭️ Пропустить"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_rating_keyboard(listing_id: int) -> InlineKeyboardMarkup:
    """Get star rating keyboard (1-5)."""
    builder = InlineKeyboardBuilder()
    stars = []
    for i in range(1, 6):
        stars.append(
            InlineKeyboardButton(
                text="⭐" * i,
                callback_data=f"review_rating:{i}:{listing_id}"
            )
        )
    # Two per row: 1-2, 3-4, then 5 alone
    builder.row(stars[0], stars[1])
    builder.row(stars[2], stars[3])
    builder.row(stars[4])
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_review_comment_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for review comment step (skip or cancel)."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_review_comment"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
    )
    return builder.as_markup()


def get_seller_reviews_keyboard(seller_id: int) -> InlineKeyboardMarkup:
    """Get button to view all seller reviews."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⭐ Отзывы о продавце",
            callback_data=f"seller_reviews:{seller_id}"
        ),
    )
    return builder.as_markup()


def remove_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()
