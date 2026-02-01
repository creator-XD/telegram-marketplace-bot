"""
Configuration settings for the Telegram Marketplace Bot.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Please check your .env file.")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "marketplace.db")

# Bot Settings
BOT_NAME = os.getenv("BOT_NAME", "Telegram Trade bot")
SUPPORT_USERNAME = "@tradetesttt_bot"

# Admin Configuration
ADMIN_TELEGRAM_IDS = [
    int(id.strip()) for id in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if id.strip()
]
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "0")) if os.getenv("SUPER_ADMIN_ID") else None

# Listing Settings
MAX_PHOTOS = 5
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 2000
MIN_PRICE = 0.01
MAX_PRICE = 1000000.00

# Pagination
PAGE_SIZE = 5

# Categories for listings
CATEGORIES: List[dict] = [
    {"id": "electronics", "name": "📱 Электроника", "emoji": "📱"},
    {"id": "clothing", "name": "👕 Одежда и мода", "emoji": "👕"},
    {"id": "home", "name": "🏠 Дом и сад", "emoji": "🏠"},
    {"id": "vehicles", "name": "🚗 Транспорт", "emoji": "🚗"},
    {"id": "services", "name": "🔧 Услуги", "emoji": "🔧"},
    {"id": "jobs", "name": "💼 Работа", "emoji": "💼"},
    {"id": "pets", "name": "🐾 Животные", "emoji": "🐾"},
    {"id": "sports", "name": "⚽ Спорт и хобби", "emoji": "⚽"},
    {"id": "books", "name": "📚 Книги и обучение", "emoji": "📚"},
    {"id": "other", "name": "📦 Другое", "emoji": "📦"},
]

# Currency settings
CURRENCY = "$"
CURRENCY_CODE = "USD"

# Message templates
MESSAGES = {
    "welcome": """
🛍️ <b>Добро пожаловать в {bot_name}!</b>

Ваш универсальный маркетплейс для покупки и продажи товаров и услуг.

<b>Что вы можете делать:</b>
• 🔍 Просматривать и искать объявления
• ➕ Создавать свои объявления
• 💬 Общаться с покупателями/продавцами
• ❤️ Сохранять в избранное

Используйте кнопки ниже, чтобы начать!
""",
    "help": """
📖 <b>Помощь и команды</b>

<b>Навигация:</b>
• /start - Главное меню
• /search - Поиск объявлений
• /mylistings - Ваши объявления
• /favorites - Избранное
• /profile - Ваш профиль
• /cancel - Отменить операцию

<b>Создание объявления:</b>
1. Перейдите в "Мои объявления" → "Добавить"
2. Введите название, описание, цену
3. Выберите категорию
4. Добавьте фото (по желанию)
5. Подтвердите и опубликуйте!

<b>Покупка:</b>
1. Просматривайте или ищите объявления
2. Смотрите подробности
3. Свяжитесь с продавцом
4. Договоритесь об оплате/доставке

Нужна помощь? Напишите {support}
""",
    "listing_created": "✅ Ваше объявление опубликовано!",
    "listing_updated": "✅ Объявление успешно обновлено!",
    "listing_deleted": "🗑️ Объявление удалено.",
    "no_listings": "📭 Объявления не найдены.",
    "contact_seller": "💬 Сообщение отправлено продавцу!",
    "added_to_favorites": "❤️ Добавлено в избранное!",
    "removed_from_favorites": "💔 Удалено из избранного.",
    "operation_cancelled": "❌ Операция отменена.",
}

# Payment Configuration (placeholder for future integration)
PAYMENT_CONFIG = {
    "enabled": False,  # Set to True when payment is implemented
    "provider": None,  # "stripe", "telegram_payments", etc.
    "test_mode": True,
    "provider_token": "",  # Payment provider token
}

# Future feature flags
FEATURES = {
    "payments_enabled": False,
    "reviews_enabled": False,
    "delivery_tracking": False,
    "verified_sellers": False,
    "promoted_listings": False,
}

# Admin Role Permissions
ADMIN_ROLES = {
    "super_admin": [
        "manage_users",
        "manage_listings",
        "manage_transactions",
        "view_analytics",
        "manage_admins",
        "view_audit_log",
        "edit_any_listing",
        "delete_any_listing",
        "block_users",
        "warn_users",
    ],
    "admin": [
        "manage_users",
        "manage_listings",
        "manage_transactions",
        "view_analytics",
        "view_audit_log",
        "edit_any_listing",
        "delete_any_listing",
        "block_users",
        "warn_users",
    ],
    "moderator": [
        "manage_listings",
        "warn_users",
        "view_analytics",
        "edit_any_listing",
    ],
}

# Admin Settings
ADMIN_PAGE_SIZE = 10  # Items per page in admin panel
