# bot/handlers/common.py
from aiogram import Router, types
from aiogram.filters import Command
from ..config import settings

router = Router()


@router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "Bot yordamchi:\n"
        "/start — boshlash\n"
        "/profile — profilingiz va havolangiz\n\n"
        "Qo'shimcha yordam uchun: Admin bilan bog'laning.",
    )
