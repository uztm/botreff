# bot/services/subscription.py
from aiogram import Bot
from typing import List
from ..config import settings


CHANNELS = [settings.CHANNEL_1, settings.CHANNEL_2]


async def check_subscriptions(bot: Bot, user_id: int) -> List[str]:
    """
    Returns list of channels where user is NOT a member.
    """
    missing = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            status = member.status  # 'left', 'member', 'administrator', 'creator', 'restricted', 'kicked'
            if status not in ("member", "administrator", "creator"):
                missing.append(ch)
        except Exception:
            # If bot is not admin or can't access chat, assume missing to be safe
            missing.append(ch)
    return missing
