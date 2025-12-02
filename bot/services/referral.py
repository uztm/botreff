# bot/services/referral.py
from .. import models
from typing import Optional, Tuple


async def ensure_user_registered(
    user_id: int, 
    username: Optional[str], 
    full_name: Optional[str], 
    inviter: Optional[int] = None
):
    """
    Register user in database if not already registered.
    Will not overwrite existing user data.
    """
    # Check if user already exists
    existing_user = await models.get_user(user_id)
    
    if not existing_user:
        # New user - register with inviter
        await models.create_user(user_id, username, full_name, invited_by=inviter)
    elif existing_user["invited_by"] is None and inviter is not None:
        # User exists but has no inviter - update inviter
        await models.update_user_inviter(user_id, inviter)


async def try_register_referral(candidate_user_id: int) -> Tuple[Optional[int], bool, int]:
    """
    If candidate_user has an inviter, add referral record and increment count.
    
    Returns:
        Tuple of (inviter_id, was_added, new_count)
    """
    inviter_id = await models.get_inviter(candidate_user_id)
    if not inviter_id:
        return None, False, 0

    was_added, new_count = await models.add_referral(inviter_id, candidate_user_id)
    return inviter_id, was_added, new_count