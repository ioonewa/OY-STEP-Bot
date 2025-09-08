from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    phone_number = State()
    email = State()
    photo = State()
    approve_photo = State()
    
class Edit(StatesGroup):
    name = State()
    phone_number = State()
    email = State()
    photo = State()
    approve_photo = State()