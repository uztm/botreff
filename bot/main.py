# bot/main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings
from .db import init_db
from .handlers import start as start_h, profile as profile_h, common as common_h, join_request as join_req_h

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = settings.BOT_TOKEN


async def main():
    """Main bot entry point"""
    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Create bot instance with HTML parse mode
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Create dispatcher with memory storage
    dp = Dispatcher(storage=MemoryStorage())

    # Register all routers
    dp.include_router(start_h.router)
    dp.include_router(profile_h.router)
    dp.include_router(common_h.router)
    dp.include_router(join_req_h.router)

    try:
        logger.info("Bot is starting...")
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except (TelegramAPIError, TelegramNetworkError) as e:
        logger.exception("Telegram API error occurred: %s", e)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

    except Exception as e:
        logger.exception("Unexpected error occurred: %s", e)

    finally:
        logger.info("Shutting down bot...")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")