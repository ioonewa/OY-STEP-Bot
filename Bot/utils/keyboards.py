from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from typing import List, Optional, Literal

from Database.enums.settings import DeviceTypes

import config

LESSONS_BTN = "Обучение"
TOURS_BTN = "Брокер-туры"
SETTINGS_BTN = "Настройки"
PROFILE_BTN = "Профиль"

CONTENT_PLAN_BTN = "⭐️ Контент-план"

CHANNEL_BTN = "Чаты"
FAQ_BTN = "Поддержка"

PHONE_IOS = "Устройство: IOS"
PHONE_ANDROID = "Устройство: Android"
NOTIFICATIONS_ON = "🔔 Уведомления"
NOTIFICATIONS_OFF = "🔕 Уведомления"

PIN_PHONE_BTN = "Прикрепить контакт"

APPROVE_PHOTO_BTN = "Продолжить"
CHANGE_PHOTO_BTN = "Заменить фото"

BACK_BTN = "Назад"

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=CONTENT_PLAN_BTN)
            ],
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
        [InlineKeyboardButton(text="История", callback_data=f"story:{file_ident}")],
        [InlineKeyboardButton(text="Пост", callback_data=f"post:{file_ident}")],
        [InlineKeyboardButton(text="Видео", callback_data=f"video:{file_ident}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)

def reg_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я согласен с политикой конфиденциальности", callback_data="reg:agree")]
    ])

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
            [InlineKeyboardButton(text="🔓 Закрытый канал", url=config.INVITE_LINK)],
            [InlineKeyboardButton(text="🔓 Группа с обсуждениями", url=config.PRIVATE_GROUP_LINK)],
            [InlineKeyboardButton(text="Новостной канал", url=config.PUBLIC_CHANNEL)]
        ]
    )

def channel_invite_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔓 Закрытый канал", url=config.INVITE_LINK)],
            [InlineKeyboardButton(text="🔓 Группа с обсуждениями", url=config.PRIVATE_GROUP_LINK)],
        ]
    )

def studying_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Советы", callback_data="studying:tips")],
            [InlineKeyboardButton(text="Видео-уроки", callback_data="studying:lessons")]
        ]
    )

def lessons_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1. Почему важен личный бренд", callback_data="lesson:1")],
            [InlineKeyboardButton(text="2. Как перестать бояться камеры", callback_data="lesson:2")],
            [InlineKeyboardButton(text="3. Как снимать стильно?", callback_data="lesson:3")],
        ]
    )

def lesson_kb(current_lesson: str) -> InlineKeyboardMarkup:
    lessons = {
        "1": "1. Почему важен личный бренд",
        "2": "2. Как перестать бояться камеры",
        "3": "3. Как снимать стильно?"
    }

    kb = []
    if current_lesson == "1":
        kb = [InlineKeyboardButton(text="Следующий ➡️", callback_data="lesson:2")]
    elif current_lesson == "2":
        kb = [
            InlineKeyboardButton(text="⬅️", callback_data="lesson:1"),
            InlineKeyboardButton(text="➡️", callback_data="lesson:3")
        ]
    elif current_lesson == "3":
        kb = [InlineKeyboardButton(text="⬅️ Предыдущий", callback_data="lesson:2")]
    return InlineKeyboardMarkup(inline_keyboard=[
        kb
        # [InlineKeyboardButton(text="Весь список", callback_data="lessons")]
    ])


def faq_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать в поддержку", url=config.SUPPORT_LINK)]
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

def settings_kb(
    device: Optional[str] = DeviceTypes.IOS,
    notifications_status: bool = True
) -> InlineKeyboardMarkup:
    if device is None:
        device = DeviceTypes.IOS

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=PHONE_IOS if device == DeviceTypes.IOS else PHONE_ANDROID, callback_data="set:switch_device")],
            [InlineKeyboardButton(text=NOTIFICATIONS_ON if notifications_status else NOTIFICATIONS_OFF, callback_data="set:switch_notif")],
            [InlineKeyboardButton(text="Документы", callback_data="show_docs")],
            [InlineKeyboardButton(text="Сбросить аккаунт", callback_data="reset_account")]
        ]
    )

def approve_reset_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сбросить аккаунт", callback_data="approve_reset")],
        [InlineKeyboardButton(text="Отмена", callback_data="back_to:settings")]
    ])

def approve_photo_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=APPROVE_PHOTO_BTN)],
            [KeyboardButton(text=CHANGE_PHOTO_BTN)]
        ]
    )

INSTAGRAM_BTN = "Instagram"
TELEGRAM_BTN = "Telegram"
WHATSAPP_BTN = "WhatsApp"

def post_tips_tg(
    obj: str,
    current_platform: str
) -> InlineKeyboardMarkup:
    kb = []
    tg_btn, tg_cb = ("☑️", "current_tip") if current_platform=="tg" else (TELEGRAM_BTN, f"p_tip:{obj}:tg")
    kb.append(InlineKeyboardButton(text=tg_btn, callback_data=tg_cb))
    inst_btn, inst_cb = ("☑️", "current_tip") if current_platform=="ig" else (INSTAGRAM_BTN, f"p_tip:{obj}:ig")
    kb.append(InlineKeyboardButton(text=inst_btn, callback_data=inst_cb))
    if obj == "story":
        wa_btn, wa_cb = ("☑️", "current_tip") if current_platform=="wa" else (WHATSAPP_BTN, f"p_tip:{obj}:wa")
        kb.append(InlineKeyboardButton(text=wa_btn, callback_data=wa_cb))

    return InlineKeyboardMarkup(inline_keyboard=[kb])

cp_modes = [
    "Захват рынка",
    "Умеренный",
    "💤 Выкл"
]

cp_time = [
    "Утро",
    "Вечер",
    "Универсальный"
]

def content_plan_kb(
    need_platforms: bool = False,
    on_edit: bool = False 
) -> InlineKeyboardMarkup:
    inline_keyboard=[
        [InlineKeyboardButton(text="Захват рынка", callback_data=f"сp_mode")],
        [InlineKeyboardButton(text="Утро", callback_data=f"cp_time")]
    ]

    if need_platforms:
        for plat in ["wa", "ig", "tg"]:
            inline_keyboard.append([
                InlineKeyboardButton(text=f"{config.PLATFORMS_MAP.get(plat)}", callback_data=f"cp_plat:{plat}")
            ])
    else:
        inline_keyboard.append([[InlineKeyboardButton(text="Выбрать соцсети", callback_data=f"cp_platforms")]])

    if on_edit:
        inline_keyboard.append([InlineKeyboardButton(text="Сохранить", callback_data=f"cp_save")])
        inline_keyboard.append([InlineKeyboardButton(text="Отменить", callback_data=f"cp_cancel")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)    