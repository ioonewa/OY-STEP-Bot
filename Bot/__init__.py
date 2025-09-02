from aiogram import Dispatcher
from .utils.middleware import AccessMiddleware

dispatcher = Dispatcher()

dispatcher.message.middleware(AccessMiddleware())

from .routers import routers

dispatcher.include_routers(*routers)