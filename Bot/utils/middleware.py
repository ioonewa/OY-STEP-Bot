from loader import database

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


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
        
        user = await database.get_user(event.from_user.id)
        if not user:
            await event.answer("Для доступа к боту свяжитесь с разработчиками")
            return 


        return await handler(event, data)
        
