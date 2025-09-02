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

def post_vars_kb(post_id: str, vars: List[str], current_var: str) -> InlineKeyboardMarkup:
    kb_vars = []
    for var in vars:
        kb_vars.append(InlineKeyboardButton(
            text=f"☑️ {var}" if var == current_var else var,
            callback_data=f"var_{var}" if var != current_var else "current_var"
        ))

    kb = [
        kb_vars,
        [InlineKeyboardButton(text="Для Истории", callback_data=f"story:{post_id}:{current_var}")],
        [InlineKeyboardButton(text="Для Поста", callback_data=f"post:{post_id}:{current_var}")],
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