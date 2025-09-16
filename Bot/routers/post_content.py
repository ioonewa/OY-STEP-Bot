from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InputMediaPhoto,
    FSInputFile
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ChatAction
from ..utils import keyboards as kb
import os

from config import INSTRUCTIONS

from content_utils import get_personal_photo, append_photo_with_blink, add_music_segment

from Database.enums.media_files import FileTypes

from loader import database

from typing import Optional

import logging

router = Router()

# https://t.me/oystep_bot?start=
# https://t.me/oysteptest_bot?start=

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
    text= (
        "<b>Генерация контента.</b>\n\n"
        "\t1.\t\t\tВыберите понравившийся шаблон\n"
        "\t2.\t\t\tВыберите нужный формат\n"
        "\t2.\t\t\tОпубликуйте контент у себя в соцсетях\n"
        "🔥\t\t\t<b>Получите свежие лиды!</b>"
    )

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
    try:
        user_id = call.from_user.id
        obj, post_id, style  = call.data.split(":")
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
            obj=obj
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
    except Exception as ex:
        logging.error(f"Ошибка при получение формата {user_id} ({call.data}) - {ex}")
        await call.answer("Формат поста недоступен")

# Получение контента для Истории
@router.callback_query(F.data.startswith("story:"))
async def get_content_story(call: CallbackQuery):
    try:
        user_id = call.from_user.id
        obj, post_id, style  = call.data.split(":")
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
            obj=obj
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
    except Exception as ex:
        logging.error(f"Ошибка при получение формата {user_id} ({call.data}) - {ex}")
        await call.answer("Формат историй недоступен")

# Получение контента для Reels
@router.callback_query(F.data.startswith("video:"))
async def get_video(call: CallbackQuery):
    try:
        await call.message.answer("Подождите немного, генерация видео может занимать до 2х минут")
        user_id = call.from_user.id
        obj, post_id, style  = call.data.split(":")
        post_id = int(post_id)

        user_data = await database.get_user_data_dict(user_id)
        source_dir = f"videos/{user_id}"
        os.makedirs(source_dir,exist_ok=True)

        await get_personal_photo(
            user_data=user_data,
            style=style,
            telegram_id=user_id,
            post_id=post_id,
            obj="story"
        )

        await call.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_VIDEO)

        out_file = await append_photo_with_blink(
            photo_path=f"photos/{user_id}/{post_id}_story_{style}.png",
            video_path=f"content/templates/{post_id}/{style}/video.mp4",
            output_path=f"{source_dir}/{post_id}_{obj}_{style}.mp4",
            fade_duration=0.5
        )
        out_file = await add_music_segment(
            video_path=out_file,
            music_path=f"content/templates/{post_id}/{style}/music.mp3",
            output_path=f"{source_dir}/{post_id}_{obj}_{style}_final.mp4"
        )

        await call.message.answer_video(video=FSInputFile(path=out_file), protect_content=False)
        # Место для обучалки
        await send_instructions(call.message, obj)
        await call.answer()
    except Exception as ex:
        logging.error(f"Ошибка при получение формата {user_id} ({call.data}) - {ex}")
        await call.answer("Видео формат недоступен")


async def send_instructions(message: Message, obj: str, platform:str = "tg", need_replace: bool = False):
    instruction_text = INSTRUCTIONS.get(obj, {}).get(platform, "")
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

# Получение инструкции
@router.callback_query(F.data.startswith("p_tip:"))
async def post_tip(call: CallbackQuery):
    place, obj, platform = call.data.split(":")
    await send_instructions(call.message, obj, platform, need_replace=True)

@router.callback_query(F.data.in_(["current_style", "current_tip"]))
async def current_var(call: CallbackQuery):
    await call.answer()

