"""
Handlers for user profile management.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing
from keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
)
from keyboards.keyboards import remove_keyboard
from states import ProfileStates
from utils.helpers import format_user_profile, escape_html, safe_edit_or_answer

logger = logging.getLogger(__name__)
router = Router(name="profile")


@router.message(F.text == "/profile")
async def cmd_profile(message: Message, state: FSMContext):
    """Handle /profile command."""
    await state.clear()
    user = await User.get_by_telegram_id(message.from_user.id)
    
    # Get user stats
    active_listings = await Listing.get_by_user(user.id, status="active")
    sold_listings = await Listing.get_by_user(user.id, status="sold")
    
    text = format_user_profile(user)
    text += f"\n📊 <b>Статистика:</b>\n"
    text += f"• Активных объявлений: {len(active_listings)}\n"
    text += f"• Продано товаров: {len(sold_listings)}\n"
    
    await message.answer(
        text,
        reply_markup=get_profile_keyboard(user.id),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery, state: FSMContext):
    """Show user profile."""
    await state.clear()
    user = await User.get_by_telegram_id(callback.from_user.id)

    # Get user stats
    active_listings = await Listing.get_by_user(user.id, status="active")
    sold_listings = await Listing.get_by_user(user.id, status="sold")

    text = format_user_profile(user)
    text += f"\n📊 <b>Статистика:</b>\n"
    text += f"• Активных объявлений: {len(active_listings)}\n"
    text += f"• Продано товаров: {len(sold_listings)}\n"

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=get_profile_keyboard(user.id),
        parse_mode="HTML",
    )
    await callback.answer()


def get_profile_keyboard(user_id: int = None):
    """Get profile management keyboard."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📍 Изменить местоположение", callback_data="edit_location"),
        InlineKeyboardButton(text="📝 Изменить о себе", callback_data="edit_bio"),
    )
    if user_id is not None:
        builder.row(
            InlineKeyboardButton(text="⭐ Мои отзывы", callback_data=f"seller_reviews:{user_id}"),
        )
    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu"),
    )

    return builder.as_markup()


# ==================== Edit Location ====================

@router.callback_query(F.data == "edit_location")
async def edit_location(callback: CallbackQuery, state: FSMContext):
    """Start location editing."""
    await state.set_state(ProfileStates.editing_location)

    user = await User.get_by_telegram_id(callback.from_user.id)
    current_location = user.location or "Не указано"

    await safe_edit_or_answer(
        callback,
        f"📍 <b>Изменить местоположение</b>\n\n"
        f"Текущее: {escape_html(current_location)}\n\n"
        f"Введите ваше новое местоположение:\n\n"
        f"<i>Пример: Москва или Санкт-Петербург</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ProfileStates.editing_location)
async def process_location(message: Message, state: FSMContext):
    """Process location update."""
    location = message.text.strip()
    
    if len(location) > 100:
        await message.answer(
            "❌ Местоположение слишком длинное. Ограничьте его 100 символами:",
            reply_markup=get_cancel_keyboard(),
        )
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    await user.update(location=location)

    await state.clear()
    await message.answer(
        "✅ <b>Местоположение обновлено!</b>\n\n"
        f"Ваше местоположение: {escape_html(location)}",
        reply_markup=get_profile_keyboard(user.id),
        parse_mode="HTML",
    )


# ==================== Edit Bio ====================

@router.callback_query(F.data == "edit_bio")
async def edit_bio(callback: CallbackQuery, state: FSMContext):
    """Start bio editing."""
    await state.set_state(ProfileStates.editing_bio)

    user = await User.get_by_telegram_id(callback.from_user.id)
    current_bio = user.bio or "Не указано"

    await safe_edit_or_answer(
        callback,
        f"📝 <b>Изменить информацию о себе</b>\n\n"
        f"Текущая: {escape_html(current_bio)}\n\n"
        f"Напишите что-нибудь о себе:\n\n"
        f"<i>Это поможет покупателям больше вам доверять!</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ProfileStates.editing_bio)
async def process_bio(message: Message, state: FSMContext):
    """Process bio update."""
    bio = message.text.strip()
    
    if len(bio) > 500:
        await message.answer(
            "❌ Информация слишком длинная. Ограничьте её 500 символами:",
            reply_markup=get_cancel_keyboard(),
        )
        return

    user = await User.get_by_telegram_id(message.from_user.id)
    await user.update(bio=bio)

    await state.clear()
    await message.answer(
        "✅ <b>Информация о себе обновлена!</b>\n\n"
        f"Ваша информация: {escape_html(bio)}",
        reply_markup=get_profile_keyboard(user.id),
        parse_mode="HTML",
    )


# ==================== Future: Payment Settings ====================

@router.callback_query(F.data == "payment_settings")
async def payment_settings(callback: CallbackQuery):
    """Show payment settings (placeholder for future)."""
    await safe_edit_or_answer(
        callback,
        "💳 <b>Настройки оплаты</b>\n\n"
        "Интеграция оплаты скоро появится!\n\n"
        "<i>Эта функция позволит вам:\n"
        "• Привязать способы оплаты\n"
        "• Получать безопасные платежи\n"
        "• Отслеживать историю транзакций</i>",
        reply_markup=get_back_keyboard("profile"),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Future: Verification ====================

@router.callback_query(F.data == "get_verified")
async def get_verified(callback: CallbackQuery):
    """Show verification options (placeholder for future)."""
    await safe_edit_or_answer(
        callback,
        "✅ <b>Верификация</b>\n\n"
        "Верификация продавцов скоро появится!\n\n"
        "<i>Преимущества верификации:\n"
        "• Значок верификации на ваших объявлениях\n"
        "• Повышенное доверие покупателей\n"
        "• Приоритет в результатах поиска</i>",
        reply_markup=get_back_keyboard("profile"),
        parse_mode="HTML",
    )
    await callback.answer()
