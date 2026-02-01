"""
Script to check admin panel setup and configuration.
Run this to diagnose admin panel issues.
"""
import asyncio
import os
from pathlib import Path


async def check_setup():
    """Check admin panel setup."""
    print("=" * 60)
    print("ADMIN PANEL SETUP CHECKER")
    print("=" * 60)
    print()

    issues = []
    warnings = []

    # Check 1: .env file exists
    print("✓ Checking .env file...")
    if not os.path.exists(".env"):
        issues.append(".env file not found! Create it from .env.example")
    else:
        print("  ✅ .env file exists")

        # Check environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Check BOT_TOKEN
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            issues.append("BOT_TOKEN not set in .env")
        else:
            print(f"  ✅ BOT_TOKEN is set")

        # Check ADMIN_TELEGRAM_IDS
        admin_ids = os.getenv("ADMIN_TELEGRAM_IDS")
        if not admin_ids:
            issues.append("ADMIN_TELEGRAM_IDS not set in .env")
        else:
            ids = [id.strip() for id in admin_ids.split(",") if id.strip()]
            print(f"  ✅ ADMIN_TELEGRAM_IDS is set ({len(ids)} admin(s))")
            for admin_id in ids:
                print(f"    - {admin_id}")

        # Check SUPER_ADMIN_ID
        super_admin = os.getenv("SUPER_ADMIN_ID")
        if not super_admin:
            warnings.append("SUPER_ADMIN_ID not set (optional but recommended)")
        else:
            print(f"  ✅ SUPER_ADMIN_ID is set: {super_admin}")

    print()

    # Check 2: Database file
    print("✓ Checking database...")
    if not os.path.exists("marketplace.db"):
        warnings.append("marketplace.db not found - run bot.py first to create it")
    else:
        print("  ✅ marketplace.db exists")

        # Check database tables
        from database.db import get_db
        db = await get_db()

        try:
            # Check admin tables exist
            result = await db.fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'"
            )
            if result:
                print("  ✅ admin_users table exists")
            else:
                issues.append("admin_users table not found - run bot.py to create it")

            result = await db.fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log'"
            )
            if result:
                print("  ✅ admin_audit_log table exists")
            else:
                issues.append("admin_audit_log table not found - run bot.py to create it")

            result = await db.fetch_one(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user_warnings'"
            )
            if result:
                print("  ✅ user_warnings table exists")
            else:
                issues.append("user_warnings table not found - run bot.py to create it")

            # Check for admin users
            admin_count = await db.fetch_one("SELECT COUNT(*) as count FROM admin_users")
            if admin_count and admin_count["count"] > 0:
                print(f"  ✅ {admin_count['count']} admin user(s) in database")

                # List admins
                admins = await db.fetch_all(
                    """
                    SELECT a.*, u.telegram_id, u.first_name, u.last_name
                    FROM admin_users a
                    JOIN users u ON a.user_id = u.id
                    """
                )
                for admin in admins:
                    status = "🟢" if admin["is_active"] else "🔴"
                    name = admin["first_name"] or "Unknown"
                    print(f"    {status} {name} (TG: {admin['telegram_id']}, Role: {admin['role']})")
            else:
                warnings.append("No admin users in database - run create_admin.py")

        except Exception as e:
            issues.append(f"Database error: {e}")

    print()

    # Check 3: Required files
    print("✓ Checking required files...")
    required_files = [
        "handlers/admin/__init__.py",
        "handlers/admin/admin_router.py",
        "middleware/admin_auth.py",
        "middleware/audit_logger.py",
        "utils/decorators.py",
        "utils/admin_helpers.py",
        "keyboards/admin_keyboards.py",
        "database/admin_models.py",
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            issues.append(f"Missing file: {file_path}")

    print()

    # Check 4: Imports
    print("✓ Checking imports...")
    try:
        from config import ADMIN_TELEGRAM_IDS, ADMIN_ROLES
        print("  ✅ config imports work")
    except Exception as e:
        issues.append(f"Config import error: {e}")

    try:
        from database.admin_models import AdminUser, AdminAuditLog, UserWarning
        print("  ✅ admin_models imports work")
    except Exception as e:
        issues.append(f"admin_models import error: {e}")

    try:
        from middleware import AdminAuthMiddleware, AuditLoggerMiddleware
        print("  ✅ middleware imports work")
    except Exception as e:
        issues.append(f"middleware import error: {e}")

    try:
        from utils.decorators import require_admin, require_permission
        print("  ✅ decorators imports work")
    except Exception as e:
        issues.append(f"decorators import error: {e}")

    try:
        from keyboards.admin_keyboards import get_admin_main_menu_keyboard
        print("  ✅ admin_keyboards imports work")
    except Exception as e:
        issues.append(f"admin_keyboards import error: {e}")

    try:
        from handlers.admin import admin_router
        print("  ✅ admin_router import works")
    except Exception as e:
        issues.append(f"admin_router import error: {e}")

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    if not issues and not warnings:
        print("🎉 ✅ Everything looks good!")
        print()
        print("Next steps:")
        print("1. Make sure you've sent /start to the bot")
        print("2. Run: python create_admin.py")
        print("3. Run: python bot.py")
        print("4. Send /admin to your bot")
    else:
        if issues:
            print(f"❌ {len(issues)} issue(s) found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            print()

        if warnings:
            print(f"⚠️  {len(warnings)} warning(s):")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
            print()

        print("Fix the issues above and run this script again.")

    print()


if __name__ == "__main__":
    try:
        asyncio.run(check_setup())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
