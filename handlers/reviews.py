"""
Handlers for seller reviews and feedback.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.models import User, Listing, Review
from keyboards import (
    get_rating_keyboard,
    get_review_comment_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_pagination_keyboard,
    get_confirm_keyboard,
)
from states import ReviewStates
from utils import format_review_text, escape_html
from utils.helpers import safe_edit_or_answer
from config import PAGE_SIZE

logger = logging.getLogger(__name__)
router = Router(name="reviews")

REVIEWS_PER_PAGE = PAGE_SIZE


# ==================== Leave Review ====================

@router.callback_query(F.data.startswith("leave_review:"))
async def leave_review(callback: CallbackQuery, state: FSMContext):
    """Start the review flow for a listing's seller."""
    listing_id = int(callback.data.split(":")[1])

    user = await User.get_by_telegram_id(callback.from_user.id)
    listing = await Listing.get_by_id(listing_id, with_user=True)

    if not listing:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return

    # Can't review yourself
    if listing.user_id == user.id:
        await callback.answer("Вы не можете оставить отзыв о себе.", show_alert=True)
        return

    # Check if already reviewed this listing
    existing = await Review.get_by_reviewer_and_listing(user.id, listing_id)
    if existing:
        await callback.answer("Вы уже оставили отзыв на это объявление.", show_alert=True)
        return

    await state.set_state(ReviewStates.waiting_for_rating)
    await state.update_data(listing_id=listing_id, seller_id=listing.user_id)

    seller_name = escape_html(listing.user.display_name) if listing.user else "продавца"

    await safe_edit_or_answer(
        callback,
        f"⭐ <b>Отзыв о продавце {seller_name}</b>\n\n"
        f"Объявление: <b>{escape_html(listing.title)}</b>\n\n"
        f"Выберите оценку от 1 до 5 звёзд:",
        reply_markup=get_rating_keyboard(listing_id),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Process Rating ====================

@router.callback_query(F.data.startswith("review_rating:"), ReviewStates.waiting_for_rating)
async def process_rating(callback: CallbackQuery, state: FSMContext):
    """Process the star rating selection."""
    parts = callback.data.split(":")
    rating = int(parts[1])
    listing_id = int(parts[2])

    await state.update_data(rating=rating, listing_id=listing_id)
    await state.set_state(ReviewStates.waiting_for_comment)

    stars = "⭐" * rating

    await safe_edit_or_answer(
        callback,
        f"Ваша оценка: {stars} ({rating}/5)\n\n"
        f"Напишите комментарий к отзыву или нажмите «Пропустить»:",
        reply_markup=get_review_comment_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Process Comment ====================

@router.message(ReviewStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    """Process the review comment text."""
    comment = message.text.strip() if message.text else None

    if comment and len(comment) > 500:
        await message.answer(
            "❌ Комментарий слишком длинный. Ограничьте его 500 символами:",
            reply_markup=get_review_comment_keyboard(),
        )
        return

    data = await state.get_data()
    await state.clear()

    user = await User.get_by_telegram_id(message.from_user.id)
    review = await Review.create(
        reviewer_id=user.id,
        seller_id=data["seller_id"],
        listing_id=data["listing_id"],
        rating=data["rating"],
        comment=comment,
    )

    if review:
        stars = "⭐" * data["rating"]
        await message.answer(
            f"✅ <b>Отзыв сохранён!</b>\n\n"
            f"Оценка: {stars}\n"
            f"{('Комментарий: ' + escape_html(comment)) if comment else ''}",
            reply_markup=get_back_keyboard("back_to_menu"),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "❌ Не удалось сохранить отзыв. Возможно, вы уже оставляли отзыв на это объявление.",
            reply_markup=get_back_keyboard("back_to_menu"),
            parse_mode="HTML",
        )


# ==================== Skip Comment ====================

@router.callback_query(F.data == "skip_review_comment", ReviewStates.waiting_for_comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    """Skip comment and save review with rating only."""
    data = await state.get_data()
    await state.clear()

    user = await User.get_by_telegram_id(callback.from_user.id)
    review = await Review.create(
        reviewer_id=user.id,
        seller_id=data["seller_id"],
        listing_id=data["listing_id"],
        rating=data["rating"],
    )

    if review:
        stars = "⭐" * data["rating"]
        await safe_edit_or_answer(
            callback,
            f"✅ <b>Отзыв сохранён!</b>\n\n"
            f"Оценка: {stars}",
            reply_markup=get_back_keyboard("back_to_menu"),
            parse_mode="HTML",
        )
    else:
        await safe_edit_or_answer(
            callback,
            "❌ Не удалось сохранить отзыв. Возможно, вы уже оставляли отзыв на это объявление.",
            reply_markup=get_back_keyboard("back_to_menu"),
            parse_mode="HTML",
        )
    await callback.answer()


# ==================== View Seller Reviews ====================

@router.callback_query(F.data.startswith("seller_reviews:"))
async def view_seller_reviews(callback: CallbackQuery, state: FSMContext):
    """Show seller reviews with pagination."""
    parts = callback.data.split(":")

    # Handle paginated: seller_reviews:page:{page}:{seller_id}
    if len(parts) == 4 and parts[1] == "page":
        page = int(parts[2])
        seller_id = int(parts[3])
    else:
        # Simple: seller_reviews:{seller_id}
        seller_id = int(parts[1])
        page = 1

    seller = await User.get_by_id(seller_id)
    if not seller:
        await callback.answer("Продавец не найден.", show_alert=True)
        return

    total = await Review.count_by_seller(seller_id)

    if total == 0:
        await safe_edit_or_answer(
            callback,
            f"⭐ <b>Отзывы о {escape_html(seller.display_name)}</b>\n\n"
            f"Пока нет отзывов.",
            reply_markup=get_back_keyboard("back_to_menu"),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    total_pages = (total + REVIEWS_PER_PAGE - 1) // REVIEWS_PER_PAGE
    offset = (page - 1) * REVIEWS_PER_PAGE

    reviews = await Review.get_by_seller(seller_id, limit=REVIEWS_PER_PAGE, offset=offset)

    # Get current user to check which reviews belong to them
    current_user = await User.get_by_telegram_id(callback.from_user.id)

    avg_rating = seller.rating
    text = (
        f"⭐ <b>Отзывы о {escape_html(seller.display_name)}</b>\n"
        f"Средний рейтинг: {'⭐' * round(avg_rating)} {avg_rating:.1f} ({total} отзывов)\n\n"
    )

    for review in reviews:
        reviewer = await User.get_by_id(review.reviewer_id)
        text += format_review_text(review, reviewer) + "\n"

    # Build keyboard with delete buttons for own reviews + pagination
    builder = InlineKeyboardBuilder()

    for review in reviews:
        if current_user and review.reviewer_id == current_user.id:
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить мой отзыв",
                    callback_data=f"delete_review:{review.id}:{seller_id}"
                )
            )

    # Add pagination
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️ Пред.",
                    callback_data=f"seller_reviews:page:{page - 1}:{seller_id}"
                )
            )
        nav_buttons.append(
            InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop")
        )
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="След. ▶️",
                    callback_data=f"seller_reviews:page:{page + 1}:{seller_id}"
                )
            )
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")
    )

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


