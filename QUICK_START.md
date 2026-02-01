# 🚀 Admin Panel - Quick Start

## In 5 Minutes

### 1. Configure (1 min)

Edit `.env`:
```env
BOT_TOKEN=your_token
ADMIN_TELEGRAM_IDS=your_telegram_id
SUPER_ADMIN_ID=your_telegram_id
```

**How to get your Telegram ID**: Message @userinfobot

### 2. Start Bot (1 min)

```bash
python bot.py
```

Wait for: "Database initialized" and "Bot started"

### 3. Create User (1 min)

In Telegram, send `/start` to your bot.

### 4. Create Admin (1 min)

```bash
python create_admin.py
```

Look for: "✅ Admin user created successfully!"

### 5. Access Panel (1 min)

In Telegram, send `/admin` to your bot.

**Done!** 🎉

---

## What You Can Do Now

### ✅ Working Features

- Access admin panel with `/admin`
- View live dashboard statistics
- Navigate admin sections

### 🔄 To Be Implemented

- User management (block, warn)
- Listing management (flag, edit, delete)
- Transaction viewing
- Detailed analytics
- Audit log viewer

See `ADMIN_IMPLEMENTATION_STATUS.md` for implementation templates.

---

## File Overview

| File | Purpose |
|------|---------|
| `ADMIN_SETUP_COMPLETE.md` | ✅ Complete setup guide & status |
| `ADMIN_README.md` | 📚 Full documentation |
| `ADMIN_IMPLEMENTATION_STATUS.md` | 🔧 Technical details & templates |
| **`QUICK_START.md`** | ⚡ This file - fastest path to running |
| `create_admin.py` | 🛠️ Script to create admin users |
| `check_admin_setup.py` | 🔍 Diagnostic tool |

---

## Troubleshooting

### "У вас нет доступа"
→ Check `.env` has your Telegram ID
→ Run `create_admin.py`

### "Ваш админ-аккаунт не активен"
→ Database issue, check `admin_users` table

### Import errors
→ Check all files in correct location
→ Restart Python

### Database errors
→ Delete `marketplace.db` and restart bot

---

## Next Steps

1. ✅ You have: Working admin panel foundation
2. 📝 You need: Implement handler logic
3. 📖 Read: `ADMIN_IMPLEMENTATION_STATUS.md` for templates

---

**Ready in 5 minutes!** 🚀
