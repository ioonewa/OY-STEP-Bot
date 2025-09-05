from aiogram import types
from aiogram.filters import BaseFilter

from loader import database

from Database.enums.user import UserStatus

import config

class RegFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        status = await database.get_user_status(message.from_user.id)
        return status != UserStatus.REGISTRATION
        
