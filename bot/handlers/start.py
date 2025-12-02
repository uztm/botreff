# bot/handlers/start.py
from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart
from ..services.subscription import check_subscriptions
from ..services import referral as referral_service
from .. import models
from ..keyboards import channels_keyboard, main_menu_keyboard, admin_contact_keyboard, private_group_keyboard
from ..config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: types.Message, bot: Bot):
    """Handle /start command with optional referral parameter"""
    args = message.text.split(maxsplit=1)
    ref = None
    if len(args) > 1:
        try:
            ref = int(args[1])
        except (ValueError, TypeError):
            ref = None

    user = message.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    
    # Register user in database
    await referral_service.ensure_user_registered(
        user.id, 
        user.username, 
        full_name, 
        inviter=ref
    )

    # Send greeting message first
    greeting = (
        f"👋 Assalomu aleykum, {user.first_name}!\n\n"
        "🎉 Yopiq kanal marafonimizga xush kelibsiz!\n\n"
        "📚 Bu yerda siz:\n"
        "• Qimmatli ma'lumotlar\n"
        "• Eksklyuziv kontentlar\n"
        "• Foydali resurslar olasiz\n\n"
        "Davom etish uchun quyidagi kanallarga obuna bo'ling 👇"
    )
    
    await message.answer(
        greeting,
        reply_markup=main_menu_keyboard()
    )

    # Check subscription status
    missing = await check_subscriptions(bot, user.id)

    if missing:
        await message.answer(
            "📢 \"Uyg'onamiz ummat qizlari\" 9-mavsumda qatnashish uchun quyidagi sahifalarimizga obuna bo'ling!\n\n"
            "Obuna bo'lgandan keyin '✅ Obunani tekshirish' tugmasini bosing.",
            reply_markup=channels_keyboard()
        )
    else:
        # Already subscribed
        await show_subscribed_message(message, bot, user.id, ref)


async def show_subscribed_message(message: types.Message, bot: Bot, user_id: int, ref: int = None):
    """Show message after successful subscription"""
    # Mark user as member
    await models.set_user_member(user_id)
    
    # Try to register referral if user came via referral link
    if ref:
        logger.info(f"User {user_id} came via referral link from {ref}")
        inviter_id, added, ref_count = await referral_service.try_register_referral(user_id)
        logger.info(f"try_register_referral returned: inviter_id={inviter_id}, added={added}, count={ref_count}")
        
        if added and inviter_id:
            try:
                # Get the invited user's info
                invited_user = await bot.get_chat(user_id)
                logger.info(f"Sending notification to {inviter_id} with count {ref_count}")
                
                await bot.send_message(
                    inviter_id,
                    f"🎉 Yangi referal!\n\n"
                    f"👤 {invited_user.first_name} sizning havolangiz orqali qo'shildi! \n\n Harakat qilishni davom ettiring. Albatta, bu marafonda qatnasha olasiz 😌\n\n"
                    f"📊 Sizning referallaringiz: {ref_count}/7"
                    f"Qatnashish uchun yana bir yo'lingiz bor. Batafsil ma'lumot uchun: \n\n"
                    f"Referallarsiz davom etish tugmasini bosing!"
                )
                
                # Check if inviter reached 7 referrals
                if ref_count >= 7:
                    await send_private_group_access(bot, inviter_id)
            except Exception as e:
                logger.error(f"Error notifying inviter {inviter_id}: {e}")
        else:
            logger.warning(f"Referral not added: inviter_id={inviter_id}, added={added}")

    # Check user's own referral count
    user_ref_count = await models.referral_count(user_id)
    
    if user_ref_count >= 7:
        # User has 7+ referrals, give access
        await send_private_group_access(bot, user_id)
    else:
        # Show referral link
        ref_link = f"https://t.me/{settings.BOT_USERNAME}?start={user_id}"
        await message.answer(
            f"✅ Ajoyib! Siz kanallarga muvaffaqiyatli obuna bo'ldingiz!\n\n"
            f"🎯 Marafonda qatnashish uchun birinchi qadamni bajardingiz. \n\nEndi 7ta do'stingizga ham quyidagi havolani ulashing va yopiq kanalimiz uchun havolani qo'lga kiriting.\n\n"
            f"📊 Sizning referallaringiz: {user_ref_count}/7\n\n"
            f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n"
            f"💡 Havolani do'stlaringizga yuboring va ular botni boshlashini kuting!"
        )


