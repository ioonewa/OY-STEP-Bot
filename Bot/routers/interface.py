from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery
)
from aiogram.enums import ChatAction

from loader import database
from Database.enums.user import UserStatus

from .registration import start_registration, validate_phone
from ..utils import keyboards as kb
from ..utils.states import Edit
from ..utils.stash import stash_img

import config

router = Router()

@router.message(Edit.name, F.text == kb.BACK_BTN)
@router.message(Edit.email, F.text == kb.BACK_BTN)
@router.message(Edit.phone_number, F.text == kb.BACK_BTN)
@router.message(Edit.photo, F.text == kb.BACK_BTN)
async def cancel_edit(message: Message, state: FSMContext):
    await state.clear()
    await menu(message)

@router.message(Edit.name, F.text)
async def edit_name(message: Message, state: FSMContext):
    name = message.text

    if len(name) > config.NAME_LIMIT:
        await message.reply(f"Имя слишко длинное, максимальное кол-во символов - {config.NAME_LIMIT}")
        return

    await database.execute(
        'UPDATE users SET name = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        name, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(Edit.email, F.text)
async def edit_email(message: Message, state: FSMContext):
    email = message.text

    if len(email) > config.NAME_LIMIT:
        await message.reply(f"Имя слишко длинное, максимальное кол-во символов - {config.NAME_LIMIT}")
        return

    await database.execute(
        'UPDATE users SET email = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        email, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(Edit.phone_number, F.text)
async def edit_phone_number(message: Message, state: FSMContext):
    phone_number = message.text

    phone_number = validate_phone(phone_number)
    if not phone_number:
        await message.reply("Номер некорректный, попробуйте снова")
        return

    await database.execute(
        'UPDATE users SET phone_number = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        phone_number, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(F.contact, Edit.phone_number)
async def edit_phone_number_contact(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.reply("Можно отправлять только свой контакт")
        return
    
    phone_number = validate_phone(contact.phone_number)
    if not phone_number:
        await message.reply("Номер некорректный, попробуйте снова")
        return
    
    await database.execute(
        'UPDATE users SET phone_number = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        phone_number, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(F.photo | F.document, Edit.photo)
async def edit_photo(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    save_dir = f"photos/{tg_id}"
    file_path = f"{save_dir}/photo.png"

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    tg_photo_id = await stash_img(file_path)
    await database.execute(
        'UPDATE users SET photo_tg = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        tg_photo_id, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)


@router.message(Edit.name)
@router.message(Edit.email)
@router.message(Edit.phone_number)
@router.message(Edit.photo)
async def wrong_input(message: Message):
    await message.answer("Недопустимый формат ввода", reply_markup=kb.back_kb())

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
        "<b>Бот позволяет:</b>\n\n"
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
        "<b>Вам доступно 2 канала.</b>",
        reply_markup=kb.channels_kb()
    )

@router.message(F.text == kb.FAQ_BTN)
async def faq(message: Message):
    await message.answer(
        """<b>Часто задаваемые вопросы</b>
        
<b>Как работает этот бот</b>
- Бот обрабатывает ваши запросы и выдает быстрый результат автоматически.

<b>Сколько стоит использование бота?</b>
- Цена зависит от выбранного тарифа.

<b>Что делать, если бот не отвечает?</b>
- Попробуйте перезапустить чат или повторить запрос через несколько минут.

<b>Можно ли пользоваться ботом с телефона и компьютера?</b>
- Да, бот доступен в Telegram на любых устройствах.

<b>К кому обращаться при проблемах?</b>
- Вы можете написать в поддержку""",
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
        f"{user_data['email']}\n\n"
        "Чтобы редактировать профиль, воспользуйтесь кнопками\n"
        "👇🏻",
        reply_markup=kb.edit_profile_kb()
    )

@router.callback_query(F.data.startswith("edit:"))
async def edit_profile(call: CallbackQuery, state: FSMContext):
    field = call.data.replace("edit:", "")
    
    reply_markup = kb.back_kb()

    if field == "name":
        text = "<b>Напишите свое Имя и Фамилию (в одном сообщение)</b>"
        state_name = Edit.name
    elif field == "phone_number":
        text = "<b>Напишите ваш Номер телефона (в формате +7...)</b>"
        state_name = Edit.phone_number
        reply_markup = kb.pin_phone_kb()
    elif field == "photo":
        text = "<b>Прикрепите вашу Фотографию</b>"
        state_name = Edit.photo
    elif field == "email":
        text = "<b>Напишите ваш Email</b>"
        state_name = Edit.email
    
    await call.message.answer(text, reply_markup=reply_markup)
    await state.set_state(state_name)

    await call.message.edit_reply_markup()

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
async def hide_content(call: CallbackQuery):
    await call.message.delete()

@router.callback_query()
async def development(call: CallbackQuery):
    await call.answer(f"В разработке")