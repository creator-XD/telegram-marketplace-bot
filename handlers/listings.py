"""
Handlers for listing management (create, edit, delete, view).
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.models import User, Listing, ListingPhoto, Favorite
from keyboards import (
    get_main_menu_keyboard,
    get_my_listings_keyboard,
    get_categories_keyboard,
    get_listing_detail_keyboard,
    get_edit_listing_keyboard,
    get_cancel_keyboard,
    get_skip_keyboard,
    get_confirm_keyboard,
    get_back_keyboard,
)
from keyboards.keyboards import get_done_keyboard, get_listings_keyboard
from states import ListingStates
from utils import format_listing_text, get_category_name
from utils.helpers import validate_title, validate_description, validate_price
from config import MESSAGES, MAX_PHOTOS, PAGE_SIZE

logger = logging.getLogger(__name__)
router = Router(name="listings")


# ==================== My Listings Menu ====================

@router.message(F.text == "/mylistings")
async def cmd_my_listings(message: Message, state: FSMContext):
    """Handle /mylistings command."""
    await state.clear()
    await message.answer(
        "📝 <b>Мои объявления</b>\n\nУправляйте своими объявлениями здесь:",
        reply_markup=get_my_listings_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "my_listings")
async def callback_my_listings(callback: CallbackQuery, state: FSMContext):
    """Handle My Listings menu callback."""
    await state.clear()
    await callback.message.edit_text(
        "📝 <b>Мои объявления</b>\n\nУправляйте своими объявлениями здесь:",
        reply_markup=get_my_listings_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "my_active")
async def callback_my_active_listings(callback: CallbackQuery):
    """Show user's active listings."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Listing.get_by_user(user.id, status="active")
    
    if not listings:
        await callback.message.edit_text(
            "📭 У вас пока нет активных объявлений.\n\nНажмите 'Добавить объявление', чтобы создать!",
            reply_markup=get_my_listings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = f"📋 <b>Ваши активные объявления</b> ({len(listings)})\n\n"
    text += "Выберите объявление для просмотра или редактирования:"
    
    keyboard = get_listings_keyboard(listings, callback_prefix="view_own_listing")
    keyboard.inline_keyboard.append([
        {"text": "◀️ Назад", "callback_data": "my_listings"}
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "my_sold")
async def callback_my_sold_listings(callback: CallbackQuery):
    """Show user's sold listings."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Listing.get_by_user(user.id, status="sold")
    
    if not listings:
        await callback.message.edit_text(
            "📭 У вас пока нет проданных товаров.",
            reply_markup=get_my_listings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = f"✅ <b>Ваши проданные товары</b> ({len(listings)})\n\n"
    
    keyboard = get_listings_keyboard(listings, callback_prefix="view_own_listing")
    keyboard.inline_keyboard.append([
        {"text": "◀️ Назад", "callback_data": "my_listings"}
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Create Listing ====================

@router.callback_query(F.data == "add_listing")
async def callback_add_listing(callback: CallbackQuery, state: FSMContext):
    """Start listing creation process."""
    await state.set_state(ListingStates.waiting_for_title)
    await state.update_data(photos=[])
    
    await callback.message.edit_text(
        "➕ <b>Создание объявления</b>\n\n"
        "Шаг 1/5: Введите <b>название</b> вашего объявления:\n\n"
        "<i>Пример: iPhone 14 Pro Max 256GB</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ListingStates.waiting_for_title)
async def process_listing_title(message: Message, state: FSMContext):
    """Process listing title."""
    is_valid, error = validate_title(message.text)
    
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\nПожалуйста, введите корректное название:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(ListingStates.waiting_for_description)

    await message.answer(
        "Шаг 2/5: Введите <b>описание</b> вашего объявления:\n\n"
        "<i>Опишите товар подробно - состояние, характеристики и т.д.</i>",
        reply_markup=get_skip_keyboard(skip_callback="skip_description"),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "skip_description", ListingStates.waiting_for_description)
async def skip_description(callback: CallbackQuery, state: FSMContext):
    """Skip description step."""
    await state.update_data(description="")
    await state.set_state(ListingStates.waiting_for_price)

    await callback.message.edit_text(
        "Шаг 3/5: Введите <b>цену</b> вашего объявления:\n\n"
        "<i>Пример: 999.99</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ListingStates.waiting_for_description)
async def process_listing_description(message: Message, state: FSMContext):
    """Process listing description."""
    is_valid, error = validate_description(message.text)
    
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\nПожалуйста, введите более короткое описание:",
            reply_markup=get_skip_keyboard(skip_callback="skip_description"),
            parse_mode="HTML",
        )
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(ListingStates.waiting_for_price)

    await message.answer(
        "Шаг 3/5: Введите <b>цену</b> вашего объявления:\n\n"
        "<i>Пример: 999.99</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(ListingStates.waiting_for_price)
async def process_listing_price(message: Message, state: FSMContext):
    """Process listing price."""
    is_valid, price, error = validate_price(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error}\n\nПожалуйста, введите корректную цену:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(price=price)
    await state.set_state(ListingStates.waiting_for_category)

    await message.answer(
        "Шаг 4/5: Выберите <b>категорию</b> для вашего объявления:",
        reply_markup=get_categories_keyboard(
            callback_prefix="new_listing_category",
            include_all=False,
            include_back=False,
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("new_listing_category:"), ListingStates.waiting_for_category)
async def process_listing_category(callback: CallbackQuery, state: FSMContext):
    """Process listing category selection."""
    category = callback.data.split(":")[1]
    await state.update_data(category=category)
    await state.set_state(ListingStates.waiting_for_photos)
    
    await callback.message.edit_text(
        f"Шаг 5/5: Отправьте <b>фото</b> вашего товара (до {MAX_PHOTOS}):\n\n"
        "<i>Отправляйте фото по одному, затем нажмите 'Готово'.</i>\n"
        "<i>Вы также можете пропустить этот шаг.</i>",
        reply_markup=get_skip_keyboard(skip_callback="skip_photos"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "skip_photos", ListingStates.waiting_for_photos)
async def skip_photos(callback: CallbackQuery, state: FSMContext):
    """Skip photos step."""
    await show_listing_confirmation(callback, state)


@router.message(ListingStates.waiting_for_photos, F.photo)
async def process_listing_photo(message: Message, state: FSMContext):
    """Process listing photo."""
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= MAX_PHOTOS:
        await message.answer(
            f"❌ Максимум {MAX_PHOTOS} фото. Нажмите 'Готово' для продолжения.",
            reply_markup=get_done_keyboard(done_callback="photos_done"),
            parse_mode="HTML",
        )
        return
    
    # Get the largest photo size
    photo = message.photo[-1]
    photos.append({
        "file_id": photo.file_id,
        "file_unique_id": photo.file_unique_id,
    })
    
    await state.update_data(photos=photos)
    
    remaining = MAX_PHOTOS - len(photos)
    await message.answer(
        f"✅ Фото добавлено! ({len(photos)}/{MAX_PHOTOS})\n\n"
        f"Отправьте ещё фото или нажмите 'Готово' для продолжения."
        f"{f' (осталось {remaining})' if remaining > 0 else ''}",
        reply_markup=get_done_keyboard(done_callback="photos_done"),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "photos_done", ListingStates.waiting_for_photos)
async def photos_done(callback: CallbackQuery, state: FSMContext):
    """Finish adding photos."""
    await show_listing_confirmation(callback, state)


async def show_listing_confirmation(callback: CallbackQuery, state: FSMContext):
    """Show listing confirmation."""
    data = await state.get_data()
    
    category_name = get_category_name(data["category"])
    photos_count = len(data.get("photos", []))
    
    text = (
        "📋 <b>Подтверждение объявления</b>\n\n"
        f"<b>Название:</b> {data['title']}\n"
        f"<b>Цена:</b> ${data['price']:.2f}\n"
        f"<b>Категория:</b> {category_name}\n"
        f"<b>Фото:</b> {photos_count}\n"
    )

    if data.get("description"):
        desc_preview = data["description"][:100]
        if len(data["description"]) > 100:
            desc_preview += "..."
        text += f"<b>Описание:</b> {desc_preview}\n"

    text += "\nВсё верно?"
    
    await state.set_state(ListingStates.confirm_listing)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_keyboard(
            confirm_callback="confirm_create_listing",
            cancel_callback="cancel"
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_create_listing", ListingStates.confirm_listing)
async def confirm_create_listing(callback: CallbackQuery, state: FSMContext):
    """Create the listing."""
    data = await state.get_data()
    user = await User.get_by_telegram_id(callback.from_user.id)
    
    # Create listing
    listing = await Listing.create(
        user_id=user.id,
        title=data["title"],
        description=data.get("description", ""),
        price=data["price"],
        category=data["category"],
    )
    
    # Add photos
    photos = data.get("photos", [])
    for i, photo in enumerate(photos):
        await ListingPhoto.create(
            listing_id=listing.id,
            file_id=photo["file_id"],
            file_unique_id=photo["file_unique_id"],
            is_primary=(i == 0),
        )
    
    await state.clear()
    
    logger.info(f"Listing created: {listing.id} by user {user.telegram_id}")
    
    await callback.message.edit_text(
        f"✅ <b>Объявление опубликовано!</b>\n\n"
        f"Ваше объявление \"{listing.title}\" теперь активно.\n\n"
        f"Покупатели теперь могут найти и связаться с вами по этому товару.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer(MESSAGES["listing_created"])


# ==================== View Listing ====================

@router.callback_query(F.data.startswith("view_listing:"))
async def view_listing(callback: CallbackQuery, bot: Bot):
    """View a listing (as a buyer)."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_photos=True, with_user=True)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    # Increment views
    await listing.increment_views()
    
    # Check if current user is owner
    user = await User.get_by_telegram_id(callback.from_user.id)
    is_owner = listing.user_id == user.id
    
    # Check if in favorites
    is_favorite = await Favorite.is_favorite(user.id, listing_id)
    
    text = format_listing_text(listing, user=listing.user, detailed=True)
    
    # If listing has photos, send them
    if listing.photos:
        # Delete previous message
        await callback.message.delete()
        
        if len(listing.photos) == 1:
            await bot.send_photo(
                callback.from_user.id,
                listing.photos[0].file_id,
                caption=text,
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite),
                parse_mode="HTML",
            )
        else:
            # Send media group
            media = [
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, photo in enumerate(listing.photos)
            ]
            await bot.send_media_group(callback.from_user.id, media)
            await bot.send_message(
                callback.from_user.id,
                "Выберите действие:",
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite),
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner, is_favorite),
            parse_mode="HTML",
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("view_own_listing:"))
async def view_own_listing(callback: CallbackQuery, bot: Bot):
    """View own listing (as seller)."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id, with_photos=True)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    text = format_listing_text(listing, detailed=True)
    
    if listing.photos:
        await callback.message.delete()
        
        if len(listing.photos) == 1:
            await bot.send_photo(
                callback.from_user.id,
                listing.photos[0].file_id,
                caption=text,
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True),
                parse_mode="HTML",
            )
        else:
            media = [
                InputMediaPhoto(
                    media=photo.file_id,
                    caption=text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, photo in enumerate(listing.photos)
            ]
            await bot.send_media_group(callback.from_user.id, media)
            await bot.send_message(
                callback.from_user.id,
                "Выберите действие:",
                reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True),
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_listing_detail_keyboard(listing_id, is_owner=True),
            parse_mode="HTML",
        )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_listings")
async def back_to_listings(callback: CallbackQuery):
    """Go back to listings view."""
    # Show recent listings
    listings = await Listing.get_recent(limit=PAGE_SIZE)
    
    if not listings:
        await callback.message.edit_text(
            MESSAGES["no_listings"],
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    
    text = "🛍️ <b>Последние объявления</b>\n\nВыберите объявление для просмотра:"
    
    keyboard = get_listings_keyboard(listings)
    keyboard.inline_keyboard.append([
        {"text": "◀️ В главное меню", "callback_data": "back_to_menu"}
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Edit Listing ====================

@router.callback_query(F.data.startswith("edit_listing:"))
async def edit_listing_menu(callback: CallbackQuery):
    """Show edit listing menu."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    # Verify ownership
    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer("Вы можете редактировать только свои объявления.", show_alert=True)
        return

    await callback.message.edit_text(
        f"✏️ <b>Редактирование объявления</b>\n\n"
        f"<b>{listing.title}</b>\n\n"
        f"Выберите, что хотите изменить:",
        reply_markup=get_edit_listing_keyboard(listing_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_field:"))
async def edit_field(callback: CallbackQuery, state: FSMContext):
    """Start editing a specific field."""
    parts = callback.data.split(":")
    field = parts[1]
    listing_id = int(parts[2])
    
    listing = await Listing.get_by_id(listing_id)
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    await state.update_data(editing_listing_id=listing_id)
    
    if field == "title":
        await state.set_state(ListingStates.editing_title)
        await callback.message.edit_text(
            f"Текущее название: <b>{listing.title}</b>\n\n"
            f"Введите новое название:",
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}"),
            parse_mode="HTML",
        )
    elif field == "description":
        await state.set_state(ListingStates.editing_description)
        current_desc = listing.description[:100] + "..." if listing.description and len(listing.description) > 100 else (listing.description or "Нет")
        await callback.message.edit_text(
            f"Текущее описание: {current_desc}\n\n"
            f"Введите новое описание:",
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}"),
            parse_mode="HTML",
        )
    elif field == "price":
        await state.set_state(ListingStates.editing_price)
        await callback.message.edit_text(
            f"Текущая цена: ${listing.price:.2f}\n\n"
            f"Введите новую цену:",
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}"),
            parse_mode="HTML",
        )
    elif field == "category":
        await state.set_state(ListingStates.editing_category)
        await callback.message.edit_text(
            f"Текущая категория: {get_category_name(listing.category)}\n\n"
            f"Выберите новую категорию:",
            reply_markup=get_categories_keyboard(
                callback_prefix="edit_category",
                include_all=False,
                include_back=False,
            ),
            parse_mode="HTML",
        )
    elif field == "photos":
        await callback.message.edit_text(
            "📷 <b>Управление фото</b>\n\n"
            "Чтобы обновить фото, удалите объявление и создайте новое.\n\n"
            "<i>Полное управление фото будет в будущем обновлении!</i>",
            reply_markup=get_back_keyboard(f"edit_listing:{listing_id}"),
            parse_mode="HTML",
        )
    
    await callback.answer()


