from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InputMediaPhoto
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import CommandStart, CommandObject
from ..utils import keyboards as kb
from ..utils.get_content import get_personal_photo

from .interface import menu

from Database.enums.media_files import FileTypes

from loader import database

from typing import Optional

import logging

router = Router()

# https://t.me/oystep_bot?start=post1
# https://t.me/oystep_bot?start=2
# https://t.me/oystep_bot?start=3
# https://t.me/oystep_bot?start=4
# https://t.me/oysteptest_bot?start=2

async def get_post_preview(
        message: Message,
        post_id: int,
        style: Optional[str] = None,
        need_replace: bool = False
    ):

    styles = await database.get_post_styles(post_id)
    

    if not style:
        style = styles[0]

    preview = await database.get_content_files(
        post_id=post_id,
        style=style,
        file_type=FileTypes.STYLE_PREVIEW
    )

    preview = preview[0]

    reply_markup = reply_markup=kb.post_styles_kb(post_id, styles, style)
    text="Выберите шаблон для генерации публикации/истории"

    if not need_replace:
        await message.answer_photo(
            photo=preview,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await message.edit_media(
            media=InputMediaPhoto(media=preview, caption=text),
            reply_markup=kb.post_styles_kb(post_id, styles, style)
        )

@router.callback_query(F.data.startswith("preview:"))
async def change_vars(call: CallbackQuery):
    place, post_id, style  = call.data.split(":")

    post_id = int(post_id)

    await get_post_preview(
        call.message,
        post_id, style,
        need_replace=True
    )

# Получение контента для Пост
@router.callback_query(F.data.startswith("post:"))
async def get_post_content(call: CallbackQuery):
    user_id = call.from_user.id
    place, post_id, style  = call.data.split(":")
    post_id = int(post_id)

    files = await database.get_content_files(
        post_id=post_id,
        style=style,
        file_type=FileTypes.POST_PHOTO
    )

    user_data = await database.get_user_data_dict(user_id)
    personal_photo_id = await get_personal_photo(
        user_data=user_data,
        style=style,
        telegram_id=user_id,
        post_id=post_id,
        obj="post"
    )

    files.append(personal_photo_id)

    caption = await database.get_post_text(post_id)

    media_group = MediaGroupBuilder(
        caption=caption + f"\n\nНапиши мне, и я помогу выбрать лучшую квартиру: @{user_data['username']}",
        media=[
            InputMediaPhoto(media=file) for file in files
        ]
    )

    await call.message.answer_media_group(media=media_group.build(), protect_content=False)
    # Место для обучалки
    await send_instructions(call.message, "post")
    await call.answer()

# Получение контента для Истории
@router.callback_query(F.data.startswith("story:"))
async def get_content_story(call: CallbackQuery):
    user_id = call.from_user.id
    place, post_id, style  = call.data.split(":")
    post_id = int(post_id)

    files = await database.get_content_files(
        post_id=post_id,
        style=style,
        file_type=FileTypes.STORY_PHOTO
    )

    user_data = await database.get_user_data_dict(user_id)
    personal_photo_id = await get_personal_photo(
        user_data=user_data,
        style=style,
        telegram_id=user_id,
        post_id=post_id,
        obj="story"
    )

    files.append(personal_photo_id)

    media_group = MediaGroupBuilder(
        media=[
            InputMediaPhoto(media=file) for file in files
        ]
    )

    await call.message.answer_media_group(media=media_group.build(), protect_content=False)
    # Место для обучалки
    await send_instructions(call.message, "story")
    await call.answer()

instructions = {
    "story": {
        "tg": """👆🏻 <b>Как выложить историю в Telegram</b>

1. Откройте фото → нажмите ⋯ → Сохранить

2. Вверху главного экрана нажмите Моя история (+).

3. Выберите фото из Галереи

4. При необходимости отредактируйте.

5. Нажмите Опубликовать и выберите, кто увидит историю.""",
        "ig": """👆🏻 <b>Как выложить историю в Instagram</b>

1. Сохраните фото в Галерею.

2. Откройте Instagram → нажмите (+) → История.

3. Выберите фото из Галереи.

4. При необходимости добавьте текст, стикеры, музыку.

5. Нажмите Поделиться → выберите Моя история.""",
        "wa": """👆🏻 <b>Как выложить статус в WhatsApp</b>

1. Сохраните фото в Галерею.

2. Откройте WhatsApp → вкладка Статус.

3. Нажмите на значок камеры.

4. Выберите фото из Галереи.

5. При необходимости добавьте текст, смайлы или подпись.

6. Нажмите Отправить → статус станет доступен всем вашим контактам.""",
    },
    "post": {
        "tg": """<b>👆🏻 Как выложить пост в Telegram</b>

1. Перешлите пост в свой телеграм-канал.

2. <b>Не забудьте скрыть имя отправителя.</b>""",
        "ig": """👆🏻 <b>Как выложить пост в Instagram</b>

1. Сохраните фото в Галерею.

2. Откройте Instagram → нажмите (+) → Публикация.

3. Выберите фото из Галереи.

4. При необходимости добавьте фильтр или отредактируйте.

5. Напишите подпись, хэштеги и отметьте людей.

6. Нажмите Поделиться → пост появится в профиле.""",
    }
}


async def send_instructions(message: Message, obj: str, platform:str = "tg", need_replace: bool = False):
    instruction_text = instructions.get(obj, {}).get(platform, "")
    if not instruction_text:
        await message.answer("Инструкция не найдена.")
        logging.info(f"Инструкция не найдена для {obj} на {platform}")
        return
    
    if need_replace:
        await message.edit_text(
            instruction_text,
            reply_markup=kb.post_tips_tg(obj, platform)
        )
    else:
        await message.answer(
            instruction_text,
            reply_markup=kb.post_tips_tg(obj, platform)
        )

@router.callback_query(F.data.startswith("p_tip:"))
async def post_tip(call: CallbackQuery):
    place, obj, platform = call.data.split(":")
    await send_instructions(call.message, obj, platform, need_replace=True)

@router.callback_query(F.data == "current_tip")
@router.callback_query(F.data == "current_style")
async def current_var(call: CallbackQuery):
    await call.answer()

