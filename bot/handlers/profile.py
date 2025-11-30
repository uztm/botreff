# bot/handlers/profile.py
from aiogram import Router, types
from aiogram.filters import Command
from .. import models
from ..config import settings

router = Router()


@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    user = message.from_user
    row = await models.get_user(user.id)
    if not row:
        await message.answer("Profil topilmadi. /start orqali ro'yxatdan o'ting.")
        return

    referrals = row["referrals_count"]
    await message.answer(
        f"Profilingiz:\n• Referallar: {referrals}/7\n\n"
        f"Sizning havolangiz:\nhttps://t.me/{settings.BOT_USERNAME}?start={user.id}"
    )