@router.message(ListingStates.editing_title)
async def process_edit_title(message: Message, state: FSMContext):
    """Process edited title."""
    is_valid, error = validate_title(message.text)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПожалуйста, введите корректное название:")
        return
    
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)
    
    await listing.update(title=message.text.strip())
    await state.clear()
    
    await message.answer(
        MESSAGES["listing_updated"],
        reply_markup=get_edit_listing_keyboard(listing_id),
        parse_mode="HTML",
    )


@router.message(ListingStates.editing_description)
async def process_edit_description(message: Message, state: FSMContext):
    """Process edited description."""
    is_valid, error = validate_description(message.text)
    if not is_valid:
        await message.answer(f"❌ {error}")
        return
    
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)
    
    await listing.update(description=message.text.strip())
    await state.clear()
    
    await message.answer(
        MESSAGES["listing_updated"],
        reply_markup=get_edit_listing_keyboard(listing_id),
        parse_mode="HTML",
    )


@router.message(ListingStates.editing_price)
async def process_edit_price(message: Message, state: FSMContext):
    """Process edited price."""
    is_valid, price, error = validate_price(message.text)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПожалуйста, введите корректную цену:")
        return
    
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)
    
    await listing.update(price=price)
    await state.clear()
    
    await message.answer(
        MESSAGES["listing_updated"],
        reply_markup=get_edit_listing_keyboard(listing_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("edit_category:"), ListingStates.editing_category)
async def process_edit_category(callback: CallbackQuery, state: FSMContext):
    """Process edited category."""
    category = callback.data.split(":")[1]
    data = await state.get_data()
    listing_id = data["editing_listing_id"]
    listing = await Listing.get_by_id(listing_id)
    
    await listing.update(category=category)
    await state.clear()
    
    await callback.message.edit_text(
        MESSAGES["listing_updated"],
        reply_markup=get_edit_listing_keyboard(listing_id),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Delete Listing ====================

@router.callback_query(F.data.startswith("delete_listing:"))
async def delete_listing_confirm(callback: CallbackQuery):
    """Confirm listing deletion."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    # Verify ownership
    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer("Вы можете удалять только свои объявления.", show_alert=True)
        return

    await callback.message.edit_text(
        f"🗑️ <b>Удалить объявление?</b>\n\n"
        f"Вы уверены, что хотите удалить:\n"
        f"<b>{listing.title}</b>\n\n"
        f"Это действие нельзя отменить.",
        reply_markup=get_confirm_keyboard(
            confirm_callback=f"confirm_delete:{listing_id}",
            cancel_callback=f"view_own_listing:{listing_id}",
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_listing(callback: CallbackQuery):
    """Delete the listing."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)
    
    if listing:
        await listing.delete()
        logger.info(f"Listing deleted: {listing_id}")
    
    await callback.message.edit_text(
        MESSAGES["listing_deleted"],
        reply_markup=get_my_listings_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Mark as Sold ====================

@router.callback_query(F.data.startswith("mark_sold:"))
async def mark_as_sold(callback: CallbackQuery):
    """Mark listing as sold."""
    listing_id = int(callback.data.split(":")[1])
    listing = await Listing.get_by_id(listing_id)
    
    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return
    
    # Verify ownership
    user = await User.get_by_telegram_id(callback.from_user.id)
    if listing.user_id != user.id:
        await callback.answer("Вы можете изменять только свои объявления.", show_alert=True)
        return

    await listing.update(status="sold")

    await callback.message.edit_text(
        f"✅ <b>Отмечено как продано!</b>\n\n"
        f"<b>{listing.title}</b> отмечено как проданное.\n\n"
        f"Поздравляем с продажей! 🎉",
        reply_markup=get_my_listings_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer("Объявление отмечено как продано!")


# ==================== Favorites ====================

@router.message(F.text == "/favorites")
async def cmd_favorites(message: Message):
    """Handle /favorites command."""
    user = await User.get_by_telegram_id(message.from_user.id)
    listings = await Favorite.get_user_favorites(user.id)
    
    if not listings:
        await message.answer(
            "❤️ <b>Ваше избранное</b>\n\n"
            "Вы пока не сохранили ни одного объявления.\n\n"
            "Просматривайте объявления и нажимайте ❤️, чтобы сохранить их здесь!",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    text = f"❤️ <b>Ваше избранное</b> ({len(listings)})\n\n"
    
    keyboard = get_listings_keyboard(listings)
    keyboard.inline_keyboard.append([
        {"text": "◀️ В главное меню", "callback_data": "back_to_menu"}
    ])
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "favorites")
async def callback_favorites(callback: CallbackQuery):
    """Show favorites."""
    user = await User.get_by_telegram_id(callback.from_user.id)
    listings = await Favorite.get_user_favorites(user.id)
    
    if not listings:
        await callback.message.edit_text(
            "❤️ <b>Ваше избранное</b>\n\n"
            "Вы пока не сохранили ни одного объявления.\n\n"
            "Просматривайте объявления и нажимайте ❤️, чтобы сохранить их здесь!",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    text = f"❤️ <b>Ваше избранное</b> ({len(listings)})\n\n"
    
    keyboard = get_listings_keyboard(listings)
    keyboard.inline_keyboard.append([
        {"text": "◀️ В главное меню", "callback_data": "back_to_menu"}
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_favorite:"))
async def add_to_favorites(callback: CallbackQuery):
    """Add listing to favorites."""
    listing_id = int(callback.data.split(":")[1])
    user = await User.get_by_telegram_id(callback.from_user.id)
    
    result = await Favorite.add(user.id, listing_id)
    
    if result:
        await callback.answer(MESSAGES["added_to_favorites"])
    else:
        await callback.answer("Уже в избранном!")


@router.callback_query(F.data.startswith("remove_favorite:"))
async def remove_from_favorites(callback: CallbackQuery):
    """Remove listing from favorites."""
    listing_id = int(callback.data.split(":")[1])
    user = await User.get_by_telegram_id(callback.from_user.id)
    
    await Favorite.remove(user.id, listing_id)
    await callback.answer(MESSAGES["removed_from_favorites"])
