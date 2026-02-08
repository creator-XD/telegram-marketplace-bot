"""
Review management handlers for admin panel.
"""
from math import ceil
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import User, Review
from database.admin_models import AdminUser, AdminAuditLog
from keyboards.admin_keyboards import (
    get_admin_reviews_keyboard,
    get_admin_review_actions_keyboard,
    get_admin_review_list_keyboard,
    get_admin_confirm_keyboard,
    get_back_to_admin_keyboard,
)
from utils.decorators import require_admin, require_permission
from utils.helpers import escape_html, safe_edit_or_answer
from config import ADMIN_PAGE_SIZE
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_reviews")


# ---------- Reviews menu ----------

@router.callback_query(F.data == "admin_reviews")
@require_admin
async def admin_reviews_menu(callback: CallbackQuery, admin: AdminUser):
    """Show admin reviews management menu."""
    await safe_edit_or_answer(
        callback,
        "⭐ <b>Управление отзывами</b>\n\nВыберите действие:",
        reply_markup=get_admin_reviews_keyboard(),
    )
    await callback.answer()


# ---------- Reviews list ----------

async def _render_review_list(callback: CallbackQuery, page: int):
    """Fetch and display a paginated review list."""
    total = await Review.count_all()
    total_pages = max(1, ceil(total / ADMIN_PAGE_SIZE))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * ADMIN_PAGE_SIZE

    reviews = await Review.get_all_admin(limit=ADMIN_PAGE_SIZE, offset=offset)

    text = f"⭐ <b>Все отзывы</b>\nВсего: {total}\n\n"

    if not reviews:
        text += "<i>Отзывы не найдены.</i>"
        await safe_edit_or_answer(callback, text, reply_markup=get_back_to_admin_keyboard())
        return

    text += "Нажмите на отзыв для подробностей:"

    keyboard = get_admin_review_list_keyboard(reviews, page, total_pages)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)


@router.callback_query(F.data == "admin_reviews:all")
@require_admin
async def admin_reviews_list(callback: CallbackQuery, admin: AdminUser):
    """Show all reviews (page 1)."""
    await _render_review_list(callback, page=1)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_reviews_pg:"))
@require_admin
async def admin_reviews_page(callback: CallbackQuery, admin: AdminUser):
    """Handle review list pagination."""
    # admin_reviews_pg:all:page:{num}
    parts = callback.data.split(":")
    if len(parts) < 4 or parts[2] != "page":
        await callback.answer()
        return
    try:
        page = int(parts[3])
    except (ValueError, IndexError):
        page = 1
    await _render_review_list(callback, page=page)
    await callback.answer()


# ---------- Review detail ----------

