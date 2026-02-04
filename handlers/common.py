"""
Common handlers for start, help, and general navigation.
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from database.models import User
from keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
)
from config import MESSAGES, BOT_NAME, SUPPORT_USERNAME, WELCOME_IMAGE_PATH
from utils.helpers import safe_edit_or_answer

logger = logging.getLogger(__name__)
router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command."""
    # Clear any existing state
    await state.clear()

    # Get or create user
    user = await User.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    logger.info(f"User started bot: {user.telegram_id} ({user.display_name})")

    welcome_text = MESSAGES["welcome"].format(bot_name=BOT_NAME)

    # Send welcome image with caption
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await message.answer_photo(
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = MESSAGES["help"].format(support=SUPPORT_USERNAME)
    
    await message.answer(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Handle help button callback."""
    help_text = MESSAGES["help"].format(support=SUPPORT_USERNAME)

    await safe_edit_or_answer(
        callback,
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command."""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "Нечего отменять. Используйте /start для перехода в главное меню.",
            parse_mode="HTML",
        )
        return
    
    await state.clear()
    await message.answer(
        MESSAGES["operation_cancelled"],
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Handle cancel button callback."""
    await state.clear()

    welcome_text = MESSAGES["welcome"].format(bot_name=BOT_NAME)

    # Delete the current message and send new photo message
    await callback.message.delete()
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await callback.message.answer_photo(
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(MESSAGES["operation_cancelled"])


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Handle back to menu callback."""
    await state.clear()

    welcome_text = MESSAGES["welcome"].format(bot_name=BOT_NAME)

    # Delete the current message and send new photo message
    await callback.message.delete()
    welcome_image = FSInputFile(WELCOME_IMAGE_PATH)
    await callback.message.answer_photo(
        photo=welcome_image,
        caption=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """Handle no-operation callbacks (like page indicators)."""
    await callback.answer()



