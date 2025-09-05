from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    InputMediaDocument
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command, CommandStart, CommandObject
from ..utils import keyboards as kb
from ..utils.get_content import get_personal_photo

from .interface import menu

from Database.enums.media_files import FileTypes

from loader import database

from typing import Optional

router = Router()

# https://t.me/oystep_bot?start=post1
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
    

@router.message(CommandStart(deep_link=True))
async def get_post_content(message: Message, command: CommandObject):
    post_id = command.args.replace("post", "")

    if not post_id.isdigit():
        await message.answer("Некорректная ссылка")
        await menu(message)
        return
    
    post_id = int(post_id)

    ids = await database.get_posts_id()
    if post_id in ids:
        await get_post_preview(message, post_id)
    else:
        await message.answer("Публикация не доступна")

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
    await call.message.answer("👆🏻\nТеперь перешли пост в свой телеграм-канал. <b>Незабудь скрыть имя отправителя</b>")
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
    await call.message.answer("""<b>Как выложить фотографии в Истории Telegram</b>

1. Откройте фото → нажмите ⋯ → Сохранить

2. Вверху главного экрана нажмите Моя история (+).

3. Выберите фото из Галереи

4. При необходимости отредактируйте.

5. Нажмите Опубликовать и выберите, кто увидит историю.""",
    )
    await call.answer()

@router.callback_query(F.data == "current_style")
async def current_var(call: CallbackQuery):
    await call.answer()

