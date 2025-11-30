# bot/handlers/start.py
from aiogram import Router, types, Bot
from aiogram.filters import CommandStart
from ..services.subscription import check_subscriptions
from ..services import referral as referral_service
from .. import models
from ..keyboards import join_help_kb
from ..config import settings

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, bot: Bot):
    args = message.text.split(maxsplit=1)
    ref = None
    if len(args) > 1:
        # Accept start with argument: /start <referrer_id> or t.me/BOT?start=123
        try:
            ref = int(args[1])
        except Exception:
            ref = None

    user = message.from_user
    await referral_service.ensure_user_registered(user.id, user.username, f"{user.first_name or ''} {user.last_name or ''}".strip(), inviter=ref)

    missing = await check_subscriptions(bot, user.id)

    if len(missing) == 2:
        await message.answer(
            "Soliham, kanallarimizga obuna bo'lishingizni so'raymiz.",
            reply_markup=join_help_kb()
        )
        return

    if len(missing) == 1:
        await message.answer(
            "Marafonda qatnashish uchun, ikkinchi kanalimizga ham obuna bo'lishingizni so'raymiz.",
            reply_markup=join_help_kb()
        )
        return

    # both channels joined
    await message.answer(
        "Marafonda qatnashish uchun birinchi qadamni bajardingiz.\n"
        "Endi 7ta do'stingizga havolani ulashing va yopiq kanal havolasini oling.\n\n"
        f"Sizning referal havolangiz:\nhttps://t.me/{settings.BOT_USERNAME}?start={user.id}",
        reply_markup=join_help_kb()
    )
