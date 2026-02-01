"""
Telegram Marketplace Bot - Main Entry Point

A prototype Telegram bot for buying and selling goods and services.
Built with aiogram 3.x and SQLite (with PostgreSQL scalability in mind).
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, BOT_NAME, ADMIN_TELEGRAM_IDS
from database.db import get_db, close_db
from handlers import get_all_routers
from middleware import AdminAuthMiddleware, AuditLoggerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Uncomment to also log to file:
        # logging.FileHandler("bot.log"),
    ],
)

# Reduce noise from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Run on bot startup."""
    # Initialize database
    db = await get_db()
    logger.info("Database initialized")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username} ({bot_info.first_name})")
    
    # Set bot commands menu
    from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

    # Regular user commands
    user_commands = [
        BotCommand(command="start", description="Start the bot / Main menu"),
        BotCommand(command="search", description="Search listings"),
        BotCommand(command="mylistings", description="View your listings"),
        BotCommand(command="favorites", description="View saved listings"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="help", description="Get help"),
        BotCommand(command="cancel", description="Cancel current operation"),
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    logger.info("Bot commands menu set for regular users")

    # Admin commands (for admin users only)
    if ADMIN_TELEGRAM_IDS:
        admin_commands = user_commands + [
            BotCommand(command="admin", description="🔧 Admin Panel"),
        ]
        for admin_id in ADMIN_TELEGRAM_IDS:
            try:
                await bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
            except Exception as e:
                logger.warning(f"Could not set admin commands for {admin_id}: {e}")
        logger.info(f"Admin commands set for {len(ADMIN_TELEGRAM_IDS)} admin users")


async def on_shutdown(bot: Bot):
    """Run on bot shutdown."""
    await close_db()
    logger.info("Database connection closed")
    logger.info("Bot stopped")


async def main():
    """Main entry point."""
    # Validate token
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Bot token not configured! Please set BOT_TOKEN in config.py")
        sys.exit(1)
    
    # Initialize bot with HTML parse mode as default
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Initialize dispatcher with memory storage for FSM
    # Note: For production, consider using Redis storage for persistence
    dp = Dispatcher(storage=MemoryStorage())

    # Register middleware (before routers)
    dp.message.middleware(AdminAuthMiddleware())
    dp.callback_query.middleware(AdminAuthMiddleware())
    dp.message.middleware(AuditLoggerMiddleware())
    dp.callback_query.middleware(AuditLoggerMiddleware())
    logger.info("Admin middleware registered")

    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Include all routers
    for router in get_all_routers():
        dp.include_router(router)
        logger.info(f"Registered router: {router.name}")
    
    # Start polling
    logger.info(f"Starting {BOT_NAME}...")
    
    try:
        # Delete webhook (in case it was set before) and start polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
