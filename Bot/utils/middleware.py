from loader import database

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from Database.enums.user import UserStatus


class AccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        
        if not event.from_user.username:
            await event.answer("Для доступа к боту вам нужно добавить username для своего аккаунта Telegram, сделать это можно в настройках")
            return
        
        # пропускаем команду /start (включая /start <код>)
        if event.text and (event.text.startswith("/start") or event.text == "/info"):
            return await handler(event, data)
        
        user = await database.get_user(event.from_user.id)
        if not user or user['status'] == UserStatus.WAITING_LIST:
            await database.add_user(event.from_user.id, event.from_user.username, UserStatus.WAITING_LIST)
            await event.answer("<b>Вы добавлены в лист ожидания.</b>\n\nСейчас Бот находится в разработке. Мы добавили вас в лист ожидания — вы получите уведомление, когда Бот будет запущен.")
            return

        return await handler(event, data)
        
