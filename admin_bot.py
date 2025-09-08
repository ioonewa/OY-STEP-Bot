from Database import Database
from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.filters import CommandStart, BaseFilter
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from loader import database

import random
import string
import config

from dotenv import load_dotenv
import os

import logging

logging.basicConfig(
    level=logging.INFO,
    filemode="w+",
    filename="logs/main_admin_bot.log"
)

load_dotenv()

bot = Bot(
    token=os.getenv("ADMIN_BOT_TOKEN"),
    default=DefaultBotProperties(
        protect_content=True,
        parse_mode=ParseMode.HTML
    )
)
dispatcher = Dispatcher()

database = Database({
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
})

class AccessFilter(BaseFilter):
    async def __call__(self, event: Message) -> bool:
        return event.from_user.id in config.ADMINS

dispatcher.message.filter(AccessFilter())


def generate_code(length=12):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

CREATE_LINK_BTN = "Пригласить людей"

async def main():
    await database.connect()
    await database.create_tables()

    @dispatcher.message(CommandStart())
    async def start(message: Message):
        await message.answer(
            f"<b>Добро пожаловать в Админ-панель OYSTEP</b>\n\nВы можете выдать доступ в OYSTEP (@oystep_bot), для этого создайте пригласительную ссылку <b>\"{CREATE_LINK_BTN}\"</b>",
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text=CREATE_LINK_BTN)]
                ]
            )
        )

    @dispatcher.message(F.text == CREATE_LINK_BTN)
    async def create_code(message: Message):
        code = generate_code()
        
        await database.add_invite_link(
            creator_id=message.from_user.id,
            code=code
        )
        
        invite_link = f"https://t.me/oystep_bot?start={code}"
        
        await message.answer(
            f"<code>{invite_link}</code>\n\n"
            f"👆🏻 Пригласительная ссылка создана\n\n"
            "1. Скопируйте ссылку\n"
            "2. Отправьте ее нужному человеку\n"
            "3. Когда человек воспользуется вашей ссылкой, вы получите уведомление\n\n"
            "❗️ Получить доступ по ссылке сможет только один человек.\n"
            "Если вам нужно добавить несколько людей, нажмите на кнопку \"Пригласить людей\" еще раз",
        )

    await dispatcher.start_polling(bot)

import asyncio

asyncio.run(main())