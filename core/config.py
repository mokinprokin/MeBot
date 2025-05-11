import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from src.queries.orm import AsyncOrm

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Bot Setup ---
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
ch_username = os.getenv("CHANNEL_USERNAME")
welcome_pic = os.getenv("WELCOME_IMAGE_URL")


class UserState(StatesGroup):
    awaiting_channel_join = State()
    collecting_name = State()
    collecting_about = State()
    collecting_target = State()
    collecting_hobby = State()
    editing_name = State()
    editing_about = State()
    editing_target = State()
    editing_hobby = State()
    regenerating_presentation = State()


name = """✅ Отлично! Продолжим создание вашей самопрезентации.\n
📌 Шаг 1 из 4: Как вы хотите представиться?\n
Напишите имя и фамилию (при необходимости - с отчеством). 
Можно добавить неформальное обращение.\n
Примеры:
• Привет, я Иван (для друзей - Ваня)
• Добрый день, меня зовут Катя
• Здравствуйте, я Светлана, прозвище - Белка"""

about = """📌 Шаг 2 из 4: Расскажите о вашей деятельности.\n
Важно:
• Будьте краткими
• Избегайте занудства
• Не обязательно начинать с 'Я'\n
Примеры:
• Программист на Python с опытом 7 лет
• Владелец вокальной студии с тремя филиалами
• Таролог с 10-летним стажем"""

target = """📌 Шаг 3 из 4: Какая ваша цель в нетворкинге?\n
Примеры:
• Найти партнеров для нового проекта
• Привлечь клиентов для бизнеса
• Познакомиться с единомышленниками"""

hobby = """📌 Шаг 4 из 4: Расскажите о вашем хобби или интересном факте.\n
Примеры:
• Коллекционирую винтажные компьютеры
• Участвую в марафонах
• Пишу картины маслом\n
Если хотите пропустить этот шаг, нажмите кнопку ниже:"""
