from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from typing import List

import config

LESSONS_BTN = "Обучение"
TOURS_BTN = "Брокер-туры"
SETTINGS_BTN = "Настройки"
PROFILE_BTN = "Профиль"

CHANNEL_BTN = "Наши каналы"
FAQ_BTN = "Поддержка"


PIN_PHONE_BTN = "Прикрепить контакт"

BACK_BTN = "Назад"

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=TOURS_BTN),
                KeyboardButton(text=LESSONS_BTN),
            ],
            [
                KeyboardButton(text=PROFILE_BTN),
                KeyboardButton(text=SETTINGS_BTN)
            ],
            [
                KeyboardButton(text=CHANNEL_BTN),
                KeyboardButton(text=FAQ_BTN)
            ]
        ],
        resize_keyboard=True
    )

def post_styles_kb(
        post_id: str,
        styles: List[str],
        current: str
    ) -> InlineKeyboardMarkup:
    kb_styles = []
    for style in styles:
        kb_styles.append(InlineKeyboardButton(
            text="☑️" if style == current else style,
            callback_data=f"preview:{post_id}:{style}" if style != current else "current_style"
        ))

    file_ident = f"{post_id}:{current}"

    kb = [
        kb_styles,
        [InlineKeyboardButton(text="Для Истории", callback_data=f"story:{file_ident}")],
        [InlineKeyboardButton(text="Для Поста", callback_data=f"post:{file_ident}")],
        [InlineKeyboardButton(text="Видео", callback_data=f"video:{file_ident}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=BACK_BTN)]
        ]
    )

def pin_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=PIN_PHONE_BTN, request_contact=True)],
            [KeyboardButton(text=BACK_BTN)]
        ]
    )

def channels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔓 Приватный канал", url=config.INVITE_LINK)],
            [InlineKeyboardButton(text="Новостной канал", url=config.PUBLIC_CHANNEL)]
        ]
    )

def channel_invite_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔓 Приватный канал", url=config.INVITE_LINK)]
        ]
    )

def lessons_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1. Почему важен личный бренд", callback_data="lesson:1")],
            [InlineKeyboardButton(text="2. Как перестать бояться камеры", callback_data="lesson:2")],
            [InlineKeyboardButton(text="3. Как снимать стильно", callback_data="lesson:3")],
        ]
    )

def faq_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ionewa")]
    ])

def hide_content_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[InlineKeyboardButton(text="✖️ Скрыть", callback_data="hide_content")]
    )

def edit_profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_['btn'], callback_data=f"edit:{_['field']}")] for _ in config.FIELDS_TO_EDIT
        ]
    )