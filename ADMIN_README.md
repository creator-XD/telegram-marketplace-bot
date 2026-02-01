# Admin Panel - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Bot already set up and working
- Your Telegram user ID

### Step 1: Configure Environment

Edit `.env` file and add your Telegram ID:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_IDS=your_telegram_id_here
SUPER_ADMIN_ID=your_telegram_id_here
```

**How to find your Telegram ID:**
- Message @userinfobot on Telegram
- Or use @raw_info_bot
- Look for the number after "Id:"

### Step 2: Install Dependencies

Dependencies are already installed if you ran `pip install -r requirements.txt` before.
The admin panel uses existing dependencies (no new packages needed).

### Step 3: Initialize Database

Run the bot once to create new admin tables:

```bash
python bot.py
```

The bot will automatically create the admin tables when it starts.

### Step 4: Create Your Admin User

1. **First**, send `/start` to your bot in Telegram to create your user account

2. **Then**, run the admin creation script:

```bash
python create_admin.py
```

You should see:
```
✅ Admin user created successfully!
  User ID: 123
  Telegram ID: your_telegram_id
  Name: Your Name
  Role: super_admin
  Permissions: 10

You can now access the admin panel by sending /admin command in the bot.
```

### Step 5: Access Admin Panel

In Telegram, send `/admin` to your bot.

You should see the admin panel menu with options like:
- 📊 Dashboard
- 👥 Users
- 📝 Listings
- 💳 Transactions
- 📈 Analytics
- 📋 Audit Log

---

## 📊 Current Features

### ✅ Implemented (Working Now)

1. **Foundation & Security**
   - Secure environment variable configuration
   - Admin authentication via Telegram ID whitelist
   - Role-based permission system
   - Automatic audit logging

2. **Database & Models**
   - Admin users table with roles
   - Audit log for all admin actions
   - User warnings system
   - Extended user/listing models with admin queries

3. **Basic Admin Panel**
   - `/admin` command access
   - Dashboard with statistics:
     - Total users (active, blocked, verified)
     - Total listings (active, sold, flagged)
     - Total transactions (pending, completed)
     - New registrations and listings

4. **Navigation**
   - Admin main menu
   - Section navigation (users, listings, transactions, analytics, audit log)

### 🔄 In Progress (Need Implementation)

The following features are planned but not yet implemented:

1. **User Management** (handlers/admin/user_management.py)
   - View all users with filters
   - User detail view
   - Block/unblock users
   - Warning system
   - View user's listings

2. **Listing Management** (handlers/admin/listing_management.py)
   - View all listings with filters
   - Flag/unflag inappropriate listings
   - Edit any listing
   - Delete listings
   - View listing details

3. **Transaction Management** (handlers/admin/transaction_management.py)
   - View all transactions
   - Filter by status
   - Transaction details

4. **Analytics** (handlers/admin/analytics.py)
   - Detailed user analytics
   - Listing statistics by category
   - Growth charts

5. **Audit Log Viewer** (handlers/admin/audit.py)
   - View recent admin actions
   - Filter by action type
   - Search audit logs

---

## 👥 Admin Roles & Permissions

### Super Admin
Full access to everything:
- ✅ Manage users (block, warn, edit)
- ✅ Manage listings (flag, edit, delete)
- ✅ Manage transactions
- ✅ View analytics
- ✅ Manage other admins
- ✅ View audit log

### Admin
Standard admin access:
- ✅ Manage users (block, warn, edit)
- ✅ Manage listings (flag, edit, delete)
- ✅ Manage transactions
- ✅ View analytics
- ✅ View audit log
- ❌ Cannot manage other admins

### Moderator
Limited moderation access:
- ✅ Manage listings (flag, edit)
- ✅ Warn users
- ✅ View analytics
- ❌ Cannot block users
- ❌ Cannot delete listings
- ❌ Cannot manage admins

---

## 🔐 Security Features

### Multi-Layer Security

1. **Telegram ID Whitelist**
   - Only Telegram IDs in `.env` can access admin panel
   - Configured in `ADMIN_TELEGRAM_IDS`

2. **Database Role Check**
   - Admin user must exist in `admin_users` table
   - Must have `is_active = 1`

3. **Permission System**
   - Each action requires specific permission
   - Permissions defined by role (super_admin, admin, moderator)

4. **Audit Logging**
   - All admin actions automatically logged
   - Tracks: who, what, when, why
   - Cannot be disabled

### What's Protected

- ✅ BOT_TOKEN moved from code to environment variable
- ✅ Admin IDs stored in .env (not in code)
- ✅ .env file in .gitignore (won't be committed to git)
- ✅ All admin routes require authentication
- ✅ All destructive actions logged

---

## 📝 How to Add More Admins

### Option 1: Using create_admin.py (Recommended)

1. Add their Telegram ID to `.env`:
```env
ADMIN_TELEGRAM_IDS=your_id,their_id,another_id
```

2. They send `/start` to the bot

3. Run:
```bash
python create_admin.py
```

The script will create admin users for all IDs in the whitelist.

### Option 2: Directly in Database (Advanced)

```python
from database.models import User
from database.admin_models import AdminUser
from config import ADMIN_ROLES

