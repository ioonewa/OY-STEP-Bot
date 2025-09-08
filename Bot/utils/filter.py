from aiogram import types
from aiogram.filters import BaseFilter

from loader import database

from Database.enums.user import UserStatus

import config

class RegFilter(BaseFilter):
    async def __call__(self, event: types.Message | types.CallbackQuery) -> bool:
        status = await database.get_user_status(event.from_user.id)
        return status != UserStatus.REGISTRATION
        