@router.callback_query(F.data.startswith("admin_view_review:"))
@require_admin
async def admin_view_review(callback: CallbackQuery, admin: AdminUser):
    """Show detailed view for a single review."""
    try:
        review_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer("Отзыв не найден", show_alert=True)
        return

    reviewer = await User.get_by_id(review.reviewer_id)
    seller = await User.get_by_id(review.seller_id)

    stars = "⭐" * review.rating
    reviewer_name = escape_html(reviewer.display_name) if reviewer else f"#{review.reviewer_id}"
    seller_name = escape_html(seller.display_name) if seller else f"#{review.seller_id}"

    text = (
        f"⭐ <b>Отзыв #{review.id}</b>\n\n"
        f"<b>Оценка:</b> {stars} ({review.rating}/5)\n"
        f"<b>Автор:</b> {reviewer_name} (ID: {review.reviewer_id})\n"
        f"<b>Продавец:</b> {seller_name} (ID: {review.seller_id})\n"
    )

    if review.listing_id:
        text += f"<b>Объявление ID:</b> {review.listing_id}\n"

    if review.comment:
        text += f"\n<b>Комментарий:</b>\n{escape_html(review.comment)}\n"

    if review.created_at:
        date_str = str(review.created_at)[:19]
        text += f"\n<b>Дата:</b> {date_str}"

    keyboard = get_admin_review_actions_keyboard(review.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


# ---------- Delete review ----------

@router.callback_query(F.data.startswith("admin_review_delete:"))
@require_admin
@require_permission("manage_listings")
async def admin_review_delete_start(callback: CallbackQuery, admin: AdminUser):
    """Ask for confirmation before deleting a review."""
    try:
        review_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer("Отзыв не найден", show_alert=True)
        return

    stars = "⭐" * review.rating
    text = (
        f"🗑️ <b>Удаление отзыва</b>\n\n"
        f"Оценка: {stars}\n"
        f"ID отзыва: {review.id}\n\n"
        f"Вы уверены, что хотите удалить этот отзыв?"
    )
    keyboard = get_admin_confirm_keyboard("review_delete", review.id)
    await safe_edit_or_answer(callback, text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm:review_delete:"))
@require_admin
@require_permission("manage_listings")
async def admin_review_delete_confirm(callback: CallbackQuery, admin: AdminUser):
    """Execute review deletion."""
    try:
        review_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Неверный ID", show_alert=True)
        return

    review = await Review.get_by_id(review_id)
    if not review:
        await callback.answer("Отзыв не найден", show_alert=True)
        return

    seller_id = review.seller_id
    rating = review.rating
    success = await Review.delete(review_id, seller_id)

    if success:
        await AdminAuditLog.create(
            admin_id=admin.user_id,
            action="review_delete",
            target_type="review",
            target_id=review_id,
            details={
                "seller_id": seller_id,
                "reviewer_id": review.reviewer_id,
                "rating": rating,
            },
        )

        logger.info(f"Admin {admin.user_id} deleted review {review_id}")

        await safe_edit_or_answer(
            callback,
            f"🗑️ Отзыв #{review_id} удалён.",
            reply_markup=get_back_to_admin_keyboard(),
        )
    else:
        await safe_edit_or_answer(
            callback,
            "❌ Не удалось удалить отзыв.",
            reply_markup=get_back_to_admin_keyboard(),
        )
    await callback.answer()


# ---------- Cancel review confirmation ----------

@router.callback_query(F.data.startswith("admin_cancel:review_delete:"))
@require_admin
async def admin_cancel_review_action(callback: CallbackQuery, admin: AdminUser):
    """Cancel a pending review deletion — return to review detail."""
    parts = callback.data.split(":")
    if len(parts) >= 3:
        try:
            review_id = int(parts[-1])
        except ValueError:
            review_id = None

        if review_id:
            review = await Review.get_by_id(review_id)
            if review:
                reviewer = await User.get_by_id(review.reviewer_id)
                seller = await User.get_by_id(review.seller_id)

                stars = "⭐" * review.rating
                reviewer_name = escape_html(reviewer.display_name) if reviewer else f"#{review.reviewer_id}"
                seller_name = escape_html(seller.display_name) if seller else f"#{review.seller_id}"

                text = (
                    f"⭐ <b>Отзыв #{review.id}</b>\n\n"
                    f"<b>Оценка:</b> {stars} ({review.rating}/5)\n"
                    f"<b>Автор:</b> {reviewer_name} (ID: {review.reviewer_id})\n"
                    f"<b>Продавец:</b> {seller_name} (ID: {review.seller_id})\n"
                )
                if review.listing_id:
                    text += f"<b>Объявление ID:</b> {review.listing_id}\n"
                if review.comment:
                    text += f"\n<b>Комментарий:</b>\n{escape_html(review.comment)}\n"
                if review.created_at:
                    date_str = str(review.created_at)[:19]
                    text += f"\n<b>Дата:</b> {date_str}"

                keyboard = get_admin_review_actions_keyboard(review.id)
                await safe_edit_or_answer(callback, text, reply_markup=keyboard)
                await callback.answer()
                return

    await safe_edit_or_answer(
        callback,
        "Действие отменено.",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()
