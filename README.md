# Telegram Referral Bot

A Telegram bot for managing referral campaigns with channel subscription verification.

## Features

- User registration with referral tracking
- Channel subscription verification
- Referral link generation
- User profile with referral count
- SQLite database for data persistence

## Requirements

- Python 3.10+
- aiogram 3.x
- aiosqlite

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd bot
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your configuration:
```env
BOT_TOKEN=your_bot_token_here
CHANNEL_1=@your_channel_1
CHANNEL_2=@your_channel_2
BOT_USERNAME=your_bot_username
ADMIN_IDS=[123456789,987654321]
ADMIN_PANEL_TOKEN=your_admin_token
DATABASE_PATH=./data/bot.db
```

## Configuration

- `BOT_TOKEN`: Your bot token from @BotFather
- `CHANNEL_1`, `CHANNEL_2`: Channel usernames or IDs (e.g., @mychannel or -1001234567890)
- `BOT_USERNAME`: Your bot's username without @
- `ADMIN_IDS`: List of admin user IDs
- `DATABASE_PATH`: Path to SQLite database file

## Running the Bot

```bash
python -m bot.main
```

Or with the virtual environment:
```bash
source .venv/bin/activate
python -m bot.main
```

## Project Structure

```
bot/
├── __init__.py
├── main.py           # Bot entry point
├── config.py         # Configuration settings
├── db.py            # Database setup and utilities
├── models.py        # Database models and queries
├── keyboards.py     # Keyboard layouts
├── handlers/        # Message handlers
│   ├── __init__.py
│   ├── start.py     # /start command handler
│   ├── profile.py   # /profile command handler
│   └── common.py    # Common handlers (/help, etc.)
└── services/        # Business logic
    ├── __init__.py
    ├── referral.py  # Referral management
    └── subscription.py  # Subscription checking
```

## Commands

- `/start` - Start the bot and register user
- `/start <referrer_id>` - Start with referral link
- `/profile` - View profile and referral stats
- `/help` - Show help message

## Database Schema

### users
- `user_id` (INTEGER PRIMARY KEY)
- `username` (TEXT)
- `full_name` (TEXT)
- `invited_by` (INTEGER)
- `referrals_count` (INTEGER)
- `is_member` (INTEGER)

### referrals
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `inviter_id` (INTEGER)
- `invited_id` (INTEGER)
- `created_at` (TEXT)

## Development

The bot uses:
- **aiogram 3.x** for Telegram Bot API
- **aiosqlite** for async SQLite operations
- **pydantic-settings** for configuration management

## License

[Your License Here]