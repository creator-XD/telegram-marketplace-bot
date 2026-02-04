"""
Handlers for buyer-seller communication.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing, Message as DBMessage
from keyboards import get_cancel_keyboard, get_main_menu_keyboard, get_back_keyboard
from states import MessageStates
from utils import format_listing_short, escape_html
from utils.helpers import safe_edit_or_answer
from config import MESSAGES

logger = logging.getLogger(__name__)
router = Router(name="messages")


@router.callback_query(F.data.startswith("contact_seller:"))
async def contact_seller(callback: CallbackQuery, state: FSMContext):
    """Start contact seller flow."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_user=True)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return

    # Check if not contacting self
    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id == user.id:
        await callback.answer("Вы не можете написать себе!", show_alert=True)
        return
    
    await state.set_state(MessageStates.waiting_for_message)
    await state.update_data(
        contact_listing_id=listing_id,
        contact_seller_id=listing.user_id,
        contact_seller_telegram_id=listing.user.telegram_id,
    )

    await safe_edit_or_answer(
        callback,
        f"💬 <b>Связаться с продавцом</b>\n\n"
        f"Объявление: <b>{escape_html(listing.title)}</b>\n"
        f"Продавец: {escape_html(listing.user.display_name)}\n\n"
        f"Напишите ваше сообщение продавцу:\n\n"
        f"<i>Советы:\n"
        f"• Будьте вежливы и понятны\n"
        f"• Задайте вопросы о товаре\n"
        f"• Укажите, если хотите торговаться</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(MessageStates.waiting_for_message)
async def process_buyer_message(message: Message, state: FSMContext, bot: Bot):
    """Process and send message to seller."""
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(
            "❌ Сообщение слишком короткое. Напишите полноценное сообщение:",
            reply_markup=get_cancel_keyboard(),
        )
        return

    if len(message.text) > 1000:
        await message.answer(
            "❌ Сообщение слишком длинное. Ограничьте его 1000 символами:",
            reply_markup=get_cancel_keyboard(),
        )
        return
    
    data = await state.get_data()
    listing_id = data["contact_listing_id"]
    seller_telegram_id = data["contact_seller_telegram_id"]
    seller_id = data["contact_seller_id"]
    
    # Get listing and buyer info
    listing = await Listing.get_by_id(listing_id)
    buyer = await User.get_by_telegram_id(message.from_user.id)
    
    if not listing:
        await state.clear()
        await message.answer(
            "❌ Объявление больше не существует.",
            reply_markup=get_main_menu_keyboard(),
        )
        return
    
    # Save message to database
    await DBMessage.create(
        sender_id=buyer.id,
        receiver_id=seller_id,
        listing_id=listing_id,
        message_text=message.text.strip(),
    )
    
    # Send message to seller
    seller_message = (
        f"📩 <b>Новое сообщение!</b>\n\n"
        f"От: {escape_html(buyer.display_name)}"
    )

    if buyer.username:
        seller_message += f" (@{buyer.username})"

    seller_message += (
        f"\n\n"
        f"По объявлению: <b>{escape_html(listing.title)}</b>\n"
        f"Цена: ${listing.price:.2f}\n\n"
        f"<b>Сообщение:</b>\n{escape_html(message.text.strip())}\n\n"
        f"<i>Ответьте покупателю напрямую через Telegram</i>"
    )
    
    try:
        await bot.send_message(
            seller_telegram_id,
            seller_message,
            parse_mode="HTML",
        )
        
        await state.clear()
        
        response_text = (
            f"✅ <b>Сообщение отправлено!</b>\n\n"
            f"Ваше сообщение отправлено продавцу.\n\n"
        )

        # Provide contact info if available
        seller = await User.get_by_id(seller_id)
        if seller and seller.username:
            response_text += f"Вы также можете связаться с продавцом напрямую: @{seller.username}"
        else:
            response_text += "Продавец ответит вам через этот бот или Telegram."
        
        await message.answer(
            response_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        
        logger.info(f"Message sent: buyer {buyer.telegram_id} -> seller {seller_telegram_id} for listing {listing_id}")
        
    except Exception as e:
        logger.error(f"Failed to send message to seller: {e}")
        await state.clear()
        await message.answer(
            "❌ <b>Не удалось отправить</b>\n\n"
            "Telegram-аккаунт продавца не смог получить сообщение.\n"
            "Возможно, продавец заблокировал бота.\n\n"
            "Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )


# ==================== Reply to Buyer (for future enhancement) ====================

@router.callback_query(F.data.startswith("reply_to_buyer:"))
async def reply_to_buyer(callback: CallbackQuery, state: FSMContext):
    """Start reply to buyer flow."""
    # This is a placeholder for future enhancement
    # In a full implementation, this would allow sellers to reply through the bot
    parts = callback.data.split(":")
    buyer_id = int(parts[1])
    listing_id = int(parts[2]) if len(parts) > 2 else None
    
    await state.set_state(MessageStates.waiting_for_reply)
    await state.update_data(
        reply_buyer_id=buyer_id,
        reply_listing_id=listing_id,
    )

    await safe_edit_or_answer(
        callback,
        "💬 <b>Ответ покупателю</b>\n\n"
        "Напишите ваш ответ:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(MessageStates.waiting_for_reply)
async def process_seller_reply(message: Message, state: FSMContext, bot: Bot):
    """Process seller's reply to buyer."""
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(
            "❌ Сообщение слишком короткое. Напишите полноценный ответ:",
            reply_markup=get_cancel_keyboard(),
        )
        return
    
    data = await state.get_data()
    buyer_id = data.get("reply_buyer_id")
    listing_id = data.get("reply_listing_id")
    
    buyer = await User.get_by_id(buyer_id)
    seller = await User.get_by_telegram_id(message.from_user.id)
    
    if not buyer:
        await state.clear()
        await message.answer(
            "❌ Покупатель не найден.",
            reply_markup=get_main_menu_keyboard(),
        )
        return
    
    # Save reply to database
    await DBMessage.create(
        sender_id=seller.id,
        receiver_id=buyer_id,
        listing_id=listing_id,
        message_text=message.text.strip(),
    )
    
    # Build reply message
    reply_text = f"📩 <b>Ответ продавца!</b>\n\n"
    reply_text += f"От: {escape_html(seller.display_name)}"

    if seller.username:
        reply_text += f" (@{seller.username})"

    if listing_id:
        listing = await Listing.get_by_id(listing_id)
        if listing:
            reply_text += f"\n\nПо объявлению: <b>{escape_html(listing.title)}</b>"

    reply_text += f"\n\n<b>Сообщение:</b>\n{escape_html(message.text.strip())}"
    
    try:
        await bot.send_message(
            buyer.telegram_id,
            reply_text,
            parse_mode="HTML",
        )
        
        await state.clear()
        await message.answer(
            "✅ <b>Ответ отправлен!</b>",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Failed to send reply to buyer: {e}")
        await state.clear()
        await message.answer(
            "❌ Не удалось отправить ответ. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(),
        )
