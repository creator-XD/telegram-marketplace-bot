"""
Finite State Machine (FSM) states for handling conversation flows.
"""
from aiogram.fsm.state import State, StatesGroup


class ListingStates(StatesGroup):
    """States for listing creation and editing."""
    # Creating a new listing
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_photos = State()
    waiting_for_location = State()
    confirm_listing = State()
    
    # Editing an existing listing
    editing_select_field = State()
    editing_title = State()
    editing_description = State()
    editing_price = State()
    editing_category = State()
    editing_photos = State()


class SearchStates(StatesGroup):
    """States for search and filtering."""
    waiting_for_query = State()
    waiting_for_category = State()
    waiting_for_price_range = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    browsing_results = State()


class MessageStates(StatesGroup):
    """States for buyer-seller communication."""
    waiting_for_message = State()
    waiting_for_reply = State()


class ProfileStates(StatesGroup):
    """States for profile editing."""
    editing_phone = State()
    editing_location = State()
    editing_bio = State()


class ReviewStates(StatesGroup):
    """States for leaving seller reviews."""
    waiting_for_rating = State()
    waiting_for_comment = State()


class AdminStates(StatesGroup):
    """States for admin operations."""
    # User management
    blocking_user = State()
    warning_user = State()
    editing_user_profile = State()

    # Listing management
    flagging_listing = State()
    editing_listing = State()
    deleting_listing = State()

    # Analytics filtering
    filtering_analytics = State()
