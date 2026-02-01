"""
Helper utility functions for the Telegram Marketplace Bot.
"""
import html
from typing import Optional
from config import CATEGORIES, CURRENCY
from database.models import Listing, User


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if text is None:
        return ""
    return html.escape(str(text))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if text is None:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_price(price: float, currency: str = CURRENCY) -> str:
    """Format price with currency symbol."""
    return f"{currency}{price:,.2f}"


def get_category_name(category_id: str) -> str:
    """Get category display name by ID."""
    for cat in CATEGORIES:
        if cat["id"] == category_id:
            return cat["name"]
    return category_id.title()


def get_category_emoji(category_id: str) -> str:
    """Get category emoji by ID."""
    for cat in CATEGORIES:
        if cat["id"] == category_id:
            return cat["emoji"]
    return "📦"


def format_listing_text(listing: Listing, user: Optional[User] = None, detailed: bool = True) -> str:
    """
    Format listing for display in Telegram message.
    
    Args:
        listing: The listing to format
        user: Optional seller user object
        detailed: Whether to show full details
    
    Returns:
        Formatted HTML string
    """
    category_name = get_category_name(listing.category)
    price_text = format_price(listing.price)
    
    if detailed:
        text = f"""
<b>{escape_html(listing.title)}</b>

💰 <b>Цена:</b> {price_text}
📁 <b>Категория:</b> {category_name}
"""

        if listing.location:
            text += f"📍 <b>Местоположение:</b> {escape_html(listing.location)}\n"

        text += f"\n📝 <b>Описание:</b>\n{escape_html(listing.description or 'Нет описания')}\n"

        if user:
            text += f"\n👤 <b>Продавец:</b> {escape_html(user.display_name)}"
            if user.rating > 0:
                text += f" ⭐ {user.rating:.1f} ({user.rating_count} отзывов)"

        text += f"\n\n👁️ Просмотров: {listing.views}"

        if listing.status != "active":
            status_emoji = "✅" if listing.status == "sold" else "🔒"
            status_text = "Продано" if listing.status == "sold" else listing.status.title()
            text += f"\n{status_emoji} Статус: {status_text}"
    else:
        # Short format
        text = f"<b>{escape_html(truncate_text(listing.title, 40))}</b>\n"
        text += f"💰 {price_text} | 📁 {category_name}"
    
    return text


def format_listing_short(listing: Listing) -> str:
    """Format listing in short single-line format."""
    price_text = format_price(listing.price)
    title = truncate_text(listing.title, 30)
    return f"{title} - {price_text}"


def format_user_profile(user: User) -> str:
    """Format user profile for display."""
    text = f"""
👤 <b>Ваш профиль</b>

<b>Имя:</b> {escape_html(user.display_name)}
"""

    if user.username:
        text += f"<b>Имя пользователя:</b> @{escape_html(user.username)}\n"

    if user.phone:
        text += f"<b>Телефон:</b> {escape_html(user.phone)}\n"

    if user.location:
        text += f"<b>Местоположение:</b> {escape_html(user.location)}\n"

    if user.bio:
        text += f"<b>О себе:</b> {escape_html(user.bio)}\n"

    if user.rating > 0:
        text += f"\n⭐ <b>Рейтинг:</b> {user.rating:.1f} ({user.rating_count} отзывов)\n"

    if user.is_verified:
        text += "✅ Верифицированный продавец\n"

    return text


def format_search_results_header(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    total: int = 0,
) -> str:
    """Format search results header."""
    text = "🔍 <b>Результаты поиска</b>\n\n"

    filters = []
    if query:
        filters.append(f"Ключевые слова: \"{escape_html(query)}\"")
    if category and category != "all":
        filters.append(f"Категория: {get_category_name(category)}")
    if min_price is not None or max_price is not None:
        if min_price and max_price:
            filters.append(f"Цена: {format_price(min_price)} - {format_price(max_price)}")
        elif min_price:
            filters.append(f"Цена: от {format_price(min_price)}")
        elif max_price:
            filters.append(f"Цена: до {format_price(max_price)}")

    if filters:
        text += "Фильтры: " + ", ".join(filters) + "\n\n"

    text += f"Найдено <b>{total}</b> объявлений\n"

    return text


def validate_price(text: str) -> tuple[bool, Optional[float], str]:
    """
    Validate price input.

    Returns:
        Tuple of (is_valid, price_value, error_message)
    """
    try:
        # Remove currency symbols and whitespace
        cleaned = text.strip().replace("$", "").replace(",", "").replace(" ", "")
        price = float(cleaned)

        if price < 0:
            return False, None, "Цена не может быть отрицательной."

        if price > 1000000:
            return False, None, "Цена не может превышать $1,000,000."

        return True, round(price, 2), ""
    except ValueError:
        return False, None, "Пожалуйста, введите корректное число для цены."


def validate_title(text: str) -> tuple[bool, str]:
    """
    Validate listing title.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Название не может быть пустым."

    if len(text.strip()) < 3:
        return False, "Название должно быть не менее 3 символов."

    if len(text.strip()) > 100:
        return False, "Название не может превышать 100 символов."

    return True, ""


def validate_description(text: str) -> tuple[bool, str]:
    """
    Validate listing description.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if text and len(text.strip()) > 2000:
        return False, "Описание не может превышать 2000 символов."

    return True, ""
