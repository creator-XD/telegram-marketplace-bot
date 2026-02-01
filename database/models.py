"""
Database models and operations for the Telegram Marketplace Bot.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from .db import get_db


@dataclass
class User:
    """User model."""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    rating: float = 0.0
    rating_count: int = 0
    suspension_reason: Optional[str] = None
    suspended_until: Optional[datetime] = None
    warning_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_row(cls, row) -> Optional["User"]:
        """Create User from database row."""
        if row is None:
            return None

        # Handle new admin fields that might not exist in older database schemas
        try:
            suspension_reason = row["suspension_reason"]
        except (KeyError, IndexError):
            suspension_reason = None

        try:
            suspended_until = row["suspended_until"]
        except (KeyError, IndexError):
            suspended_until = None

        try:
            warning_count = row["warning_count"]
        except (KeyError, IndexError):
            warning_count = 0

        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone=row["phone"],
            location=row["location"],
            bio=row["bio"],
            is_active=bool(row["is_active"]),
            is_verified=bool(row["is_verified"]),
            rating=row["rating"],
            rating_count=row["rating_count"],
            suspension_reason=suspension_reason,
            suspended_until=suspended_until,
            warning_count=warning_count,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def get_by_telegram_id(cls, telegram_id: int) -> Optional["User"]:
        """Get user by Telegram ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by internal ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        return cls.from_row(row)
    
    @classmethod
    async def create(
        cls,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> "User":
        """Create a new user."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, username, first_name, last_name)
        )
        return await cls.get_by_id(cursor.lastrowid)
    
    @classmethod
    async def get_or_create(
        cls,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> "User":
        """Get existing user or create new one."""
        user = await cls.get_by_telegram_id(telegram_id)
        if user is None:
            user = await cls.create(telegram_id, username, first_name, last_name)
        else:
            # Update user info if changed
            await user.update(username=username, first_name=first_name, last_name=last_name)
            user = await cls.get_by_telegram_id(telegram_id)
        return user
    
    async def update(self, **kwargs) -> bool:
        """Update user fields."""
        if not kwargs:
            return False
        
        db = await get_db()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [self.id]
        
        await db.execute(
            f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values)
        )
        return True
    
    @property
    def display_name(self) -> str:
        """Get display name for user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return f"User #{self.telegram_id}"

    @classmethod
    async def get_all(
        cls,
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["User"]:
        """Get all users with optional filters (for admin)."""
        db = await get_db()
        conditions = []
        params = []

        if status == "active":
            conditions.append("is_active = 1")
        elif status == "blocked":
            conditions.append("is_active = 0")
        elif status == "verified":
            conditions.append("is_verified = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM users
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all(cls, status: str = None) -> int:
        """Count all users with optional filters (for admin)."""
        db = await get_db()
        conditions = []
        params = []

        if status == "active":
            conditions.append("is_active = 1")
        elif status == "blocked":
            conditions.append("is_active = 0")
        elif status == "verified":
            conditions.append("is_verified = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM users WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Get user statistics (for admin dashboard)."""
        db = await get_db()

        # Total users
        total = await db.fetch_one("SELECT COUNT(*) as count FROM users")
        # Active users
        active = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        # Blocked users
        blocked = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 0")
        # Verified users
        verified = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_verified = 1")
        # New users today
        new_today = await db.fetch_one(
            "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')"
        )
        # New users this week
        new_week = await db.fetch_one(
            "SELECT COUNT(*) as count FROM users WHERE created_at >= DATE('now', '-7 days')"
        )

        return {
            "total": total["count"] if total else 0,
            "active": active["count"] if active else 0,
            "blocked": blocked["count"] if blocked else 0,
            "verified": verified["count"] if verified else 0,
            "new_today": new_today["count"] if new_today else 0,
            "new_week": new_week["count"] if new_week else 0,
        }


@dataclass
class Listing:
    """Listing model."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    price: float
    currency: str
    category: str
    location: Optional[str]
    status: str
    views: int
    flagged: int
    flag_reason: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # Related data (loaded separately)
    photos: Optional[List["ListingPhoto"]] = None
    user: Optional[User] = None
    
    @classmethod
    def from_row(cls, row) -> Optional["Listing"]:
        """Create Listing from database row."""
        if row is None:
            return None

        # Handle new admin fields that might not exist in older database schemas
        try:
            flagged = row["flagged"]
        except (KeyError, IndexError):
            flagged = 0

        try:
            flag_reason = row["flag_reason"]
        except (KeyError, IndexError):
            flag_reason = None

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            price=row["price"],
            currency=row["currency"],
            category=row["category"],
            location=row["location"],
            status=row["status"],
            views=row["views"],
            flagged=flagged,
            flag_reason=flag_reason,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def get_by_id(cls, listing_id: int, with_photos: bool = False, with_user: bool = False) -> Optional["Listing"]:
        """Get listing by ID."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT * FROM listings WHERE id = ?",
            (listing_id,)
        )
        listing = cls.from_row(row)
        
        if listing and with_photos:
            listing.photos = await ListingPhoto.get_by_listing_id(listing_id)
        
        if listing and with_user:
            listing.user = await User.get_by_id(listing.user_id)
        
        return listing
    
    @classmethod
    async def get_by_user(cls, user_id: int, status: str = None) -> List["Listing"]:
        """Get all listings by user."""
        db = await get_db()
        if status:
            rows = await db.fetch_all(
                "SELECT * FROM listings WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                (user_id, status)
            )
        else:
            rows = await db.fetch_all(
                "SELECT * FROM listings WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def create(
        cls,
        user_id: int,
        title: str,
        description: str,
        price: float,
        category: str,
        currency: str = "USD",
        location: str = None,
    ) -> "Listing":
        """Create a new listing."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO listings (user_id, title, description, price, category, currency, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, description, price, category, currency, location)
        )
        return await cls.get_by_id(cursor.lastrowid)
    
    async def update(self, **kwargs) -> bool:
        """Update listing fields."""
        if not kwargs:
            return False
        
        db = await get_db()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [self.id]
        
        await db.execute(
            f"UPDATE listings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values)
        )
        return True
    
    async def delete(self) -> bool:
        """Soft delete listing."""
        return await self.update(status="deleted")
    
    async def increment_views(self) -> None:
        """Increment view counter."""
        db = await get_db()
        await db.execute(
            "UPDATE listings SET views = views + 1 WHERE id = ?",
            (self.id,)
        )
    
    @classmethod
    async def search(
        cls,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List["Listing"]:
        """Search listings with filters."""
        db = await get_db()
        conditions = ["status = 'active'"]
        params = []
        
        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])
        
        rows = await db.fetch_all(
            f"""
            SELECT * FROM listings 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def count_search(
        cls,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
    ) -> int:
        """Count listings matching search criteria."""
        db = await get_db()
        conditions = ["status = 'active'"]
        params = []
        
        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions)
        
        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM listings WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0
    
    @classmethod
    async def get_recent(cls, limit: int = 10) -> List["Listing"]:
        """Get recent active listings."""
        db = await get_db()
        rows = await db.fetch_all(
            "SELECT * FROM listings WHERE status = 'active' ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def get_by_category(cls, category: str, limit: int = 10, offset: int = 0) -> List["Listing"]:
        """Get listings by category."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT * FROM listings
            WHERE category = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (category, limit, offset)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def get_all_admin(
        cls,
        status: str = None,
        category: str = None,
        flagged_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List["Listing"]:
        """Get all listings with filters (for admin)."""
        db = await get_db()
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if flagged_only:
            conditions.append("flagged = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.extend([limit, offset])

        rows = await db.fetch_all(
            f"""
            SELECT * FROM listings
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all_admin(
        cls,
        status: str = None,
        category: str = None,
        flagged_only: bool = False
    ) -> int:
        """Count all listings with filters (for admin)."""
        db = await get_db()
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if flagged_only:
            conditions.append("flagged = 1")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        row = await db.fetch_one(
            f"SELECT COUNT(*) as count FROM listings WHERE {where_clause}",
            tuple(params)
        )
        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Get listing statistics (for admin dashboard)."""
        db = await get_db()

        # Total listings
        total = await db.fetch_one("SELECT COUNT(*) as count FROM listings")
        # Active listings
        active = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'active'")
        # Sold listings
        sold = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'sold'")
        # Deleted listings
        deleted = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE status = 'deleted'")
        # Flagged listings
        flagged = await db.fetch_one("SELECT COUNT(*) as count FROM listings WHERE flagged = 1")
        # New listings today
        new_today = await db.fetch_one(
            "SELECT COUNT(*) as count FROM listings WHERE DATE(created_at) = DATE('now')"
        )
        # New listings this week
        new_week = await db.fetch_one(
            "SELECT COUNT(*) as count FROM listings WHERE created_at >= DATE('now', '-7 days')"
        )

        return {
            "total": total["count"] if total else 0,
            "active": active["count"] if active else 0,
            "sold": sold["count"] if sold else 0,
            "deleted": deleted["count"] if deleted else 0,
            "flagged": flagged["count"] if flagged else 0,
            "new_today": new_today["count"] if new_today else 0,
            "new_week": new_week["count"] if new_week else 0,
        }


@dataclass
class ListingPhoto:
    """Listing photo model."""
    id: int
    listing_id: int
    file_id: str
    file_unique_id: str
    is_primary: bool
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["ListingPhoto"]:
        """Create ListingPhoto from database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            file_id=row["file_id"],
            file_unique_id=row["file_unique_id"],
            is_primary=bool(row["is_primary"]),
            created_at=row["created_at"],
        )
    
    @classmethod
    async def get_by_listing_id(cls, listing_id: int) -> List["ListingPhoto"]:
        """Get all photos for a listing."""
        db = await get_db()
        rows = await db.fetch_all(
            "SELECT * FROM listing_photos WHERE listing_id = ? ORDER BY is_primary DESC, id ASC",
            (listing_id,)
        )
        return [cls.from_row(row) for row in rows]
    
    @classmethod
    async def create(cls, listing_id: int, file_id: str, file_unique_id: str, is_primary: bool = False) -> "ListingPhoto":
        """Create a new listing photo."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO listing_photos (listing_id, file_id, file_unique_id, is_primary)
            VALUES (?, ?, ?, ?)
            """,
            (listing_id, file_id, file_unique_id, is_primary)
        )
        row = await db.fetch_one("SELECT * FROM listing_photos WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)
    
    @classmethod
    async def delete_by_listing_id(cls, listing_id: int) -> None:
        """Delete all photos for a listing."""
        db = await get_db()
        await db.execute("DELETE FROM listing_photos WHERE listing_id = ?", (listing_id,))


@dataclass
class Favorite:
    """Favorite model."""
    id: int
    user_id: int
    listing_id: int
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Favorite"]:
        """Create Favorite from database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            listing_id=row["listing_id"],
            created_at=row["created_at"],
        )
    
    @classmethod
    async def add(cls, user_id: int, listing_id: int) -> Optional["Favorite"]:
        """Add listing to favorites."""
        db = await get_db()
        try:
            cursor = await db.execute(
                "INSERT INTO favorites (user_id, listing_id) VALUES (?, ?)",
                (user_id, listing_id)
            )
            row = await db.fetch_one("SELECT * FROM favorites WHERE id = ?", (cursor.lastrowid,))
            return cls.from_row(row)
        except Exception:
            return None  # Already in favorites
    
    @classmethod
    async def remove(cls, user_id: int, listing_id: int) -> bool:
        """Remove listing from favorites."""
        db = await get_db()
        await db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id)
        )
        return True
    
    @classmethod
    async def is_favorite(cls, user_id: int, listing_id: int) -> bool:
        """Check if listing is in user's favorites."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT id FROM favorites WHERE user_id = ? AND listing_id = ?",
            (user_id, listing_id)
        )
        return row is not None
    
    @classmethod
    async def get_user_favorites(cls, user_id: int) -> List[Listing]:
        """Get user's favorite listings."""
        db = await get_db()
        rows = await db.fetch_all(
            """
            SELECT l.* FROM listings l
            JOIN favorites f ON l.id = f.listing_id
            WHERE f.user_id = ? AND l.status = 'active'
            ORDER BY f.created_at DESC
            """,
            (user_id,)
        )
        return [Listing.from_row(row) for row in rows]


@dataclass
class Message:
    """Message model for buyer-seller communication."""
    id: int
    listing_id: Optional[int]
    sender_id: int
    receiver_id: int
    message_text: Optional[str]
    is_read: bool
    created_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Message"]:
        """Create Message from database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            sender_id=row["sender_id"],
            receiver_id=row["receiver_id"],
            message_text=row["message_text"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
        )
    
    @classmethod
    async def create(cls, sender_id: int, receiver_id: int, message_text: str, listing_id: int = None) -> "Message":
        """Create a new message."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO messages (listing_id, sender_id, receiver_id, message_text)
            VALUES (?, ?, ?, ?)
            """,
            (listing_id, sender_id, receiver_id, message_text)
        )
        row = await db.fetch_one("SELECT * FROM messages WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)
    
    @classmethod
    async def get_unread_count(cls, user_id: int) -> int:
        """Get count of unread messages for user."""
        db = await get_db()
        row = await db.fetch_one(
            "SELECT COUNT(*) as count FROM messages WHERE receiver_id = ? AND is_read = 0",
            (user_id,)
        )
        return row["count"] if row else 0


@dataclass
class Transaction:
    """Transaction model (placeholder for future payment integration)."""
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    payment_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @classmethod
    def from_row(cls, row) -> Optional["Transaction"]:
        """Create Transaction from database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            listing_id=row["listing_id"],
            buyer_id=row["buyer_id"],
            seller_id=row["seller_id"],
            amount=row["amount"],
            currency=row["currency"],
            status=row["status"],
            payment_method=row["payment_method"],
            payment_id=row["payment_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    @classmethod
    async def create(
        cls,
        listing_id: int,
        buyer_id: int,
        seller_id: int,
        amount: float,
        currency: str = "USD",
    ) -> "Transaction":
        """Create a new transaction (placeholder)."""
        db = await get_db()
        cursor = await db.execute(
            """
            INSERT INTO transactions (listing_id, buyer_id, seller_id, amount, currency)
            VALUES (?, ?, ?, ?, ?)
            """,
            (listing_id, buyer_id, seller_id, amount, currency)
        )
        row = await db.fetch_one("SELECT * FROM transactions WHERE id = ?", (cursor.lastrowid,))
        return cls.from_row(row)

    @classmethod
    async def get_all(
        cls,
        status: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List["Transaction"]:
        """Get all transactions with filters (for admin)."""
        db = await get_db()

        if status:
            rows = await db.fetch_all(
                """
                SELECT * FROM transactions
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (status, limit, offset)
            )
        else:
            rows = await db.fetch_all(
                """
                SELECT * FROM transactions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )

        return [cls.from_row(row) for row in rows]

    @classmethod
    async def count_all(cls, status: str = None) -> int:
        """Count all transactions with filters (for admin)."""
        db = await get_db()

        if status:
            row = await db.fetch_one(
                "SELECT COUNT(*) as count FROM transactions WHERE status = ?",
                (status,)
            )
        else:
            row = await db.fetch_one("SELECT COUNT(*) as count FROM transactions")

        return row["count"] if row else 0

    @classmethod
    async def get_statistics(cls) -> dict:
        """Get transaction statistics (for admin dashboard)."""
        db = await get_db()

        # Total transactions
        total = await db.fetch_one("SELECT COUNT(*) as count FROM transactions")
        # Pending
        pending = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'")
        # Completed
        completed = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'completed'")
        # Cancelled
        cancelled = await db.fetch_one("SELECT COUNT(*) as count FROM transactions WHERE status = 'cancelled'")

        return {
            "total": total["count"] if total else 0,
            "pending": pending["count"] if pending else 0,
            "completed": completed["count"] if completed else 0,
            "cancelled": cancelled["count"] if cancelled else 0,
        }
