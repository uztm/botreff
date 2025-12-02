# bot/services/subscription.py
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from typing import List
from ..config import settings


CHANNELS = [settings.CHANNEL_1, settings.CHANNEL_2]


async def check_subscriptions(bot: Bot, user_id: int) -> List[str]:
    """
    Check user's subscription status for all required channels.
    
    Returns:
        List of channel IDs where user is NOT a member.
    """
    missing = []
    
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            # Valid member statuses
            if member.status not in ("member", "administrator", "creator"):
                missing.append(ch)
        except TelegramBadRequest:
            # User not found in chat or bot doesn't have access
            missing.append(ch)
        except Exception as e:
            # Any other error - assume user is not subscribed to be safe
            missing.append(ch)
    
    return missing