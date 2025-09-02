from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile
)
from aiogram.enums import ChatAction

from loader import database
from Database.enums.user import UserStatus

from .registration import start_registration
from ..utils import keyboards as kb

import config

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = message.from_user
    status = await database.get_user_status(user.id)

    if status == UserStatus.INVITED:
        await message.answer("<b>Вы были добавлены в фокус группу для Тестирования!</b>")
        await database.update_user_status(user.id, UserStatus.REGISTRATION)
        # Начать регистрацию
        await start_registration(message, state)
    else:
        # Вызвать меню
        await menu(message)

async def menu(message: Message):
    await message.answer(
        "<b>OYBOT</b> - это простой и удобный бот для брокеров.\n\n"
        "<b>Бот позволяем:</b>\n\n"
        "— Создавать персональный контент\n\n"
        "— Смотреть календарь брокеров-туров\n\n"
        "— Получать новые скиллы (раздел \"Обучение\")",
        reply_markup=kb.menu_kb()
    )

@router.message(F.text == kb.LESSONS_BTN)
async def lessons(message: Message):
    await message.answer(
        "<b>Вам доступно 3 видео-урока.</b>\n\n"
        "1. Почему важен личный бренд? | 1:39\n\n"
        "2. Как перестать бояться камеры? | 1:51\n\n"
        "3. Как снимать стильно? | 2:08",
        reply_markup=kb.lessons_kb()
    )

@router.message(F.text == kb.TOURS_BTN)
async def tours(message: Message):
    await message.answer_photo(
        photo="AgACAgIAAxkDAAOdaLacYDPxcVLWqLOoPX7K-_FelE8AAk34MRsbdbBJSSr8FvfJAAFfAQADAgADeQADNgQ",
        caption="""<b>Брокер-туры MR — I половина сентября 2025</b>

Приглашаем на брокер-туры, выбирайте удобную дату, регистрируйтесь и добавляйте событие в свой календарь. 

<b>Начало всех туров — в 11:00</b>

<b>Регистрация</b>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3481076/">МЫ.С</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3067699/">JOIS</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3107158/">City Bay</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3481020/">CITYZEN</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3107001/">МИRА</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3107038/">У Реки. Эко Видное 2.0</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3155215/">Symphony 34</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3155210/">VEER / SET</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3067669/">SLAVA</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3067707/">Метрополия</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3067629/">MOD</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3107071/">Famous</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3107086/">Селигер Сити</a>
🔘 <a href="https://open-list--mr-group.timepad.ru/event/3531754/">One</a>
"""
    )

@router.message(F.text == kb.CHANNEL_BTN)
async def channel(message: Message):
    await message.answer(
        "<b>Вам доступно 2 канала.</b>\n\n"
        f"Приватный канал\n\n"
        "<a href='https://t.me/oystepmediaburo'>Новостной канал</a>",
        reply_markup=kb.channel_invite_kb()
    )

@router.message(F.text == kb.FAQ_BTN)
async def faq(message: Message):
    await message.answer(
        """<b>Часто задаваемые вопросы</b>
        
▫️ Как работает этот бот?
\t\t\t\t- Бот обрабатывает ваши запросы и выдает быстрый результат автоматически.

▫️ Сколько стоит использование бота?
\t\t\t\t- Цена зависит от выбранного тарифа.

▫️ Что делать, если бот не отвечает?
\t\t\t\t- Попробуйте перезапустить чат или повторить запрос через несколько минут.

▫️ Можно ли пользоваться ботом с телефона и компьютера?
\t\t\t\t- Да, бот доступен в Telegram на любых устройствах.

▫️ К кому обращаться при проблемах?
\t\t\t\t- Вы можете написать в поддержку""",
        reply_markup=kb.faq_kb()
    )


@router.message(F.text == kb.SETTINGS_BTN)
async def development(message: Message):
    await message.reply("Данный раздел в разработке")
    
lessons_files = {
    "1": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/2",
        "name": "ПОЧЕМУ ВАЖЕН ЛИЧНЫЙ БРЕНД?"
    },
    "2": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/3",
        "name": "КАК ПЕРЕСТАТЬ БОЯТЬСЯ КАМЕРЫ?"
    },
    "3": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/5",
        "name": "КАК СНИМАТЬ СТИЛЬНО?"
    } 
}

@router.message(F.text == kb.PROFILE_BTN)
async def profile(message: Message):
    user_data = await database.get_user_data_dict(message.from_user.id)
    await message.answer_photo(
        photo=user_data['photo_tg'],
        caption=f"<b>{user_data['name']}</b>\n\n"
        f"https://t.me/{user_data['username']}\n"
        f"{user_data['phone_number']}\n"
        f"{user_data['email']}"
    )

@router.callback_query(F.data.startswith("lesson:"))
async def lesson_id(call: CallbackQuery):
    lesson_id = call.data.replace("lesson:", "")

    lesson = lessons_files.get(lesson_id)
    if not lesson:
        await call.answer("Видео-урок недоступен")
        return
    
    await call.bot.send_chat_action(
        call.from_user.id,
        action=ChatAction.UPLOAD_VIDEO
    )
    await call.message.answer_video(
        video=lesson['url'],
        caption=lesson['name']
    )
    await call.answer()

@router.callback_query()
async def development(call: CallbackQuery):
    await call.answer(f"В разработке")