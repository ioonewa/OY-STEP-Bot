from aiogram import Router, F
from aiogram.types import (
    Message
)
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from ..utils import keyboards as kb
from ..utils.states import Registration
from ..utils.stash import stash_img

import re
import os

from loader import database

import asyncio

import logging

logger = logging.getLogger(__name__)


router = Router()

# ---------- START REGISTRATION ----------
async def start_registration(message: Message, state: FSMContext):
    await message.answer(
        "Пройдите регистрацию, чтобы получить доступ к:\n\n"
        "🔒 Приватному телеграм каналу с топовой информацией\n\n"
        "⭐️ Персональному контенту для ваших соцсетей\n\n"
        "🔥 Обучению: Как выйти на новый уровень продаж\n\n"
        "🏙 Календарю брокер-туров"
    )
    await message.bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING
    )
    await asyncio.sleep(1)

    await input_name(message, state)

async def input_name(message: Message, state: FSMContext):
    await message.answer(
        "🟩⬜️⬜️⬜️\n[ 1/4 ]\n\n<b>Напишите свое Имя и Фамилию (в одном сообщение)</b>",
        reply_markup=kb.remove_kb()
    )
    await state.set_state(Registration.name)


async def input_phone(message: Message, state: FSMContext):
    await message.answer(
        "🟩🟩⬜️⬜️\n[ 2/4 ]\n\n<b>Напишите ваш Номер телефона (в формате +7...)</b>",
        reply_markup=kb.pin_phone_kb()
    )
    await state.set_state(Registration.phone_number)


async def input_email(message: Message, state: FSMContext):
    await message.answer(
        "🟩🟩🟩⬜️\n[ 3/4 ]\n\n<b>Напишите ваш Email</b>",
        reply_markup=kb.back_kb()
    )
    await state.set_state(Registration.email)


async def input_photo(message: Message, state: FSMContext):
    await message.answer(
        "🟩🟩🟩🟩\n[ 4/4 ]\n\n<b>Прикрепите вашу Фотографию</b>",
        reply_markup=kb.back_kb()
    )
    await state.set_state(Registration.photo)

# ---------- VALIDATION ----------
def validate_phone(phone_raw: str) -> str | None:
    """Проверка и нормализация номера в формат +7XXXXXXXXXX"""
    phone = re.sub(r"\D", "", phone_raw)

    # Заменяем 8 на 7
    if phone.startswith("8"):
        phone = "7" + phone[1:]

    if not phone.startswith("7"):
        return None

    if len(phone) != 11:
        return None

    return f"+{phone}"

async def finish_registration(message: Message, state: FSMContext):
    reg_data = await state.get_data()
    user_id = message.from_user.id

    try:
        await database.registrate_user(
            telegram_id=user_id,
            **reg_data
        )
        logger.info(f"Пользователь {user_id} успешно завершил регистрацию")
    except Exception as ex:
        logging.error(f"Не получилось зарегистрировать пользователя ({user_id}): {reg_data} - {ex}")
        await message.reply(f"Не получилось зарегистрировать вас. Для решения проблемы обратитесь к @ionewa")
        return

    await state.clear()
    
    # Функция menu в interface, нужно убрать повтор
    await message.answer(
        "<b>OYBOT</b> - это простой и удобный бот для брокеров.\n\n"
        "<b>Бот позволяет:</b>\n\n"
        "— Создавать персональный контент\n\n"
        "— Смотреть календарь брокеров-туров\n\n"
        "— Получать новые скиллы (раздел \"Обучение\")",
        reply_markup=kb.menu_kb()
    )
    # Выдаем доступ в канал
    await message.answer(
        "<b>Вам открыт доступ в приватный канал</b>",
        reply_markup=kb.channel_invite_kb()
    )
    


# ---------- NAME HANDLERS ----------
@router.message(F.text, Registration.name)
async def reg_stage_2(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name.split(" ")) != 2:
        await message.reply("Ваше сообщение должно содержать Имя и Фамилию, попробуйте ещё раз")
        return
    
    await state.update_data(name=name)
    await input_phone(message, state)

@router.message(Registration.phone_number, F.text == kb.BACK_BTN)
@router.message(Registration.name)
async def reg_stage_2_wrong(message: Message, state: FSMContext):
    await input_name(message, state)


# ---------- PHONE HANDLERS ----------
@router.message(F.contact, Registration.phone_number)
async def reg_stage_3_contact(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.reply("Можно отправлять только свой контакт")
        return
    
    phone = validate_phone(contact.phone_number)
    if not phone:
        await message.reply("Номер некорректный, попробуйте снова")
        return
    
    await state.update_data(phone_number=phone)
    await input_email(message, state)


@router.message(F.text, Registration.phone_number)
async def reg_stage_3_text(message: Message, state: FSMContext):
    phone = validate_phone(message.text)
    if not phone:
        await message.reply("Номер некорректный, попробуйте снова")
        return
    
    await state.update_data(phone_number=phone)
    await input_email(message, state)

@router.message(Registration.email, F.text == kb.BACK_BTN)
@router.message(Registration.phone_number)
async def reg_stage_3_wrong(message: Message, state: FSMContext):
    await input_phone(message, state)


# ---------- EMAIL HANDLERS ----------
@router.message(F.text, Registration.email)
async def reg_stage_4(message: Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        await message.reply("Некорректный email, попробуйте снова")
        return
    
    await state.update_data(email=email)
    await input_photo(message, state)

@router.message(Registration.photo, F.text == kb.BACK_BTN)
@router.message(F.text, Registration.email)
async def reg_stage_4_wrong(message: Message, state: FSMContext):
    await input_email(message, state)

# ---------- PHOTO HANDLERS ----------
@router.message(F.photo | F.document, Registration.photo)
async def reg_stage_5(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    save_dir = f"photos/{tg_id}"
    os.makedirs(save_dir, exist_ok=True)
    file_path = f"{save_dir}/photo.png"

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id
    else:
        await input_photo(message, state)
        return

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    tg_photo_id = await stash_img(file_path)

    await state.update_data(
        photo_source=file_path,
        photo_tg=tg_photo_id
    )

    await finish_registration(message, state)

@router.message(Registration.photo)
async def reg_stage_5_wrong(message: Message, state: FSMContext):
    await input_photo(message, state)