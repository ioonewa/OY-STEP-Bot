from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command, CommandStart, CommandObject
from ..utils import keyboards as kb
from ..utils.get_content import get_personal_photo

from loader import database

from typing import Optional

router = Router()

# https://t.me/oystep_bot?start=post1

test_previews = {
    "Red": "AgACAgIAAxkDAAMGaLS5J16_Yl0uXcS0SdPLf981HJ0AAm74MRvcpKhJOpH35U87vbABAAMCAAN5AAM2BA",
    "Blue": "AgACAgIAAxkDAAMHaLS5J0aN3fn3yEelquuNAa0do38AAm_4MRvcpKhJXVFVGtHleXgBAAMCAAN5AAM2BA",
    "Black": "AgACAgIAAxkDAAMFaLS5JpsovacRie3A6wq2lJggBKgAAm34MRvcpKhJ18zUH54Eh_8BAAMCAAN5AAM2BA"
}

async def get_post_vars(message: Message, number: str, current_var: Optional[str] = None, need_replace: bool = False):
    if not current_var:
        current_var = list(test_previews.keys())[0]
    
    photo = test_previews[current_var]
    
    if not need_replace:
        await message.answer_photo(
            photo=photo,
            caption="Выберите шаблон для генерации публикации/истории",
            reply_markup=kb.post_vars_kb(number, list(test_previews.keys()), current_var)
        )
    else:
        await message.edit_media(
            media=InputMediaPhoto(media=photo, caption="Выберите шаблон для генерации публикации/истории"),
            reply_markup=kb.post_vars_kb(number, list(test_previews.keys()), current_var)
        )
    

@router.message(CommandStart(deep_link=True))
async def get_post_content(message: Message, command: CommandObject):
    post = command.args.replace("post", "")
    if post == "1":
        await get_post_vars(message, post)
    else:
        await message.answer(f"Привет! Кажется, ты тут случайно...")

@router.callback_query(F.data.startswith("var_"))
async def change_vars(call: CallbackQuery):
    current_var = call.data.replace("var_", "")
    await get_post_vars(call.message, "test", current_var, need_replace=True)

styles_rules = {
    "Red": {
        "top": 109,
        "left": 196,
        "rect_width": 605,
        "rect_height": 600,
        "angle": 5,
        "frame_path": "frame_red.png",
        "photo_path": "photo.png",
        "textes": {
            "username": {
                "text_top_offset": 804,
                "text_left_offset": 90,
                "font_size": 86,
                "font_path": "TT Interphases Pro Mono Trial Bold.ttf",
                "font_color": (0,0,0,255)
            }
        }
    }
}

@router.callback_query(F.data.startswith("post:"))
async def get_post_content(call: CallbackQuery):
    user_id = call.from_user.id
    place, post_id, style  = call.data.split(":")
    # post_id = int(post_id)
    post_id = 1

    files = await database.get_post_files(post_id, style)

    user_data = await database.get_user_data_dict(user_id)
    if not user_data:
        await call.message.answer("Сначала пройдите регистрацию")
        return
    
    personal_photo_id = await get_personal_photo(
        user_id,
        user_data,
        post_id,
        style
    )

    files.append(personal_photo_id)

    captions = {
        "Black": """<b>Жилой комплекс</b> бизнес-класса <b>Stone Rise</b> всего в нескольких минутах от метро <b>Римская</b> и <b>Площадь Ильича</b>.

Проект включает <b>три корпуса</b> разной этажности (до 28 этажей), выполненных в  минималистичном дизайне с сочетанием серого и изумрудного оттенков. Выразительный экстерьер и панорамное остекление создают архитектурную доминанту района.

<b>88 уникальных планировок</b> — от компактных студий с балконами до просторных квартир с мастер-спальнями, окнами в ванной и даже двухуровневых решений. Террасы и балконы доступны в почти 20 % квартир.

<b>Инфраструктура</b>: гранд-лобби с кофе-зоной и ресепшен, семейные и коворкинг-зоны, общественные террасы, детские площадки, лапомойки и кладовые. Территория закрытая, с подземным паркингом

<blockquote>Акция от застройщика: - 3% от общей стоимости</blockquote>""",
        "Blue": "<b>ЖК Joice</b> — комфорт, стиль и современные решения в одном проекте. Узнайте больше и найдите свой идеальный дом",
        "Red": """<b>Клубный дом класса de luxe в Хамовниках</b> — это камерный проект на 72 квартиры, где классическая архитектура встречается с современным комфортом. 

Пространство <b>продумано до мелочей</b>: панорамные окна, террасы, wellness-зона, приватный сад с арт-объектами и подземный паркинг. 

Уют, статус и высокий уровень сервиса для тех, кто ценит эстетику и тишину в самом сердце Москвы."""
    }

    media_group = MediaGroupBuilder(
        caption=captions.get(style) + f"\n\nНапиши мне, и я помогу выбрать лучшую квартиру: @{user_data['username']}",
        media=[
            InputMediaPhoto(media=file) for file in files
        ]
    )

    await call.message.answer_media_group(media=media_group.build(), protect_content=False)
    await call.message.answer(
        "👆🏻\nТеперь перешли пост в свой телеграм-канал. <b>Незабудь скрыть имя отправителя</b>"
    )
    await call.answer()

@router.callback_query(F.data == "current_var")
async def current_var(call: CallbackQuery):
    await call.answer()