async def send_private_group_access(bot: Bot, user_id: int):
    """Send private group link to user who has 7 referrals"""
    private_group_link = settings.PRIVATE_GROUP_LINK
    
    await bot.send_message(
        user_id,
        "🎊 TABRIKLAYMIZ! 🎊\n\n"
        "🌟 Siz 7 ta referal to'pladingiz va yopiq guruhga kirish huquqini qo'lga kiritdingiz!\n\n"
        "👇 Quyidagi tugmani bosib guruhga qo'shilish so'rovini yuboring.\n"
        "Bot avtomatik ravishda sizni tasdiqlaydi.",
        "15kunlik marafonimizda qatnashing!",
        reply_markup=private_group_keyboard(private_group_link)
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery, bot: Bot):
    """Handle subscription check button"""
    user = callback.from_user
    
    # Check subscription status
    missing = await check_subscriptions(bot, user.id)

    if missing:
        await callback.answer(
            "❌ Siz hali barcha kanallarga obuna bo'lmagansiz!\n\n"
            "Iltimos, avval barcha kanallarga obuna bo'ling.",
            show_alert=True
        )
        return

    # Mark user as member
    await models.set_user_member(user.id)
    
    # Check if user came via referral
    inviter_id = await models.get_inviter(user.id)
    logger.info(f"Callback: User {user.id} has inviter: {inviter_id}")
    
    if inviter_id:
        inviter_id_result, added, ref_count = await referral_service.try_register_referral(user.id)
        logger.info(f"Callback: try_register_referral returned: inviter_id={inviter_id_result}, added={added}, count={ref_count}")
        
        if added and inviter_id_result:
            try:
                # Get the invited user's info
                invited_user = await bot.get_chat(user.id)
                logger.info(f"Callback: Sending notification to {inviter_id_result} with count {ref_count}")
                
                await bot.send_message(
                    inviter_id_result,
                    f"🎉 Yangi referal!\n\n"
                    f"👤 {invited_user.first_name} sizning havolangiz orqali qo'shildi!\n\n"
                    f"📊 Sizning referallaringiz: {ref_count}/7"
                )
                
                # Check if inviter reached 7 referrals
                if ref_count >= 7:
                    await send_private_group_access(bot, inviter_id_result)
            except Exception as e:
                logger.error(f"Error notifying inviter {inviter_id_result}: {e}")
        else:
            logger.warning(f"Callback: Referral not added: inviter_id={inviter_id_result}, added={added}")

    # Check user's referral count
    user_ref_count = await models.referral_count(user.id)
    
    if user_ref_count >= 7:
        # User already has 7+ referrals
        await send_private_group_access(bot, user.id)
        await callback.message.edit_text(
            "✅ Obuna tasdiqlandi!\n\n"
            "🎊 Siz allaqachon 7 ta referal to'plab bo'lgansiz!\n"
            "Yopiq guruh havolasi yuqorida yuborildi."
        )
    else:
        # Show referral link
        ref_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.id}"
        await callback.message.edit_text(
            f"✅ Ajoyib! Siz kanallarga muvaffaqiyatli obuna bo'ldingiz!\n\n"
            f"🎯 Endi yopiq guruhga kirish uchun 7 ta do'stingizni taklif qiling.\n\n"
            f"📊 Sizning referallaringiz: {user_ref_count}/7\n\n"
            f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n"
            f"💡 Havolani do'stlaringizga yuboring va ular botni boshlashini kuting!"
        )
    
    await callback.answer("✅ Obuna tasdiqlandi!")


@router.message(F.text == "👥 Mening referallarim")
async def my_referrals_handler(message: types.Message):
    """Show user's referral statistics"""
    user = message.from_user
    row = await models.get_user(user.id)
    
    if not row:
        await message.answer(
            "❌ Profil topilmadi. Iltimos /start buyrug'ini yuboring.",
            reply_markup=main_menu_keyboard()
        )
        return

    referrals = row["referrals_count"] if row["referrals_count"] is not None else 0
    logger.info(f"User {user.id} referrals from DB: {referrals}, row data: {dict(row)}")
    ref_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.id}"
    
    if referrals >= 7:
        await message.answer(
            f"🎊 TABRIKLAYMIZ!\n\n"
            f"✅ Siz 7 ta referalni to'pladingiz!\n"
            f"📊 Jami referallar: {referrals}/7\n\n"
            f"🔐 Yopiq guruhga kirish huquqingiz faol.",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            f"📊 Sizning statistikangiz:\n\n"
            f"👥 Referallar: {referrals}/7\n"
            f"🎯 Qolgan: {7 - referrals} ta\n\n"
            f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n"
            f"💡 Havolani do'stlaringizga ulashing!",
            reply_markup=main_menu_keyboard()
        )


@router.message(F.text == "💬 Aloqa")
async def contact_handler(message: types.Message):
    """Show contact information"""
    await message.answer(
        "📞 Admin bilan bog'lanish:\n\n"
        "Savollaringiz yoki muammolaringiz bo'lsa, admin bilan bog'laning.",
        reply_markup=admin_contact_keyboard()
    )


@router.message(F.text == "💳 Referalsiz davom etish")
async def continue_without_referral_handler(message: types.Message):
    """Handle continue without referral option"""
    await message.answer(
        "💳 Referalsiz davom etish\n\n"
        "Agar siz 7 ta referal to'play olmasangiz, yopiq guruhga to'g'ridan-to'g'ri "
        "kirish uchun admin bilan bog'lanishingiz mumkin.\n\n"
        "Admin sizga to'lov variantlarini taklif qiladi.",
        reply_markup=admin_contact_keyboard()
    )