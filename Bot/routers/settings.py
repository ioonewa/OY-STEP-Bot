from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ..utils import keyboards as kb
from .registration import start_registration

from Database.enums.settings import (
    DeviceTypes
)

from loader import database

router = Router()

@router.callback_query(F.data == "reset_account")
async def reset_account(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "<b>Предупреждение</b>\n\n"
        "Сброс аккаунта запустит процесс регистрации заново. При этом ваша подписка на сервис сохранит свое действие\n\n"
        f"Если вам нужно изменить личные данные, вы можете это сделать в разделе \"{kb.PROFILE_BTN}\"",
        reply_markup=kb.approve_reset_kb()
    )

@router.callback_query(F.data == "set:switch_device")
async def switch_device(call: CallbackQuery):
    settings = await database.get_settings(call.from_user.id)

    if settings.device == DeviceTypes.IOS:
        device = DeviceTypes.ANDROID
    else:
        device = DeviceTypes.IOS

    await database.update_device(call.from_user.id, device)
    await call.message.edit_reply_markup(
        reply_markup=kb.settings_kb(
            device=device,
            notifications_status=settings.notifications_enabled
        )
    )

@router.callback_query(F.data == "set:switch_notif")
async def switch_notifications(call: CallbackQuery):
    settings = await database.get_settings(call.from_user.id)

    notifications_enabled = not settings.notifications_enabled
    await database.update_notifications(call.from_user.id, notifications_enabled)
    await call.message.edit_reply_markup(
        reply_markup=kb.settings_kb(
            device=settings.device,
            notifications_status=notifications_enabled
        )
    )

@router.callback_query(F.data == "approve_reset")
async def approve_reset(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await start_registration(call.message, state, call.from_user.id)