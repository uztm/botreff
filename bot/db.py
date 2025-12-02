import aiosqlite
from pathlib import Path
from .config import settings
import asyncio
from contextlib import asynccontextmanager

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
            # Enable WAL mode for better concurrency
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=NORMAL")
            await db.execute(CREATE_USERS)
            await db.execute(CREATE_REFERRALS)
            await db.commit()


@asynccontextmanager
async def get_db():
    """
    Async context manager that returns a database connection.
    Usage: async with get_db() as db:
    """
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    # Set isolation level to ensure we read committed data
    await conn.execute("PRAGMA read_uncommitted=0")
    try:
        yield conn
    finally:
        await conn.close()