# ==================== Delete Review (User) ====================

@router.callback_query(F.data.startswith("delete_review:"))
async def delete_review_confirm(callback: CallbackQuery):
    """Ask for confirmation before deleting own review."""
    parts = callback.data.split(":")
    review_id = int(parts[1])
    seller_id = int(parts[2])

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer("Отзыв не найден.", show_alert=True)
        return

    # Verify ownership
    current_user = await User.get_by_telegram_id(callback.from_user.id)
    if not current_user or review.reviewer_id != current_user.id:
        await callback.answer("Вы можете удалять только свои отзывы.", show_alert=True)
        return

    stars = "⭐" * review.rating
    text = (
        f"🗑 <b>Удаление отзыва</b>\n\n"
        f"Оценка: {stars}\n"
    )
    if review.comment:
        text += f"Комментарий: {escape_html(review.comment)}\n"
    text += "\nВы уверены, что хотите удалить этот отзыв?"

    await safe_edit_or_answer(
        callback,
        text,
        reply_markup=get_confirm_keyboard(
            confirm_callback=f"confirm_delete_review:{review_id}:{seller_id}",
            cancel_callback=f"seller_reviews:{seller_id}",
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_review:"))
async def confirm_delete_review(callback: CallbackQuery):
    """Execute review deletion after confirmation."""
    parts = callback.data.split(":")
    review_id = int(parts[1])
    seller_id = int(parts[2])

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer("Отзыв не найден.", show_alert=True)
        return

    # Verify ownership again
    current_user = await User.get_by_telegram_id(callback.from_user.id)
    if not current_user or review.reviewer_id != current_user.id:
        await callback.answer("Вы можете удалять только свои отзывы.", show_alert=True)
        return

    success = await Review.delete(review_id, seller_id)

    if success:
        await safe_edit_or_answer(
            callback,
            "✅ Отзыв успешно удалён.",
            reply_markup=get_back_keyboard(f"seller_reviews:{seller_id}"),
            parse_mode="HTML",
        )
    else:
        await safe_edit_or_answer(
            callback,
            "❌ Не удалось удалить отзыв. Попробуйте позже.",
            reply_markup=get_back_keyboard(f"seller_reviews:{seller_id}"),
            parse_mode="HTML",
        )
    await callback.answer()
