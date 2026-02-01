"""
Database migration script to add admin panel columns to existing database.
Run this once to update your existing database with admin features.
"""
import asyncio
import sqlite3
from database.db import get_db


async def migrate():
    """Add admin columns to existing database."""
    print("=" * 60)
    print("DATABASE MIGRATION - Adding Admin Panel Columns")
    print("=" * 60)
    print()

    db = await get_db()

    # Get list of columns in users table
    cursor = await db.connection.execute("PRAGMA table_info(users)")
    user_columns = await cursor.fetchall()
    user_column_names = [col[1] for col in user_columns]

    print("Checking users table...")

    # Add suspension_reason column if it doesn't exist
    if "suspension_reason" not in user_column_names:
        print("  + Adding suspension_reason column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN suspension_reason TEXT")
        print("    [OK] Added suspension_reason")
    else:
        print("  [OK] suspension_reason already exists")

    # Add suspended_until column if it doesn't exist
    if "suspended_until" not in user_column_names:
        print("  + Adding suspended_until column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN suspended_until TIMESTAMP")
        print("    [OK] Added suspended_until")
    else:
        print("  [OK] suspended_until already exists")

    # Add warning_count column if it doesn't exist
    if "warning_count" not in user_column_names:
        print("  + Adding warning_count column...")
        await db.connection.execute("ALTER TABLE users ADD COLUMN warning_count INTEGER DEFAULT 0")
        print("    [OK] Added warning_count")
    else:
        print("  [OK] warning_count already exists")

    print()

    # Get list of columns in listings table
    cursor = await db.connection.execute("PRAGMA table_info(listings)")
    listing_columns = await cursor.fetchall()
    listing_column_names = [col[1] for col in listing_columns]

    print("Checking listings table...")

    # Add flagged column if it doesn't exist
    if "flagged" not in listing_column_names:
        print("  + Adding flagged column...")
        await db.connection.execute("ALTER TABLE listings ADD COLUMN flagged INTEGER DEFAULT 0")
        print("    [OK] Added flagged")
    else:
        print("  [OK] flagged already exists")

    # Add flag_reason column if it doesn't exist
    if "flag_reason" not in listing_column_names:
        print("  + Adding flag_reason column...")
        await db.connection.execute("ALTER TABLE listings ADD COLUMN flag_reason TEXT")
        print("    [OK] Added flag_reason")
    else:
        print("  [OK] flag_reason already exists")

    # Commit changes
    await db.connection.commit()

    print()
    print("=" * 60)
    print("[SUCCESS] Migration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart the bot: python bot.py")
    print("2. Send /start to create your user account (if not done)")
    print("3. Run: python create_admin.py")
    print("4. Send /admin to access the admin panel")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
