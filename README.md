# Telegram Marketplace Bot

A prototype Telegram bot for buying and selling goods and services, built with Python and aiogram.

## Features

### Current (Prototype)
- **User Management**: Automatic user registration and profile management
- **Listing Management**: Create, edit, and delete product listings with photos
- **Search & Filtering**: Search by keywords, filter by category and price range
- **Categories**: Organize products into categories
- **Communication**: Direct messaging between buyers and sellers via Telegram
- **Favorites**: Save interesting listings for later

### Planned (Future Expansion)
- Payment system integration (placeholder implemented)
- Secure escrow transactions
- Seller ratings and reviews
- Product delivery tracking
- Multimedia content support
- API integrations

## Project Structure

```
telegram_marketplace_bot/
├── bot.py              # Main bot entry point
├── config.py           # Configuration settings
├── database/
│   ├── __init__.py
│   ├── db.py           # Database connection and initialization
│   └── models.py       # Database models and operations
├── handlers/
│   ├── __init__.py
│   ├── common.py       # Common handlers (start, help, cancel)
│   ├── listings.py     # Listing management handlers
│   ├── search.py       # Search and filtering handlers
│   ├── messages.py     # Buyer-seller communication handlers
│   └── profile.py      # User profile handlers
├── keyboards/
│   ├── __init__.py
│   └── keyboards.py    # Inline and reply keyboards
├── states/
│   ├── __init__.py
│   └── states.py       # FSM states for conversations
├── utils/
│   ├── __init__.py
│   └── helpers.py      # Utility functions
└── requirements.txt    # Project dependencies
```

## Installation

1. **Clone/Download the project**

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**:
   - Get a bot token from [@BotFather](https://t.me/BotFather)
   - Copy `config.py.example` to `config.py` (or edit `config.py` directly)
   - Set your `BOT_TOKEN` in `config.py`

5. **Run the bot**:
   ```bash
   python bot.py
   ```

## Configuration

Edit `config.py` to customize:
- `BOT_TOKEN`: Your Telegram bot token
- `DATABASE_URL`: Database connection string (SQLite by default, can switch to PostgreSQL)
- `CATEGORIES`: Product categories
- `MAX_PHOTOS`: Maximum photos per listing
- `PAGE_SIZE`: Items per page in listings

## Database

The bot uses SQLite by default for simplicity. To switch to PostgreSQL:

1. Install `asyncpg`: `pip install asyncpg`
2. Update `DATABASE_URL` in `config.py`:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost/marketplace"
   ```
3. Update the database initialization in `database/db.py`

### Database Schema

- **users**: User accounts and profiles
- **listings**: Product/service listings
- **listing_photos**: Photos for listings
- **favorites**: User's saved listings
- **messages**: Communication between users
- **transactions**: Payment transactions (placeholder for future)

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

## Bot Commands

- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/search` - Search for listings
- `/mylistings` - View your listings
- `/favorites` - View saved listings
- `/profile` - View your profile
- `/cancel` - Cancel current operation

## Scalability Considerations

This prototype is built with scalability in mind:

1. **Database**: Easy migration from SQLite to PostgreSQL
2. **Modular Structure**: Handlers, keyboards, and models are separated
3. **FSM (Finite State Machine)**: Used for complex conversation flows
4. **Payment Placeholder**: Ready for payment gateway integration
5. **Extensible Categories**: Easy to add new product categories
6. **Middleware Ready**: Can add logging, rate limiting, etc.

## Future Enhancements

1. **Payments**: Integrate Telegram Payments API or external gateways
2. **Escrow**: Implement secure transaction holding
3. **Reviews**: Add seller/buyer rating system
4. **Delivery**: Integrate with shipping APIs
5. **Admin Panel**: Web-based administration interface
6. **Analytics**: Track popular products, user behavior
7. **Notifications**: Push notifications for price drops, new listings

## License

MIT License - feel free to use and modify as needed.
