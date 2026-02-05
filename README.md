# Telegram Marketplace Bot

A Telegram bot for buying and selling goods and services, built with Python and aiogram 3.x. Features a full admin panel with user/listing management, audit logging, and role-based access control.

> **Language / Язык:** [Русская версия (README_RU.md)](README_RU.md)

## Features

### User Features
- **User Management** — Automatic registration on `/start`, profile editing (phone, location, bio)
- **Listing Management** — Create, edit, delete, and mark listings as sold; supports up to 5 photos per listing
- **Search & Filtering** — Keyword search, category browsing, price range filters, pagination
- **Categories** — 10 product categories with emoji icons (electronics, clothing, home, vehicles, services, jobs, pets, sports, books, other)
- **Buyer-Seller Messaging** — Direct communication between users through the bot
- **Favorites** — Save and manage interesting listings
- **Welcome Image** — Visual main menu with a branded welcome image

### Admin Panel
- **Dashboard** — Real-time statistics: users (total, active, blocked, verified, new today/week), listings (total, active, sold, flagged, new today/week), transactions
- **User Management** — View/filter users (all, active, blocked, verified), block/unblock with reasons, issue warnings (low/medium/high severity), view warning history, view user listings
- **Listing Management** — View/filter listings (all, active, flagged, deleted), flag/unflag inappropriate content with reasons, delete listings, view seller info
- **Audit Log** — Automatic logging of all admin actions with filtering (blocks, warnings, deletions, edits) and pagination
- **Role-Based Access** — Three roles (super_admin, admin, moderator) with granular permissions
- **Security** — Three-layer auth: environment whitelist → database role verification → permission checks

### Planned (Future)
- Payment system integration (placeholder implemented)
- Secure escrow transactions
- Seller ratings and reviews
- Product delivery tracking
- Analytics dashboard with charts

## Project Structure

```
telegram_marketplace_bot/
├── bot.py                          # Main entry point
├── config.py                       # Configuration & settings
├── requirements.txt                # Dependencies
├── .env                            # Environment variables (not in git)
├── .env.example                    # Environment template
│
├── assets/
│   └── images/
│       └── menu.jpg                # Welcome menu image
│
├── database/
│   ├── __init__.py
│   ├── db.py                       # Database connection & initialization (SQLite)
│   ├── models.py                   # Core models (User, Listing, ListingPhoto, Favorite, Message, Transaction)
│   └── admin_models.py             # Admin models (AdminUser, AdminAuditLog, UserWarning)
│
├── handlers/
│   ├── __init__.py                 # Router registration & ordering
│   ├── common.py                   # /start, /help, /cancel, main menu
│   ├── listings.py                 # Listing CRUD operations
│   ├── search.py                   # Search & category browsing
│   ├── messages.py                 # Buyer-seller communication
│   ├── profile.py                  # User profile management
│   └── admin/
│       ├── __init__.py
│       ├── admin_router.py         # Admin panel entry & dashboard
│       ├── user_management.py      # User blocking, warnings, viewing
│       ├── listing_management.py   # Listing flagging, deletion
│       ├── transaction_management.py  # Transaction viewing (stub)
│       ├── analytics.py            # Analytics views (stub)
│       └── audit.py                # Audit log viewer with filters
│
├── keyboards/
│   ├── __init__.py
│   ├── keyboards.py                # User-facing keyboards
│   └── admin_keyboards.py          # Admin panel keyboards
│
├── states/
│   ├── __init__.py
│   └── states.py                   # FSM states (Listing, Search, Message, Profile, Admin)
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py                  # Formatting, validation, utility functions
│   ├── decorators.py               # @require_admin, @require_permission
│   └── admin_helpers.py            # Admin-specific formatting
│
├── middleware/
│   ├── __init__.py
│   ├── admin_auth.py               # Admin authentication middleware
│   └── audit_logger.py             # Automatic audit logging middleware
│
├── create_admin.py                 # Script to create the first admin user
├── check_admin_setup.py            # Diagnostic tool for admin setup
└── migrate_database.py             # Database migration utility
```

## Installation

1. **Clone the repository**

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root (see `.env.example`):
   ```env
   BOT_TOKEN=your_bot_token_from_botfather
   ADMIN_TELEGRAM_IDS=123456789,987654321
   SUPER_ADMIN_ID=123456789
   ```

5. **Run the bot**:
   ```bash
   python bot.py
   ```

6. **Set up the first admin** (after the admin user has sent `/start` to the bot):
   ```bash
   python create_admin.py
   ```

## Configuration

All settings are in `config.py`, with sensitive values loaded from `.env`:

