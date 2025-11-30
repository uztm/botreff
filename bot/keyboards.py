# bot/keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import settings


def admin_contact_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Admin bilan bog'lanish", url=f"https://t.me/your_admin"))
    return kb


def join_help_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Kanal 1", url=settings.CHANNEL_1))
    kb.add(InlineKeyboardButton("Kanal 2", url=settings.CHANNEL_2))
    kb.add(InlineKeyboardButton("Admin bilan bog'lanish", url=f"https://t.me/your_admin"))
    return kb
