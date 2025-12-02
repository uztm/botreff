# bot/keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from .config import settings


def _format_channel_url(channel: str) -> str:
    """
    Convert channel username/ID to proper t.me URL.
    
    Examples:
        @channel -> https://t.me/channel
        -1001234567890 -> https://t.me/c/1234567890
    """
    if channel.startswith('@'):
        return f"https://t.me/{channel[1:]}"
    elif channel.startswith('-100'):
        channel_id = channel[4:]
        return f"https://t.me/c/{channel_id}"
    elif channel.startswith('-'):
        return f"https://t.me/c/{channel[1:]}"
    else:
        return f"https://t.me/{channel}"


def channels_keyboard():
    """Keyboard with channel subscription links"""
    buttons = [
        [InlineKeyboardButton(
            text="1-kanal", 
            url=_format_channel_url(settings.CHANNEL_1)
        )],
        [InlineKeyboardButton(
            text="2-kanal", 
            url=_format_channel_url(settings.CHANNEL_2)
        )],
        [InlineKeyboardButton(
            text="✅ Obunani tekshirish", 
            callback_data="check_subscription"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard():
    """Main menu with buttons at the bottom"""
    keyboard = [
        [KeyboardButton(text="👥 Mening referallarim")],
        [KeyboardButton(text="💬 Aloqa"), KeyboardButton(text="💳 Referalsiz davom etish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang..."
    )


def admin_contact_keyboard():
    """Inline keyboard with admin contact"""
    buttons = [
        [InlineKeyboardButton(
            text="📞 Admin bilan bog'lanish", 
            url="https://t.me/uygonamiz_admin1"
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def private_group_keyboard(group_link: str):
    """Keyboard with private group link"""
    buttons = [
        [InlineKeyboardButton(
            text="🔐 Yopiq guruhga o'tish", 
            url=group_link
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)