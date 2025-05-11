from typing import Dict, Any
from aiogram import Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
)
from .utils import descriptionCreator, get_description
from config import logger,ch_username,bot,UserState


async def validate_channel_membership(user_id: int) -> bool:
    """Check if user is a channel member"""
    try:
        chat_member = await bot.get_chat_member(chat_id=ch_username, user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
        return False


async def generate_presentation(user_data: Dict[str, Any]) -> str:
    """Generate presentation text using GigaChat"""
    try:
        prompt = descriptionCreator(
            name=user_data["name"],
            about=user_data["about"],
            target=user_data.get("target"),
            hobby=user_data.get("hobby"),
        )
        return await get_description(prompt)
    except Exception as e:
        logger.error(f"Error generating presentation: {e}")
        return (
            "⚠️ Не удалось сгенерировать самопрезентацию. "
            "Попробуйте позже или свяжитесь с поддержкой."
        )


