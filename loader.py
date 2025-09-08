from dotenv import load_dotenv
import os

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from Database import Database

from config import DIRS

# Подгружаем данные окружения
load_dotenv()

# Создаем необходимые директории
for dir in DIRS:
    os.makedirs(dir, exist_ok=True)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(
        protect_content=True,
        parse_mode=ParseMode.HTML
    )
)

admin_bot = Bot(
    token=os.getenv("ADMIN_BOT_TOKEN"),
    default=DefaultBotProperties(
        protect_content=True,
        parse_mode=ParseMode.HTML
    )
)

database = Database({
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
})