| Setting | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token (from @BotFather) | Required |
| `DATABASE_URL` | Database connection string | `marketplace.db` (SQLite) |
| `ADMIN_TELEGRAM_IDS` | Comma-separated admin Telegram IDs | Empty |
| `SUPER_ADMIN_ID` | Super admin Telegram ID | None |
| `MAX_PHOTOS` | Max photos per listing | 5 |
| `MAX_TITLE_LENGTH` | Max listing title length | 100 |
| `MAX_DESCRIPTION_LENGTH` | Max listing description length | 2000 |
| `MIN_PRICE` / `MAX_PRICE` | Price range limits | 0.01 – 1,000,000 |
| `PAGE_SIZE` | Items per page (user views) | 5 |
| `ADMIN_PAGE_SIZE` | Items per page (admin views) | 10 |
| `CURRENCY` | Display currency symbol | `$` |

## Database

### Engine
SQLite by default (`marketplace.db`, auto-created on first run). Migration path to PostgreSQL is available.

### Schema

| Table | Description |
|---|---|
| `users` | User accounts, profiles, verification status, suspension info, warning count |
| `listings` | Product/service listings with status, views, flag support |
| `listing_photos` | Photos for listings (Telegram file_id, primary flag) |
| `favorites` | User-saved listings |
| `messages` | Buyer-seller communication with read status |
| `transactions` | Payment transactions (placeholder) |
| `admin_users` | Admin roles and permissions (JSON) |
| `admin_audit_log` | Audit trail for all admin actions |
| `user_warnings` | Warnings issued to users with severity levels |

### Switching to PostgreSQL
1. Install `asyncpg`: `pip install asyncpg`
2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/marketplace
   ```
3. Update database driver in `database/db.py`

## Usage

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot, show main menu with welcome image |
| `/search` | Search for listings |
| `/mylistings` | View your listings |
| `/favorites` | View saved listings |
| `/profile` | View/edit your profile |
| `/help` | Show help information |
| `/cancel` | Cancel current operation |
| `/admin` | Open admin panel (admin users only) |

### For Buyers
1. `/start` to register and see the main menu
2. Browse listings or use search with filters
3. Filter by category, keywords, or price range
4. Contact the seller directly through the bot
5. Save interesting items to favorites

### For Sellers
1. Go to "My Listings" → "Add New Listing"
2. Follow the prompts: title → description → price → category → photos → location
3. Manage your listings (edit, delete, mark as sold)
4. Respond to buyer inquiries

### Admin Panel
1. Ensure your Telegram ID is in `ADMIN_TELEGRAM_IDS` in `.env`
2. Send `/start` to the bot, then run `python create_admin.py`
3. Use `/admin` to access the admin panel
4. Navigate: Dashboard, Users, Listings, Audit Log

#### Admin Roles

| Role | Permissions |
|---|---|
| `super_admin` | All permissions including admin management |
| `admin` | All permissions except admin management |
| `moderator` | Manage listings, warn users, view analytics, edit listings |

## Architecture

### Handler Router Priority
Routers are registered in this order (earlier = higher priority):
1. `admin_router` — Admin panel and all sub-routers
2. `listings_router` — Listing CRUD operations
3. `search_router` — Search and filtering
4. `messages_router` — Buyer-seller communication
5. `profile_router` — User profile management
6. `common_router` — Catch-all (/start, /help, /cancel)

### FSM States
- **ListingStates** — 7 creation + 5 editing states
- **SearchStates** — 5 search flow states
- **MessageStates** — 2 messaging states
- **ProfileStates** — 3 profile editing states
- **AdminStates** — 6 admin operation states (blocking, warning, flagging, editing, deleting, filtering)

### Middleware
- **AdminAuthMiddleware** — Runs on every message/callback, injects `admin` and `is_admin` into handler data
- **AuditLoggerMiddleware** — Automatically logs admin actions after handler execution

### Callback Data Patterns
- Simple: `"action"` (e.g., `"help"`, `"cancel"`)
- With ID: `"action:id"` (e.g., `"view_listing:123"`)
- Pagination: `"action:page"` (e.g., `"browse:2"`)
- Multi-param: `"action:param1:param2"` (e.g., `"admin_warn_severity:123:high"`)

## Tech Stack

| Component | Technology |
|---|---|
| Framework | aiogram 3.4.1 |
| Database | SQLite (aiosqlite) |
| Config | python-dotenv |
| Language | Python 3.11+ |
| Concurrency | Fully async/await |

## Scalability Notes

- **Database**: Ready for PostgreSQL migration
- **FSM Storage**: In-memory (switch to Redis for production persistence)
- **Modular Architecture**: Separated handlers, keyboards, models, middleware
- **Async**: All handlers and database operations are async
- **Indexes**: Pre-configured on frequently queried columns
- **Photos**: Stored by Telegram file_id (no local storage needed)

## License

MIT License — feel free to use and modify as needed.
