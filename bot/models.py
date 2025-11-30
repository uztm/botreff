from typing import Optional, List, Dict, Any
from .db import get_db
import aiosqlite


async def create_user(user_id: int, username: Optional[str], full_name: Optional[str], invited_by: Optional[int] = None):
    async with get_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, invited_by) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, invited_by)
        )
        await db.commit()


async def get_user(user_id: int) -> Optional[aiosqlite.Row]:
    async with get_db() as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()


async def set_user_member(user_id: int):
    async with get_db() as db:
        await db.execute("UPDATE users SET is_member = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def add_referral(inviter_id: int, invited_id: int):
    async with get_db() as db:
        cur = await db.execute(
            "SELECT id FROM referrals WHERE inviter_id = ? AND invited_id = ?",
            (inviter_id, invited_id)
        )
        if await cur.fetchone():
            return False

        await db.execute(
            "INSERT INTO referrals (inviter_id, invited_id) VALUES (?, ?)",
            (inviter_id, invited_id)
        )
        await db.execute(
            "UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?",
            (inviter_id,)
        )
        await db.commit()
        return True


async def referral_count(user_id: int) -> int:
    async with get_db() as db:
        cur = await db.execute("SELECT referrals_count FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row["referrals_count"] if row else 0


async def get_inviter(user_id: int) -> Optional[int]:
    async with get_db() as db:
        cur = await db.execute("SELECT invited_by FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row["invited_by"] if row else None


async def list_users(limit: int = 1000) -> List[Dict[str, Any]]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT user_id, username, referrals_count, is_member FROM users LIMIT ?",
            (limit,)
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
