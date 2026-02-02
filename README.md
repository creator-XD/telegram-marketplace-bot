# Telegram Marketplace Bot

*[English](#) | [Русский](README.ru.md)*

A Telegram bot for buying and selling goods and services, built with Python and aiogram 3.x.

## Features

### Current Features
- **User Management**: Automatic user registration and profile management
- **Listing Management**: Create, edit, and delete product listings with photos
- **Search & Filtering**: Search by keywords, filter by category and price range
- **Categories**: Organize products into categories (Electronics, Clothing, Home & Garden, etc.)
- **Communication**: Direct messaging between buyers and sellers via Telegram
- **Favorites**: Save interesting listings for later
- **Admin Panel**: Full-featured admin panel with dashboard, user management, and audit logging

### Admin Panel Features
- **Dashboard**: Real-time statistics (users, listings, transactions)
- **User Management**: Block/unblock users, issue warnings, view user activity
- **Listing Management**: Flag/unflag inappropriate content, edit/delete listings
- **Role-Based Access**: Super Admin, Admin, and Moderator roles with different permissions
- **Audit Logging**: Automatic logging of all admin actions
- **Security**: Multi-layer authentication with Telegram ID whitelist

### Planned (Future Expansion)
- Payment system integration (placeholder implemented)
- Secure escrow transactions
- Seller ratings and reviews
- Product delivery tracking
- Multimedia content support
- API integrations
- Advanced analytics and reporting

## Project Structure

```
telegram_marketplace_bot/
├── bot.py                          # Main bot entry point
├── config.py                       # Configuration settings
├── .env                            # Environment variables (BOT_TOKEN, ADMIN_IDS)
├── .env.example                    # Example environment file
├── database/
│   ├── __init__.py
│   ├── db.py                       # Database connection and initialization
│   ├── models.py                   # User, Listing, Message models
│   └── admin_models.py             # Admin models (AdminUser, AuditLog, Warnings)
├── handlers/
│   ├── __init__.py
│   ├── common.py                   # Common handlers (start, help, cancel)
│   ├── listings.py                 # Listing management handlers
│   ├── search.py                   # Search and filtering handlers
│   ├── messages.py                 # Buyer-seller communication handlers
│   ├── profile.py                  # User profile handlers
│   └── admin/                      # Admin panel handlers
│       ├── __init__.py
│       ├── dashboard.py            # Admin dashboard
│       ├── user_management.py      # User moderation
│       ├── listing_management.py   # Listing moderation
│       ├── transaction_management.py
│       ├── analytics.py            # Statistics & analytics
│       └── audit.py                # Audit log viewer
├── keyboards/
│   ├── __init__.py
│   └── keyboards.py                # Inline and reply keyboards
├── middleware/
│   ├── __init__.py
│   ├── admin_auth.py               # Admin authentication middleware
│   └── audit_logger.py             # Audit logging middleware
├── states/
│   ├── __init__.py
│   └── states.py                   # FSM states for conversations
├── utils/
│   ├── __init__.py
│   └── helpers.py                  # Utility functions
├── create_admin.py                 # Script to create admin users
├── check_admin_setup.py            # Admin setup verification tool
├── migrate_database.py             # Database migration utility
├── requirements.txt                # Project dependencies
├── CLAUDE.md                       # Development guidelines for AI assistants
├── README.md                       # This file
├── QUICK_START.md                  # Quick start guide
├── ADMIN_README.md                 # Admin panel documentation
├── ADMIN_SETUP_COMPLETE.md         # Admin setup guide
└── ADMIN_IMPLEMENTATION_STATUS.md  # Admin implementation status
```

## Installation

1. **Clone/Download the project**

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env  # On Windows: copy .env.example .env
     ```
   - Edit `.env` and add your configuration:
     ```env
     BOT_TOKEN=your_bot_token_from_botfather
     ADMIN_TELEGRAM_IDS=your_telegram_id
     SUPER_ADMIN_ID=your_telegram_id
     ```
   - Get a bot token from [@BotFather](https://t.me/BotFather)
   - Get your Telegram ID from [@userinfobot](https://t.me/userinfobot)

5. **Run the bot**:
   ```bash
   python bot.py
   ```
   The database will be created automatically on first run.

6. **Set up admin access** (optional):
   - Send `/start` to your bot in Telegram
   - Run the admin creation script:
     ```bash
     python create_admin.py
     ```
   - Access admin panel with `/admin` command

For detailed admin setup instructions, see [QUICK_START.md](QUICK_START.md).

## Configuration

### Environment Variables (.env)
- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `ADMIN_TELEGRAM_IDS`: Comma-separated list of admin Telegram IDs
- `SUPER_ADMIN_ID`: Telegram ID of the super admin
- `DATABASE_URL`: Database connection string (default: sqlite+aiosqlite:///./marketplace.db)

### Application Settings (config.py)
- `CATEGORIES`: Product categories with emojis
- `MAX_PHOTOS`: Maximum photos per listing (default: 5)
- `PAGE_SIZE`: Items per page in listings (default: 10)
- `MESSAGES`: Message templates in Russian
- `ADMIN_ROLES`: Admin permission levels
- `FEATURES`: Feature flags for planned functionality

## Database

The bot uses SQLite by default (`marketplace.db`) for simplicity. To switch to PostgreSQL:

1. Uncomment `asyncpg` in `requirements.txt` and install: `pip install asyncpg`
2. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/marketplace
   ```
3. Update the database wrapper in `database/db.py` to use asyncpg

### Database Schema

**Core Tables:**
- **users**: User accounts and profiles
- **listings**: Product/service listings
- **listing_photos**: Photos for listings (multiple per listing)
- **favorites**: User's saved listings
- **messages**: Communication between users
- **transactions**: Payment transactions (placeholder for future)

**Admin Tables:**
- **admin_users**: Admin accounts with roles and permissions
- **admin_audit_log**: Audit trail of all admin actions
- **user_warnings**: Warning system for user moderation

The database is automatically initialized on first run with all necessary tables and indexes.

## Usage

### For Buyers
1. `/start` - Start the bot
2. Browse listings or use search
3. Filter by category, keywords, or price
4. Contact seller directly through the bot
5. Save interesting items to favorites

### For Sellers
1. `/start` - Start the bot
2. Go to "My Listings" → "Add New Listing"
3. Follow the prompts to add title, description, price, category, and photos
4. Manage your listings (edit, delete, mark as sold)
5. Respond to buyer inquiries

### For Admins
1. Set up admin access (see Installation step 6)
2. Use `/admin` to access the admin panel
3. View dashboard for real-time statistics
4. Manage users: block spam accounts, issue warnings
5. Moderate listings: flag inappropriate content, edit or delete
6. Monitor activity through audit log
7. View detailed analytics

For complete admin documentation, see [ADMIN_README.md](ADMIN_README.md).

## Bot Commands

### User Commands
- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/search` - Search for listings
- `/mylistings` - View your listings
- `/favorites` - View saved listings
- `/profile` - View your profile
- `/cancel` - Cancel current operation

### Admin Commands
- `/admin` - Access admin panel (requires admin privileges)
  - View dashboard with statistics
  - Manage users (block, warn, view activity)
  - Manage listings (flag, edit, delete)
  - View transactions
  - View analytics
  - View audit log

## Scalability Considerations

This bot is built with scalability in mind:

1. **Database**: Easy migration from SQLite to PostgreSQL for production
2. **Modular Architecture**: Handlers, keyboards, models, and middleware are separated
3. **FSM (Finite State Machine)**: MemoryStorage for development, Redis-ready for production
4. **Async/Await**: Fully asynchronous for concurrent request handling
5. **Middleware System**: Admin authentication, audit logging, and extensible middleware
6. **Database Indexes**: Optimized queries on frequently accessed columns
7. **Environment Configuration**: Secure .env-based configuration
8. **Role-Based Access Control**: Flexible admin permission system
9. **Audit Logging**: Complete action tracking for security and compliance
10. **Dataclass Models**: Type-safe database operations with class methods

### Production Recommendations
- Switch to PostgreSQL for better concurrent access
- Use Redis for FSM storage (instead of MemoryStorage)
- Add rate limiting middleware
- Implement proper backup strategy
- Monitor audit logs regularly
- Set up logging infrastructure

## Future Enhancements

### Admin Panel (In Progress)
- ✅ Dashboard and statistics
- ✅ Authentication and role-based access
- ✅ Audit logging system
- 🔄 User management handlers (template ready)
- 🔄 Listing management handlers (template ready)
- 🔄 Transaction viewing
- 🔄 Advanced analytics views
- 🔄 Audit log viewer interface

### Payments & Transactions
1. **Payments**: Integrate Telegram Payments API or external gateways
2. **Escrow**: Implement secure transaction holding
3. **Reviews**: Add seller/buyer rating system

### Features
4. **Delivery**: Integrate with shipping APIs
5. **Multimedia**: Video and document support for listings
6. **Notifications**: Push notifications for price drops, new listings
7. **Localization**: Multi-language support
8. **Web Interface**: Web-based marketplace view
9. **API**: REST API for third-party integrations

### Infrastructure
10. **Redis**: FSM storage for production
11. **PostgreSQL**: Migration to production database
12. **Monitoring**: Logging, metrics, and alerting
13. **Backup**: Automated database backups

## Documentation

- **[README.md](README.md)** - This file, project overview (English)
- **[README.ru.md](README.ru.md)** - Project overview in Russian
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide (5 minutes to admin panel)
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines and architecture documentation
- **[ADMIN_README.md](ADMIN_README.md)** - Complete admin panel documentation
- **[ADMIN_SETUP_COMPLETE.md](ADMIN_SETUP_COMPLETE.md)** - Detailed admin setup guide
- **[ADMIN_IMPLEMENTATION_STATUS.md](ADMIN_IMPLEMENTATION_STATUS.md)** - Admin feature status and templates

## Tech Stack

- **Python**: 3.11+
- **aiogram**: 3.x - Modern Telegram Bot framework
- **aiosqlite**: Async SQLite database
- **python-dotenv**: Environment variable management
- **asyncpg**: (Optional) PostgreSQL async driver for production

## Development

For development guidelines and architectural details, see [CLAUDE.md](CLAUDE.md).

### Key Patterns
- All database operations use dataclass models
- FSM for multi-step conversations
- Middleware for cross-cutting concerns
- Router priority for handler organization
- Callback data patterns for navigation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the patterns in [CLAUDE.md](CLAUDE.md)
4. Test thoroughly with the bot
5. Submit a pull request

## Security

- Bot token stored in `.env` (never committed)
- Admin IDs whitelisted in environment variables
- Multi-layer admin authentication
- Audit logging for all admin actions
- SQL injection protection via parameterized queries
- `.env` file in `.gitignore`

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
