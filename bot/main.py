import asyncio
import logging

from aiogram import Bot, Dispatcher, exceptions
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from .config import settings
from .db import init_db
from .handlers import start as start_h, profile as profile_h, common as common_h

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = settings.BOT_TOKEN


async def main():
    # Initialize DB
    await init_db()

    # Aiogram 3.7+: parse_mode now goes into DefaultBotProperties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start_h.router)
    dp.include_router(profile_h.router)
    dp.include_router(common_h.router)

    try:
        logger.info("Bot is starting...")
        await dp.start_polling(bot)

    except (exceptions.TelegramAPIError, exceptions.NetworkError) as e:
        logger.exception("Polling stopped with exception: %s", e)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
