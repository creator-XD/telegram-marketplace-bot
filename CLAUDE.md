# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram Marketplace Bot - A prototype Telegram bot for buying and selling goods and services, built with Python and aiogram 3.x. Uses SQLite for storage with PostgreSQL migration path for production scaling.

## Development Commands

### Running the bot
```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Unix/Mac)
source .venv/bin/activate

# Run the bot
python bot.py
```

### Dependencies
```bash
# Install/update dependencies
pip install -r requirements.txt

# If switching to PostgreSQL, uncomment asyncpg in requirements.txt first
```

### Database
The database is automatically initialized on first run. SQLite file: `marketplace.db`

## Architecture

### Bot Initialization Flow
1. `bot.py` - Main entry point creates Bot and Dispatcher instances
2. FSM storage: Uses `MemoryStorage` (for production, consider Redis)
3. On startup: Database initialized via `database/db.py:get_db()`, bot commands menu set
4. Router registration: All routers from `handlers/__init__.py:get_all_routers()` are included
5. Polling starts with automatic update type resolution

### Handler Router Priority
Routers are registered in this order (earlier = higher priority):
1. `listings_router` - Listing CRUD operations
2. `search_router` - Search and filtering
3. `messages_router` - Buyer-seller communication
4. `profile_router` - User profile management
5. `common_router` - Catch-all for /start, /help, /cancel

### Database Architecture
- Uses dataclass models with class methods for all database operations
- All models in `database/models.py` follow the pattern: `from_row()`, `get_by_id()`, `create()`, `update()`
- Database wrapper in `database/db.py` provides `execute()`, `fetch_one()`, `fetch_all()`
- Foreign keys enforced with CASCADE deletes for data integrity
- Indexes on frequently queried columns (user_id, category, status, price)

### State Machine Flow (FSM)
The bot uses aiogram's FSM for multi-step conversations. States defined in `states/states.py`:
- `ListingStates` - Creating/editing listings (7 creation states, 5 editing states)
- `SearchStates` - Search flow with filters (5 states)
- `MessageStates` - Buyer-seller messaging (2 states)
- `ProfileStates` - Profile editing (3 states)

When adding new multi-step flows, create a new `StatesGroup` class in `states/states.py`.

### User Management
- Users auto-created on first `/start` via `User.get_or_create()`
- User info updated on each interaction to keep username/name in sync
- All handlers receive user via `message.from_user` or `callback.from_user`

### Listing Status Flow
Listings have status field: `active` → `sold` | `reserved` | `deleted`
- Only `active` listings appear in search/browse
- Soft delete pattern: status set to `deleted`, never actually removed
- Views counter incremented on detail view

### Callback Data Patterns
- Simple actions: `"action"` (e.g., `"help"`, `"cancel"`)
- With ID: `"action:id"` (e.g., `"view_listing:123"`)
- Pagination: `"action:page"` (e.g., `"browse:2"`)
- With multiple params: `"action:param1:param2"` (e.g., `"edit_listing:123:title"`)

Parse callbacks using `F.data.startswith("prefix:")` or `F.data == "exact"`.

### Keyboard Construction
All keyboards in `keyboards/keyboards.py`. Use `InlineKeyboardBuilder` for inline keyboards.
- Main menu: `get_main_menu_keyboard()` - central navigation hub
- Categories: `get_categories_keyboard()` - grid layout from `config.CATEGORIES`
- Pagination: `get_pagination_keyboard()` - standard prev/next with page indicator

## Configuration

All settings in `config.py`:
- `BOT_TOKEN` - Telegram bot token (from @BotFather)
- `DATABASE_URL` - SQLite path or PostgreSQL URL
- `CATEGORIES` - List of dicts with id/name/emoji for product categories
- `MESSAGES` - Message templates with Russian text
- `FEATURES` - Feature flags for planned functionality
- `PAYMENT_CONFIG` - Placeholder for future payment integration

## Key Design Patterns

### Database Query Patterns
- List by user: `Listing.get_by_user(user_id, status="active")`
- Search with filters: `Listing.search(query=q, category=cat, min_price=min, max_price=max)`
- Count results: `Listing.count_search(...)` - use for pagination
- Recent listings: `Listing.get_recent(limit=10)`

### Photo Management
- Photos stored separately in `listing_photos` table
- `is_primary` flag marks main photo (shown in listings)
- Use `ListingPhoto.create()` for each uploaded photo
- Auto-load photos: `listing = await Listing.get_by_id(id, with_photos=True)`

### Error Handling
- Database errors should be caught at handler level
- Use try/except around `Listing.create()`, `User.update()`, etc.
- Return user-friendly messages on failure
- Log exceptions with `logger.exception()`

## Common Tasks

### Adding a new handler
1. Create handler function in appropriate `handlers/*.py` file
2. Decorate with `@router.message()` or `@router.callback_query()`
3. Import and use FSM states if multi-step flow needed
4. Router auto-registered via `get_all_routers()`

### Adding a new listing field
1. Add column in `database/db.py:init_tables()` ALTER TABLE or add to CREATE TABLE
2. Add field to `Listing` dataclass in `database/models.py`
3. Update `Listing.from_row()` to include new field
4. Add to `Listing.create()` and `Listing.update()` as needed
5. Add FSM state in `ListingStates` if user input required
6. Update handlers in `handlers/listings.py`

### Migrating to PostgreSQL
1. Install `asyncpg`: `pip install asyncpg`
2. Update `DATABASE_URL` in `config.py` to PostgreSQL connection string
3. Replace `aiosqlite` imports with `asyncpg` in `database/db.py`
4. Update `Database.connect()` to use `asyncpg.connect()`
5. Adjust row factory (asyncpg uses different interface)
6. Update SQL syntax if needed (TIMESTAMP vs DATETIME, etc.)

## Language and Localization

Bot currently uses Russian language in:
- `config.MESSAGES` - All user-facing message templates
- `config.CATEGORIES` - Category names with emojis
- Handler responses in `handlers/*.py`

To add multilingual support, create a translation system and update message templates accordingly.

## Scalability Notes

- FSM storage currently in-memory (lost on restart) - switch to Redis for production
- SQLite suitable for prototype/small scale - PostgreSQL recommended for production
- All handlers are async-ready for concurrent request handling
- Database indexes already in place for common queries
- Photos stored by Telegram file_id (no local file storage needed)
