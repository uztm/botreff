import aiosqlite
from pathlib import Path
from .config import settings
import asyncio

DB_PATH = settings.DATABASE_PATH
DB_LOCK = asyncio.Lock()

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    invited_by INTEGER,
    referrals_count INTEGER DEFAULT 0,
    is_member INTEGER DEFAULT 0
);
"""

CREATE_REFERRALS = """
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inviter_id INTEGER,
    invited_id INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


async def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    async with DB_LOCK:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(CREATE_USERS)
            await db.execute(CREATE_REFERRALS)
            await db.commit()


async def get_db():
    # Altdan connection qaytaradi har safar query uchun
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    return conn
