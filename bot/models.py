# bot/models.py
from typing import Optional, List, Dict, Any, Tuple
from .db import get_db
import aiosqlite
import logging

logger = logging.getLogger(__name__)


async def create_user(
    user_id: int, 
    username: Optional[str], 
    full_name: Optional[str], 
    invited_by: Optional[int] = None
):
    """Create a new user or ignore if already exists"""
    async with get_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, invited_by, referrals_count) VALUES (?, ?, ?, ?, 0)",
            (user_id, username, full_name, invited_by)
        )
        await db.commit()


async def get_user(user_id: int) -> Optional[aiosqlite.Row]:
    """Get user by ID with verified referral count"""
    async with get_db() as db:
        cur = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cur.fetchone()
        
        if row:
            # Verify referral count matches actual referrals
            stored_count = row["referrals_count"] if row["referrals_count"] is not None else 0
            
            cur2 = await db.execute(
                "SELECT COUNT(*) as actual FROM referrals WHERE inviter_id = ?",
                (user_id,)
            )
            actual_row = await cur2.fetchone()
            actual_count = actual_row["actual"] if actual_row else 0
            
            if stored_count != actual_count:
                logger.warning(f"User {user_id} count mismatch: stored={stored_count}, actual={actual_count}. Fixing...")
                # Fix the count in the database
                await db.execute(
                    "UPDATE users SET referrals_count = ? WHERE user_id = ?",
                    (actual_count, user_id)
                )
                await db.commit()
                
                # Re-fetch the updated row
                cur3 = await db.execute(
                    "SELECT * FROM users WHERE user_id = ?", 
                    (user_id,)
                )
                row = await cur3.fetchone()
        
        return row


async def set_user_member(user_id: int):
    """Mark user as a member"""
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET is_member = 1 WHERE user_id = ?", 
            (user_id,)
        )
        await db.commit()
        logger.info(f"User {user_id} marked as member")


async def update_user_inviter(user_id: int, inviter_id: int):
    """Update user's inviter if not already set"""
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET invited_by = ? WHERE user_id = ? AND invited_by IS NULL",
            (inviter_id, user_id)
        )
        await db.commit()


async def add_referral(inviter_id: int, invited_id: int) -> Tuple[bool, int]:
    """
    Add a referral record and increment inviter's referral count.
    Returns (was_added, new_count).
    """
    async with get_db() as db:
        # Check if referral already exists
        cur = await db.execute(
            "SELECT id FROM referrals WHERE inviter_id = ? AND invited_id = ?",
            (inviter_id, invited_id)
        )
        existing = await cur.fetchone()
        if existing:
            logger.info(f"Referral already exists: inviter={inviter_id}, invited={invited_id}")
            # Get current count
            cur = await db.execute(
                "SELECT referrals_count FROM users WHERE user_id = ?",
                (inviter_id,)
            )
            row = await cur.fetchone()
            current_count = row["referrals_count"] if row and row["referrals_count"] is not None else 0
            return False, current_count

        # Add referral record
        await db.execute(
            "INSERT INTO referrals (inviter_id, invited_id) VALUES (?, ?)",
            (inviter_id, invited_id)
        )
        
        # Get current count and increment
        cur = await db.execute(
            "SELECT referrals_count FROM users WHERE user_id = ?",
            (inviter_id,)
        )
        row = await cur.fetchone()
        current_count = row["referrals_count"] if row and row["referrals_count"] is not None else 0
        new_count = current_count + 1
        
        # Update with new count
        await db.execute(
            "UPDATE users SET referrals_count = ? WHERE user_id = ?",
            (new_count, inviter_id)
        )
        await db.commit()
        
        # Log the action
        logger.info(f"Added referral: inviter={inviter_id}, invited={invited_id}")
        logger.info(f"Inviter {inviter_id} count updated from {current_count} to {new_count}")
        
        return True, new_count


async def referral_count(user_id: int) -> int:
    """Get referral count for a user"""
    async with get_db() as db:
        # Force reading the latest data
        cur = await db.execute(
            "SELECT referrals_count FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cur.fetchone()
        
        # If count is None or seems wrong, recalculate from referrals table
        stored_count = row["referrals_count"] if row and row["referrals_count"] is not None else 0
        
        # Verify against actual referrals (for debugging)
        cur2 = await db.execute(
            "SELECT COUNT(*) as actual FROM referrals WHERE inviter_id = ?",
            (user_id,)
        )
        actual_row = await cur2.fetchone()
        actual_count = actual_row["actual"] if actual_row else 0
        
        if stored_count != actual_count:
            logger.warning(f"User {user_id} count mismatch: stored={stored_count}, actual={actual_count}. Using actual.")
            return actual_count
        
        logger.info(f"User {user_id} has {stored_count} referrals")
        return stored_count


async def get_inviter(user_id: int) -> Optional[int]:
    """Get the ID of the user who invited this user"""
    async with get_db() as db:
        cur = await db.execute(
            "SELECT invited_by FROM users WHERE user_id = ?", 
            (user_id,)
        )
        row = await cur.fetchone()
        inviter = row["invited_by"] if row else None
        logger.info(f"User {user_id} was invited by {inviter}")
        return inviter


async def list_users(limit: int = 1000) -> List[Dict[str, Any]]:
    """Get list of users with their stats"""
    async with get_db() as db:
        cur = await db.execute(
            "SELECT user_id, username, referrals_count, is_member FROM users LIMIT ?",
            (limit,)
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]