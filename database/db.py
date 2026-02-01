"""
Database connection and initialization for SQLite.
Can be adapted for PostgreSQL for production scaling.
"""
import aiosqlite
import logging
from typing import Optional
from config import DATABASE_URL

logger = logging.getLogger(__name__)


class Database:
    """
    Database manager class for handling SQLite connections.
    Designed to be easily replaceable with PostgreSQL for scaling.
    """
    
    def __init__(self, db_path: str = DATABASE_URL):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Establish database connection."""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.connection.execute("PRAGMA foreign_keys = ON")
        logger.info(f"Connected to database: {self.db_path}")
    
    async def disconnect(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def init_tables(self):
        """Initialize database tables."""
        await self.connection.executescript("""
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                location TEXT,
                bio TEXT,
                is_active INTEGER DEFAULT 1,
                is_verified INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Listings table
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                category TEXT NOT NULL,
                location TEXT,
                status TEXT DEFAULT 'active',  -- active, sold, reserved, deleted
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            -- Listing photos table
            CREATE TABLE IF NOT EXISTS listing_photos (
                id INTEGER PRIMARY KEY,
                listing_id INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                file_unique_id TEXT NOT NULL,
                is_primary INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );
            
            -- Favorites table
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                listing_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                UNIQUE(user_id, listing_id)
            );
            
            -- Messages table (for buyer-seller communication tracking)
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                listing_id INTEGER,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                message_text TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE SET NULL,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            -- Transactions table (placeholder for future payment integration)
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                listing_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'pending',  -- pending, completed, cancelled, refunded
                payment_method TEXT,
                payment_id TEXT,  -- External payment provider ID
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE SET NULL,
                FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            -- Indexes for better query performance
            CREATE INDEX IF NOT EXISTS idx_listings_user ON listings(user_id);
            CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);
            CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
            CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
            CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
            CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
        """)
        await self.connection.commit()
        logger.info("Database tables initialized")
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query and return the cursor."""
        cursor = await self.connection.execute(query, params)
        await self.connection.commit()
        return cursor
    
    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row."""
        cursor = await self.connection.execute(query, params)
        return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows."""
        cursor = await self.connection.execute(query, params)
        return await cursor.fetchall()


# Global database instance
_db: Optional[Database] = None


async def get_db() -> Database:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
        await _db.init_tables()
    return _db


async def close_db():
    """Close the global database instance."""
    global _db
    if _db is not None:
        await _db.disconnect()
        _db = None
