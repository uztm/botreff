# bot/handlers/join_request.py
from aiogram import Router, types, Bot
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated
from .. import models
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.chat_join_request()
async def handle_join_request(chat_join_request: types.ChatJoinRequest, bot: Bot):
    """
    Handle join requests to the private group.
    Auto-approve users who have 7+ referrals.
    """
    user_id = chat_join_request.from_user.user_id
    chat_id = chat_join_request.chat.id
    
    logger.info(f"Join request from user {user_id} to chat {chat_id}")
    
    # Check user's referral count
    try:
        ref_count = await models.referral_count(user_id)
        
        if ref_count >= 7:
            # User has 7+ referrals, approve the request
            await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            
            # Send confirmation message
            await bot.send_message(
                user_id,
                "✅ Tabriklaymiz!\n\n"
                "Sizning so'rovingiz tasdiqlandi. Yopiq guruhga xush kelibsiz! 🎉"
            )
            
            logger.info(f"Approved join request for user {user_id} (refs: {ref_count})")
        else:
            # User doesn't have enough referrals, decline
            await bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
            
            # Send explanation message
            await bot.send_message(
                user_id,
                f"❌ Afsuski, sizning so'rovingiz rad etildi.\n\n"
                f"📊 Sizda {ref_count}/7 referal bor.\n"
                f"🎯 Yana {7 - ref_count} ta referal to'plang yoki admin bilan bog'laning.\n\n"
                f"💡 Mening referallarim menyusidan havolangizni oling.",
            )
            
            logger.info(f"Declined join request for user {user_id} (refs: {ref_count})")
            
    except Exception as e:
        logger.error(f"Error handling join request for user {user_id}: {e}")
        # In case of error, decline to be safe
        try:
            await bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
        except Exception:
            pass