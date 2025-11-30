from .. import models
from typing import Optional


async def ensure_user_registered(user_id: int, username: Optional[str], full_name: Optional[str], inviter: Optional[int] = None):
    await models.create_user(user_id, username, full_name, invited_by=inviter)


async def try_register_referral(candidate_user_id: int):
    """
    Agar candidate_user inviterga ega bo'lsa va member bo'lsa:
    referral record qo'shadi va count oshiradi.
    Returns (inviter_id, added:bool)
    """
    inviter = await models.get_inviter(candidate_user_id)
    if not inviter:
        return None, False

    added = await models.add_referral(inviter, candidate_user_id)
    return inviter, added