# Get user by Telegram ID
user = await User.get_by_telegram_id(telegram_id)

# Create admin
admin = await AdminUser.create(
    user_id=user.id,
    role="admin",  # or "moderator"
    permissions=ADMIN_ROLES["admin"]
)
```

---

## 🔧 Troubleshooting

### "У вас нет доступа к админ-панели"

**Cause**: Your Telegram ID is not in the admin whitelist or admin user not created.

**Solutions**:
1. Check `.env` has your correct Telegram ID in `ADMIN_TELEGRAM_IDS`
2. Restart the bot after changing `.env`
3. Make sure you ran `create_admin.py`
4. Verify admin exists: check `admin_users` table in marketplace.db

### "Ваш админ-аккаунт не активен"

**Cause**: Admin user exists but `is_active = 0`

**Solution**: Update database:
```sql
UPDATE admin_users SET is_active = 1 WHERE user_id = YOUR_USER_ID;
```

### Admin commands not showing in menu

**Cause**: Bot couldn't set commands for your chat.

**Solution**:
1. Bot needs to have sent you at least one message first
2. Send `/start` to the bot
3. Restart bot - it will set commands on startup

### Database errors

**Cause**: Admin tables not created

**Solution**:
1. Stop bot
2. Run `python bot.py` - it will create new tables automatically
3. Check marketplace.db has tables: `admin_users`, `admin_audit_log`, `user_warnings`

### Import errors

**Cause**: New files not in path or syntax errors

**Solution**:
1. Check all files are in correct directories
2. Check for typos in imports
3. Run `python -m py_compile <filename>` to check for syntax errors

---

## 📊 Database Schema

### admin_users
```sql
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- super_admin, admin, moderator
    permissions TEXT,     -- JSON array
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id)
);
```

### admin_audit_log
```sql
CREATE TABLE admin_audit_log (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT,  -- user, listing, transaction
    target_id INTEGER,
    details TEXT,      -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### user_warnings
```sql
CREATE TABLE user_warnings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    admin_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    severity TEXT DEFAULT 'low',  -- low, medium, high
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 🎯 Next Steps

To complete the admin panel implementation, you need to create handlers for:

1. **User Management** - See `ADMIN_IMPLEMENTATION_STATUS.md` for template
2. **Listing Management** - Similar structure to user management
3. **Transaction Management** - View and manage transactions
4. **Analytics** - Detailed statistics views
5. **Audit Log** - View admin action history

Templates and examples are provided in `ADMIN_IMPLEMENTATION_STATUS.md`.

---

## 📚 Additional Resources

- **Implementation Status**: `ADMIN_IMPLEMENTATION_STATUS.md`
- **Project Documentation**: `CLAUDE.md`
- **Main README**: `README.md`

---

## ⚠️ Important Notes

1. **Backup First**: Always backup `marketplace.db` before testing admin features
2. **Test Safely**: Test block/delete operations on test users/listings first
3. **Audit Everything**: All destructive actions are logged - check audit log regularly
4. **Secure .env**: Never commit `.env` to version control
5. **Update IDs**: Keep `ADMIN_TELEGRAM_IDS` in .env up to date

---

## 💡 Tips

- Use `/cancel` to exit any admin operation
- Dashboard refreshes on each view with latest stats
- Audit log shows last 50 actions by default
- Blocked users cannot use any bot features
- Flagged listings still show to users (admins see flag marker)

---

**Admin Panel Version**: 1.0.0 (Foundation)
**Last Updated**: 2026-02-01
