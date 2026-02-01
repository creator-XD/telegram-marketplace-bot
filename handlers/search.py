"""
Handlers for search and filtering functionality.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import User, Listing
from keyboards import (
    get_main_menu_keyboard,
    get_search_keyboard,
    get_categories_keyboard,
    get_cancel_keyboard,
    get_back_keyboard,
)
from keyboards.keyboards import (
    get_listings_keyboard,
    get_price_range_keyboard,
    get_pagination_keyboard,
)
from states import SearchStates
from utils.helpers import (
    format_search_results_header,
    validate_price,
)
from config import PAGE_SIZE

logger = logging.getLogger(__name__)
router = Router(name="search")


# ==================== Search Menu ====================

@router.message(F.text == "/search")
async def cmd_search(message: Message, state: FSMContext):
    """Handle /search command."""
    await state.clear()
    await message.answer(
        "🔍 <b>Поиск объявлений</b>\n\n"
        "Как вы хотите искать?",
        reply_markup=get_search_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "search")
async def callback_search(callback: CallbackQuery, state: FSMContext):
    """Show search options."""
    await state.clear()
    await callback.message.edit_text(
        "🔍 <b>Поиск объявлений</b>\n\n"
        "Как вы хотите искать?",
        reply_markup=get_search_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Browse All Listings ====================

@router.callback_query(F.data == "browse")
async def browse_listings(callback: CallbackQuery, state: FSMContext):
    """Browse all listings."""
    await state.clear()
    await state.update_data(
        search_query=None,
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    
    await show_search_results(callback, state)


# ==================== Search by Keywords ====================

@router.callback_query(F.data == "search_keywords")
async def search_by_keywords(callback: CallbackQuery, state: FSMContext):
    """Start keyword search."""
    await state.set_state(SearchStates.waiting_for_query)
    await state.update_data(
        search_category=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    
    await callback.message.edit_text(
        "🔤 <b>Поиск по ключевым словам</b>\n\n"
        "Введите ключевые слова для поиска:\n\n"
        "<i>Пример: iPhone, кожаная куртка, велосипед</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    """Process search query."""
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer(
            "❌ Поисковый запрос слишком короткий. Введите минимум 2 символа.",
            reply_markup=get_cancel_keyboard(),
        )
        return
    
    await state.update_data(search_query=query, search_page=1)
    await state.set_state(SearchStates.browsing_results)
    
    # Create a fake callback to reuse show_search_results
    await show_search_results_message(message, state)


# ==================== Browse by Category ====================

@router.callback_query(F.data == "search_category")
async def search_by_category(callback: CallbackQuery, state: FSMContext):
    """Show category selection for search."""
    await state.update_data(
        search_query=None,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    
    await callback.message.edit_text(
        "📁 <b>Обзор по категориям</b>\n\n"
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(
            callback_prefix="browse_category",
            include_all=True,
            include_back=True,
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("browse_category:"))
async def process_category_browse(callback: CallbackQuery, state: FSMContext):
    """Process category selection."""
    category = callback.data.split(":")[1]
    
    if category == "all":
        await state.update_data(search_category=None)
    else:
        await state.update_data(search_category=category)
    
    await state.update_data(search_page=1)
    await state.set_state(SearchStates.browsing_results)
    
    await show_search_results(callback, state)


# ==================== Filter by Price ====================

@router.callback_query(F.data == "search_price")
async def search_by_price(callback: CallbackQuery, state: FSMContext):
    """Show price range options."""
    await callback.message.edit_text(
        "💰 <b>Фильтр по цене</b>\n\n"
        "Выберите диапазон цен:",
        reply_markup=get_price_range_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price_range:"))
async def process_price_range(callback: CallbackQuery, state: FSMContext):
    """Process price range selection."""
    range_str = callback.data.split(":")[1]
    
    if range_str == "custom":
        await state.set_state(SearchStates.waiting_for_min_price)
        await callback.message.edit_text(
            "💰 <b>Свой диапазон цен</b>\n\n"
            "Введите <b>минимальную</b> цену (или 0, если без минимума):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    
    parts = range_str.split(":")
    min_price = float(parts[0]) if parts[0] != "0" else None
    max_price = float(parts[1]) if parts[1] != "0" else None
    
    await state.update_data(
        search_min_price=min_price,
        search_max_price=max_price,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)
    
    await show_search_results(callback, state)


@router.message(SearchStates.waiting_for_min_price)
async def process_min_price(message: Message, state: FSMContext):
    """Process minimum price input."""
    is_valid, price, error = validate_price(message.text)
    
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\nПожалуйста, введите корректную минимальную цену:",
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(search_min_price=price if price > 0 else None)
    await state.set_state(SearchStates.waiting_for_max_price)

    await message.answer(
        "💰 <b>Свой диапазон цен</b>\n\n"
        "Введите <b>максимальную</b> цену (или 0, если без максимума):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(SearchStates.waiting_for_max_price)
async def process_max_price(message: Message, state: FSMContext):
    """Process maximum price input."""
    is_valid, price, error = validate_price(message.text)
    
    if not is_valid:
        await message.answer(
            f"❌ {error}\n\nПожалуйста, введите корректную максимальную цену:",
            reply_markup=get_cancel_keyboard(),
        )
        return
    
    await state.update_data(
        search_max_price=price if price > 0 else None,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)
    
    await show_search_results_message(message, state)


# ==================== Search Results ====================

async def show_search_results(callback: CallbackQuery, state: FSMContext):
    """Show search results for callback queries."""
    data = await state.get_data()
    
    query = data.get("search_query")
    category = data.get("search_category")
    min_price = data.get("search_min_price")
    max_price = data.get("search_max_price")
    page = data.get("search_page", 1)
    
    offset = (page - 1) * PAGE_SIZE
    
    # Get listings
    listings = await Listing.search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        limit=PAGE_SIZE,
        offset=offset,
    )
    
    total = await Listing.count_search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )
    
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 1
    
    # Build header
    text = format_search_results_header(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        total=total,
    )
    
    if not listings:
        text += "\n<i>Попробуйте другие фильтры или поисковые запросы.</i>"
        await callback.message.edit_text(
            text,
            reply_markup=get_search_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    
    text += "\n<i>Выберите объявление для просмотра:</i>"
    
    # Build keyboard with listings
    keyboard = get_listings_keyboard(listings)
    
    # Add pagination
    if total_pages > 1:
        # Build extra data for pagination callback
        extra_data = f"{query or ''}|{category or ''}|{min_price or ''}|{max_price or ''}"
        pagination = get_pagination_keyboard(page, total_pages, "search", extra_data)
        keyboard.inline_keyboard.extend(pagination.inline_keyboard)
    else:
        keyboard.inline_keyboard.append([
            {"text": "🔍 Новый поиск", "callback_data": "search"},
            {"text": "◀️ Меню", "callback_data": "back_to_menu"},
        ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


async def show_search_results_message(message: Message, state: FSMContext):
    """Show search results for message queries."""
    data = await state.get_data()
    
    query = data.get("search_query")
    category = data.get("search_category")
    min_price = data.get("search_min_price")
    max_price = data.get("search_max_price")
    page = data.get("search_page", 1)
    
    offset = (page - 1) * PAGE_SIZE
    
    # Get listings
    listings = await Listing.search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        limit=PAGE_SIZE,
        offset=offset,
    )
    
    total = await Listing.count_search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )
    
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 1
    
    # Build header
    text = format_search_results_header(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        total=total,
    )
    
    if not listings:
        text += "\n<i>Попробуйте другие фильтры или поисковые запросы.</i>"
        await message.answer(
            text,
            reply_markup=get_search_keyboard(),
            parse_mode="HTML",
        )
        return
    
    text += "\n<i>Выберите объявление для просмотра:</i>"
    
    # Build keyboard with listings
    keyboard = get_listings_keyboard(listings)
    
    # Add pagination
    if total_pages > 1:
        extra_data = f"{query or ''}|{category or ''}|{min_price or ''}|{max_price or ''}"
        pagination = get_pagination_keyboard(page, total_pages, "search", extra_data)
        keyboard.inline_keyboard.extend(pagination.inline_keyboard)
    else:
        keyboard.inline_keyboard.append([
            {"text": "🔍 Новый поиск", "callback_data": "search"},
            {"text": "◀️ Меню", "callback_data": "back_to_menu"},
        ])
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# ==================== Pagination ====================

@router.callback_query(F.data.startswith("search:page:"))
async def search_pagination(callback: CallbackQuery, state: FSMContext):
    """Handle search pagination."""
    parts = callback.data.split(":")
    page = int(parts[2])
    extra_data = parts[3] if len(parts) > 3 else ""
    
    # Parse extra data
    if extra_data:
        extra_parts = extra_data.split("|")
        query = extra_parts[0] if extra_parts[0] else None
        category = extra_parts[1] if len(extra_parts) > 1 and extra_parts[1] else None
        min_price = float(extra_parts[2]) if len(extra_parts) > 2 and extra_parts[2] else None
        max_price = float(extra_parts[3]) if len(extra_parts) > 3 and extra_parts[3] else None
        
        await state.update_data(
            search_query=query,
            search_category=category,
            search_min_price=min_price,
            search_max_price=max_price,
        )
    
    await state.update_data(search_page=page)
    await show_search_results(callback, state)


# ==================== Category Selection from Browse ====================

@router.callback_query(F.data.startswith("category:"))
async def category_from_main(callback: CallbackQuery, state: FSMContext):
    """Handle category selection from main browse."""
    category = callback.data.split(":")[1]
    
    await state.update_data(
        search_query=None,
        search_category=None if category == "all" else category,
        search_min_price=None,
        search_max_price=None,
        search_page=1,
    )
    await state.set_state(SearchStates.browsing_results)
    
    await show_search_results(callback, state)
