"""
Main admin panel router and dashboard.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from database.models import User, Listing, Transaction
from database.admin_models import AdminUser, AdminAuditLog
from keyboards.admin_keyboards import get_admin_main_menu_keyboard
from keyboards import get_main_menu_keyboard
from utils.decorators import require_admin
from utils.admin_helpers import format_admin_dashboard
from config import BOT_NAME, MESSAGES
import logging

logger = logging.getLogger(__name__)

admin_router = Router(name="admin")

# Import and include sub-routers
from . import user_management, listing_management, transaction_management, analytics, audit

admin_router.include_router(user_management.router)
admin_router.include_router(listing_management.router)
admin_router.include_router(transaction_management.router)
admin_router.include_router(analytics.router)
admin_router.include_router(audit.router)


@admin_router.message(Command("admin"))
@require_admin
async def admin_command(message: Message, admin: AdminUser):
    """Handle /admin command - show admin panel."""
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=get_admin_main_menu_keyboard()
    )


@admin_router.callback_query(F.data == "admin_menu")
@require_admin
async def admin_menu_callback(callback: CallbackQuery, admin: AdminUser):
    """Show admin main menu."""
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\nВыберите раздел:",
        reply_markup=get_admin_main_menu_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_dashboard")
@require_admin
async def admin_dashboard_callback(callback: CallbackQuery, admin: AdminUser):
    """Show admin dashboard with statistics."""
    # Get statistics
    user_stats = await User.get_statistics()
    listing_stats = await Listing.get_statistics()
    transaction_stats = await Transaction.get_statistics()

    stats = {
        "user_stats": user_stats,
        "listing_stats": listing_stats,
        "transaction_stats": transaction_stats,
    }

    dashboard_text = format_admin_dashboard(stats)

    await callback.message.edit_text(
        dashboard_text,
        reply_markup=get_admin_main_menu_keyboard()
    )
    await callback.answer()


@admin_router.callback_query(F.data == "main_menu")
@require_admin
async def main_menu_callback(callback: CallbackQuery, admin: AdminUser):
    """Return to main user menu from admin panel."""
    welcome_text = MESSAGES["welcome"].format(bot_name=BOT_NAME)
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
