from aiogram import Bot
from src.queries.orm import AsyncOrm
import asyncio
from aiogram.fsm.strategy import FSMStrategy
from config import logger


async def on_startup(bot: Bot):
    """Initialize on startup"""
    await AsyncOrm.create_tables()
    logger.info("Bot started")


async def on_shutdown(bot: Bot):
    """Cleanup on shutdown"""
    logger.info("Bot shutting down...")





async def main():
    from config import bot,dp
    import utils.handlers
    dp.fsm.strategy = FSMStrategy.USER_IN_CHAT

    await on_startup(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":

    asyncio.run(main())
