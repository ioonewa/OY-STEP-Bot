from loader import bot, database
from Bot import dispatcher

from aiogram.types import BotCommand

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    filemode="w+",
    filename="logs/main.log"
)


async def main():
    await database.connect()
    await database.create_tables()

    await bot.set_my_commands([
        BotCommand(command='start', description='Начать')
    ])

    await dispatcher.start_polling(bot)


asyncio.run(main())