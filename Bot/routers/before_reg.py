from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("info"))
async def payment_data(message: Message):
    await message.answer(
        "<b>OYSTEP | Офис брокера.</b>\n\n"
        "<b>Наши услуги и цены:</b>\n\n"
        "⭐️ Подписка Стандарт — 5000 ₽/мес\n\n"
        """<b>Данные о компании:</b>
<i>ИП Мудрак Максим Владимирович
ИНН 230603988280
ОГРН 325237500344922
Тел: +79998200319
Адрес:  350067, Краснодарский край, Краснодар, ул. Гаражная, 79/1, кв. 45</i>"""
    )