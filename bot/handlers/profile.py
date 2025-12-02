# bot/handlers/profile.py
from aiogram import Router, types
from aiogram.filters import Command
from .. import models
from ..config import settings
from ..keyboards import main_menu_keyboard

router = Router()


@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    """Show user profile with referral count and link"""
    user = message.from_user
    row = await models.get_user(user.id)
    
    if not row:
        await message.answer(
            "❌ Profil topilmadi. Iltimos /start buyrug'ini yuboring.",
            reply_markup=main_menu_keyboard()
        )
        return

    referrals = row["referrals_count"]
    is_member = row["is_member"]
    ref_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.id}"
    
    status = "✅ Faol a'zo" if is_member else "⏳ Kanalga obuna bo'lmagan"
    
    profile_text = (
        f"👤 Sizning profilingiz:\n\n"
        f"📊 Referallar: {referrals}/7\n"
        f"📍 Status: {status}\n\n"
    )
    
    if referrals >= 7:
        profile_text += (
            f"🎊 TABRIKLAYMIZ!\n"
            f"Siz 7 ta referalni to'pladingiz va yopiq guruhga kirish huquqini oldingiz! 🔐"
        )
    else:
        profile_text += (
            f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n"
            f"🎯 Yana {7 - referrals} ta referal kerak!"
        )
    
    await message.answer(profile_text, reply_markup=main_menu_keyboard())