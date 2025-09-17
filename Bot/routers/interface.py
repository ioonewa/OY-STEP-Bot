from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo
)
from aiogram.enums import ChatAction
from aiogram.types.link_preview_options import LinkPreviewOptions

from loader import database, admin_bot
from Database.enums.user import UserStatus
from Database.enums.media_files import FileTypes

from .registration import start_registration, validate_phone
from ..utils import keyboards as kb
from ..utils.states import Edit
from ..utils.stash import stash_img
from ..utils.get_content import get_user_preview

from aiogram.filters import CommandObject
from typing import Optional

import config

import logging

router = Router()

async def get_post_preview(
        message: Message,
        post_id: int,
        style: Optional[str] = None,
        need_replace: bool = False
    ):

    styles = await database.get_post_styles(post_id)
    

    if not style:
        style = styles[0]

    preview = await database.get_content_files(
        post_id=post_id,
        style=style,
        file_type=FileTypes.STYLE_PREVIEW
    )

    preview = preview[0]

    reply_markup = reply_markup=kb.post_styles_kb(post_id, styles, style)
    text="Выберите шаблон для генерации публикации/истории"

    if not need_replace:
        await message.answer_photo(
            photo=preview,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await message.edit_media(
            media=InputMediaPhoto(media=preview, caption=text),
            reply_markup=kb.post_styles_kb(post_id, styles, style)
        )

# @router.message(F.text == kb.CONTENT_PLAN_BTN)
# async def content_plan(message: Message):
#     await message.answer("<b>Контент-план</b>\n", reply_markup=kb.content_plan_kb())

@router.message(Edit.name, F.text == kb.BACK_BTN)
@router.message(Edit.email, F.text == kb.BACK_BTN)
@router.message(Edit.phone_number, F.text == kb.BACK_BTN)
@router.message(Edit.photo, F.text == kb.BACK_BTN)
@router.message(Edit.approve_photo, F.text == kb.BACK_BTN)
async def cancel_edit(message: Message, state: FSMContext):
    await state.clear()
    await profile(message)

@router.message(Edit.name, F.text)
async def edit_name(message: Message, state: FSMContext):
    name = message.text

    if len(name) > config.NAME_LIMIT:
        await message.reply(f"Имя слишко длинное, максимальное кол-во символов - {config.NAME_LIMIT}")
        return

    await database.execute(
        'UPDATE users SET name = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        name, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(Edit.email, F.text)
async def edit_email(message: Message, state: FSMContext):
    email = message.text

    if len(email) > config.NAME_LIMIT:
        await message.reply(f"Имя слишко длинное, максимальное кол-во символов - {config.NAME_LIMIT}")
        return

    await database.execute(
        'UPDATE users SET email = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        email, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(Edit.phone_number, F.text)
async def edit_phone_number(message: Message, state: FSMContext):
    phone_number = message.text

    phone_number = validate_phone(phone_number)
    if not phone_number:
        await message.reply("Некорректный номер")
        return

    await database.execute(
        'UPDATE users SET phone_number = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        phone_number, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(F.contact, Edit.phone_number)
async def edit_phone_number_contact(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.reply("Можно отправлять только свой контакт")
        return
    
    phone_number = validate_phone(contact.phone_number)
    if not phone_number:
        await message.reply("Некорректный номер")
        return
    
    await database.execute(
        'UPDATE users SET phone_number = $1, updated_at = current_timestamp WHERE telegram_id = $2',
        phone_number, message.from_user.id
    )
    await state.clear()
    await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
    await profile(message)

@router.message(F.photo | F.document, Edit.photo)
async def edit_photo(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    save_dir = f"photos/{tg_id}"
    file_path = f"{save_dir}/photo.png"

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=file_path)


    await state.update_data(photo_source=file_path)

    preview_photo = get_user_preview(file_path)
    
    await message.answer_photo(
        photo=FSInputFile(path=preview_photo),
        caption="<b>Убедитесь, что ваше лицо находится в рамке.</b>\n\n"
        "В наших шаблонах мы будем размещать вашу фотографию, немного обрезая ее. Вы всегда сможете поменять фотографию в Профиле.",
        reply_markup=kb.approve_photo_kb()
    )
    await state.set_state(Edit.approve_photo)

@router.message(Edit.approve_photo, F.text == kb.CHANGE_PHOTO_BTN)    
@router.message(Edit.approve_photo, F.text == kb.APPROVE_PHOTO_BTN)
async def approve_photo(message: Message, state: FSMContext):
    btn = message.text
    if btn == kb.APPROVE_PHOTO_BTN:
        state_data = await state.get_data()
        tg_photo_id = await stash_img(state_data["photo_source"])
        await database.execute(
            'UPDATE users SET photo_tg = $1, updated_at = current_timestamp WHERE telegram_id = $2',
            tg_photo_id, message.from_user.id
        )
        await state.clear()
        await message.answer("Изменения сохранены", reply_markup=kb.menu_kb())
        await profile(message)
    else:
        await message.answer(
            text="<b>Прикрепите вашу Фотографию</b>",
            reply_markup=kb.back_kb()
        )
        await state.set_state(Edit.photo)

@router.message(Edit.approve_photo)
async def approve_photo_wrong(message: Message):
    await message.answer(text="Воспользуйтесь кнопками", reply_markup=kb.approve_photo_kb())

@router.message(Edit.name)
@router.message(Edit.email)
@router.message(Edit.phone_number)
@router.message(Edit.photo)
async def wrong_input(message: Message):
    await message.answer("Недопустимый формат ввода", reply_markup=kb.back_kb())

@router.message(CommandStart(deep_link=True))
async def get_post_content_cb(message: Message, state: FSMContext, command: CommandObject):
    payload = command.args
    user = message.from_user

    if payload.isdigit():
        post_id = command.args

        if not post_id.isdigit():
            await message.answer("Некорректная ссылка")
            await menu(message)
            return
        
        post_id = int(post_id)

        ids = await database.get_posts_id()
        if post_id in ids:
            await get_post_preview(message, post_id)
        else:
            await message.answer("Публикация не доступна")
        return
    else:
        creator_id = await database.use_invite_link(payload, user.id)
        if creator_id:
            logging.info(f"Пользователь {user.id} добавлен в бота по ссылку от {creator_id}")
            await message.answer(f"<b>Вы были добавлены в фокус группу для Тестирования!</b>")
            await database.add_user(user.id, user.username, UserStatus.REGISTRATION)
            await start_registration(message, state, user.id)
            try:
                await admin_bot.send_message(creator_id, f"✅ Пользователь @{user.username} ({user.id}) получил доступ к боту.")
            except Exception as ex:
                logging.error(f"Не получилось отправить сообщение для ({creator_id}) об активации доступа - {ex}")
        else:
            await database.add_user(user.id, user.username, UserStatus.WAITING_LIST)
            await message.answer("<b>Вы добавлены в лист ожидания.</b>\n\nСейчас Бот находится в разработке. Мы добавили вас в лист ожидания — вы получите уведомление, когда Бот будет запущен.")

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = message.from_user
    status = await database.get_user_status(user.id)

    if not status or status == UserStatus.WAITING_LIST:
        await database.add_user(user.id, user.username, UserStatus.WAITING_LIST)
        await message.answer("<b>Вы добавлены в лист ожидания.</b>\n\nСейчас Бот находится в разработке. Мы добавили вас в лист ожидания — вы получите уведомление, когда Бот будет запущен.")
        return
    
    if status == UserStatus.INVITED:
        await message.answer("<b>Вы были добавлены в фокус группу для Тестирования!</b>")
        # Начать регистрацию
        await start_registration(message, state, user.id)
    else:
        # Вызвать меню
        await menu(message)

async def menu(message: Message):
    await message.answer(
        "<b>OYBOT</b> - это простой и удобный бот для брокеров.\n\n"
        "<b>Бот позволяет:</b>\n\n"
        "— Создавать персональный контент\n\n"
        "— Смотреть календарь брокеров-туров\n\n"
        "— Получать новые скиллы (раздел \"Обучение\")",
        reply_markup=kb.menu_kb()
    )

@router.message(F.text == kb.LESSONS_BTN)
async def lessons(message: Message):
    await message.answer(
        "<b>Вам доступно 3 видео-урока.</b>\n\n"
        "1. Почему важен личный бренд? | 1:39\n\n"
        "2. Как перестать бояться камеры? | 1:51\n\n"
        "3. Как снимать стильно? | 2:08",
        reply_markup=kb.lessons_kb()
    )

@router.callback_query(F.data == "lessons")
async def lessons(call: CallbackQuery):
    await call.message.edit_text(
        text="<b>Вам доступно 3 видео-урока.</b>\n\n"
        "1. Почему важен личный бренд? | 1:39\n\n"
        "2. Как перестать бояться камеры? | 1:51\n\n"
        "3. Как снимать стильно? | 2:08",
        reply_markup=kb.lessons_kb()
    )

settings_text = (
    "<b>Настройки.</b>\n\n"
    "<b>Устройство:</b> Нам важно знать, какое у вас мобильное устройство, чтобы создать для вас комфортный интерфейс.\n\n"
    "<b>Уведомления:</b> Мы напоминаем вам об \"окнах\", в которых вы сможет получить самый большой охват.\n\n"
    "<i>Можно сбросить аккаунт, чтобы пройти регистрацию заново. Подписка никуда не пропадет — после повторного прохождения регистраци, доступ будет открыт.</i>"
)

@router.message(F.text == kb.SETTINGS_BTN)
async def settings(message: Message):
    settings = await database.get_settings(message.from_user.id)
    await message.answer(
        settings_text,
        reply_markup=kb.settings_kb(settings.device, settings.notifications_enabled)
    )

@router.callback_query(F.data == "back_to:settings")
async def settings_cb(call: CallbackQuery):
    settings = await database.get_settings(call.from_user.id)
    await call.message.edit_text(
        settings_text,
        reply_markup=kb.settings_kb(settings.device, settings.notifications_enabled)
    )

@router.message(F.text == kb.TOURS_BTN)
async def tours(message: Message):
    await message.answer(
        """<b>Брокер-туры сентябрь 2025</b>

<b>🔥 В ближайшее время</b>
18.09 | 10:00 <a href="https://t.me/TrendAgent_Education_bot?start=_W2t_RfIlDm9y4cPgvivt">Автобусный тур ГК ФСК</a>
18.09 | 10:15 <a href="https://t.me/TrendAgent_Education_bot?start=vMVCNM05ZWhyDwD2JnkIS">Автобусная экскурсия INGRAD</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=AmavlpQh26lhS7lkiN3DN">3SGroup ЖК «Voice Towers»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=IbZM1oWOc54b4fFe--gT9">ЖК «Бархат»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=59w3cC0fX7ZvjwKEUAes8">РКС Девелопмент ЖК «Insider»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=d8IF7TXfj3kwVPbvtr65Z">Талан ЖК «Injoy»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=SQvW3uUOyGV3Taym0BNrj">Среда Все ЖК</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=5k3m1yMjVUkESS7PaVfOw">СЗ Сияние ЖК «Клубный Квартал 33»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=hLX_r3C51CiZBC1nySSiQ">AFI Development ЖК «AFI PARK Воронцовский»</a>
18.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=OJT8OhEz0pWvblbmqwGml">Коммерческая недвижимость DOGMA «Публицист и EVO»</a>
18.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=ZqsJs9ABZUt8YL1q34c4z">ГК Град ЖК «Домодедово парк»</a>
18.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=DUX2EGhgRqL2jVsxsDojj">Страна.Девелопмент ЖК «Страна.Озерная»</a>
19.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=_8NZ8QLdIIhclYg8_ssLm">Брусника ЖК «Издание»</a>
19.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=QGiOhJH5O5CRb3vR8WPSZ">Кортрос ЖК «ILOVE»</a>
19.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=0BS93LJOP2ZO2qvH5arQd">ГК Родина ЖК «Родина Переделкино»</a>
19.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=NclhFSB_fiQcXwDEaIJiz">ЭЛИТА-ЭКО Клубный дом D'ORO MILLE</a>
19.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=DCGoHI6qFnXNxBu7wdsqo">TOUCH ЖК «Champine»</a>

<b>22 Сентября</b>
22.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=fJn7F-W8RaCslbLjK_qy4">УПК РОСТ ЖК «Новое Летово»</a>

<b>23 Сентября</b>
23.09 | 10:00 <a href="https://t.me/TrendAgent_Education_bot?start=0PGdJHi2_Sk_dxencG23x">ГК Эталон Проекты застройщика</a>
23.09 | 10:30 <a href="https://t.me/TrendAgent_Education_bot?start=SqtlQwjWQMnbKEmIWvl7X">КСТ ЖК «Riga Holiday»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=55oVzQYXZRH_shUzYzJip">Unikey ЖК «Новые смыслы»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=lmFsePqfNeZ8eaBwfVVsz">Sezar Group ЖК «Sezar City»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=2F3a4BdgxZIbl7q-gjDwl">DAR ЖК «Rakurs»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=4x8MylfDUB9HhLOJcCdMC">FORMA ЖК «Portland»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=dzmW2oU3yL7-VaOwprT2K">Талан ЖК «INJOY»</a>
23.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=Ek8v4vzD4m-NYJeAWcxOS">Capital Alliance Бизнес-центр «Avium»</a>
23.09 | 11:30 <a href="https://t.me/TrendAgent_Education_bot?start=gYxolPZeV0viYON1d5GlZ">СЗ Горакс ЖК «Smart Garden» в Новой Москве</a>
23.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=R5DYdSY1AYFo7FMQHZvDo">ГК Сумма Элементов ЖК «Дом Дау»</a>
23.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=UU58bSXidbOgg8mGwjm33">TOUCH ЖК «Дом Горизонтов»</a>

<b>24 Сентября</b>
24.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=W32Go19tmqfM73iGxJxru">LEGENDA ЖК «Северный Порт». Путь Клиента</a>
24.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=0T_OytxFyEhouo8We9Ush">Plus Development ЖК «Акценты»</a>
24.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=QZmDfvqKqzFa_KjuWNL4A">Upside Development ЖК «Данилов Дом»</a>
24.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=X2WTpv9OLZBhObXdcWOY9">Офисная и торговая недвижимость FORMA</a>
24.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=DCPJSlcOHwVdYLyWwJgDD">Plato ЖК «Кутузов Сити»</a>
24.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=f775Qb6iTNXLwnFmOADSn">СЗ Сияние ЖК «Клубный Квартал 33»</a>
24.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=PSeiI-tmZX7P6FYvPQRJT">Кортрос ЖК «Ultima City»</a>

<b>25 Сентября</b>
25.09 | 10:00 <a href="https://t.me/TrendAgent_Education_bot?start=PS80O7b9mQ6pCUwmTWB1N">ГК Эталон Проекты застройщика</a>
25.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=_HgSh-JiYGLpeIP9Jom0p">Талан ЖК «Injoy»</a>
25.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=t-zQdB0wBOoMBG0WrvtD_">Sezar Group ЖК «Рассказово»</a>
25.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=0Hz8eoQ1OQHCfJHwjXcZu">РКС Девелопмент ЖК «Insider»</a>
25.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=G9Vc2f6AFOiqFc6cZ4TYM">AFI Development ЖК «Резиденция архитекторов»</a>
25.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=pRjyW6wX99wXb_Il3jDmk">Страна.Девелопмент ЖК «Republic»</a>

<b>26 Сентября</b>
26.09 | 10:50 <a href="https://t.me/TrendAgent_Education_bot?start=lxELjFhQMNwnqBTxSFTxA">Автобусная экскурсия Донстрой</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=2bXL1S3xHxjCSUgHNZaYm">ГК Родина ЖК «СОЮЗ»</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=5WpuXgBfSoItYxAMUDu4F">Unicom Development КП «Резиденция Булатово»</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=J5hUhklL8R5m8VCI7d6Kv">October Group ЖК «King&Sons»</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=G2zHP_YY7DImkKgI5dW0d">Торговая недвижимость ГК А101</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=HLnv9f_c9bUHpSIO46NF9">Мангазея ЖК «Мангазея на Речном»</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=LmQ0Bh6M2Ze8Ro4hW_UD_">Брусника ЖК «Первый квартал»</a>
26.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=oZ_nFdZW2IPV8CLGS1yBG">GloraX. Москва ЖК «GloraX Premium Белорусская»</a>

<b>29 Сентября</b>
29.09 | 10:00 <a href="https://t.me/TrendAgent_Education_bot?start=4K7mW0raB8hYqBW4NmHFw">Экскурсия Realt.One</a>

<b>30 Сентября</b>
30.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=adiwVAQy5FSVbvWMmXJgE">Sezar Group ЖК «Full House»</a>
30.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=qrM4AyGwEfcODKW8mSt4D">DAR ЖК «Solos»</a>
30.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=YE0-CdtuVv3BeREjEq161">Capital Alliance Бизнес-центр «Avium»</a>
30.09 | 11:00 <a href="https://t.me/TrendAgent_Education_bot?start=rPJYosqKy-EMqAbKAA9PI">FORMA ЖК «Moments»</a>
30.09 | 12:00 <a href="https://t.me/TrendAgent_Education_bot?start=cvbBzLsR26xCQG8Rizrvj">ST Michael ЖК «Квартал Серебряный Бор» + ЖК «Зорге 9»</a>""",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@router.message(F.text == kb.CHANNEL_BTN)
async def channel(message: Message):
    await message.answer(
        "<b>Вам доступно 3 чата.</b>",
        reply_markup=kb.channels_kb()
    )

@router.message(F.text == kb.FAQ_BTN)
async def faq(message: Message):
    await message.answer(
        """<b>Часто задаваемые вопросы</b>
        
<b>Как работает этот бот</b>
- Бот обрабатывает ваши запросы и выдает быстрый результат автоматически.

<b>Сколько стоит использование бота?</b>
- Цена зависит от выбранного тарифа.

<b>Что делать, если бот не отвечает?</b>
- Нужно перезапустить чат или повторить запрос через несколько минут.

<b>Можно ли пользоваться ботом с телефона и компьютера?</b>
- Да, бот доступен в Telegram на любых устройствах.

<b>К кому обращаться при проблемах?</b>
- Наша поддержка всегда рада помочь!""",
        reply_markup=kb.faq_kb()
    )


@router.message(F.text == kb.SETTINGS_BTN)
async def development(message: Message):
    await message.reply("Данный раздел в разработке")
    
lessons_files = {
    "1": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/2",
        "name": "1. Почему личный бренд важен?"
    },
    "2": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/3",
        "name": "2. Как перестать бояться камеры?"
    },
    "3": {
        "url": "https://t.me/POLPUGA7BC0MZZOVBC57/5",
        "name": "3. Как снимать стильно?"
    } 
}

@router.message(F.text == kb.PROFILE_BTN)
async def profile(message: Message):
    user_data = await database.get_user_data_dict(message.from_user.id)
    await message.answer_photo(
        photo=user_data['photo_tg'],
        caption=f"<b>{user_data['name']}</b>\n\n"
        f"https://t.me/{user_data['username']}\n"
        f"{user_data['phone_number']}\n"
        f"{user_data['email']}\n\n"
        "Чтобы редактировать профиль, воспользуйтесь кнопками\n"
        "👇🏻",
        reply_markup=kb.edit_profile_kb()
    )

@router.callback_query(F.data.startswith("edit:"))
async def edit_profile(call: CallbackQuery, state: FSMContext):
    field = call.data.replace("edit:", "")
    
    reply_markup = kb.back_kb()

    if field == "name":
        text = "<b>Напишите свое Имя и Фамилию (в одном сообщение)</b>"
        state_name = Edit.name
    elif field == "phone_number":
        text = "<b>Напишите ваш Номер телефона (в формате +7...)</b>"
        state_name = Edit.phone_number
        reply_markup = kb.pin_phone_kb()
    elif field == "photo":
        text = "<b>Прикрепите вашу Фотографию</b>"
        state_name = Edit.photo
    elif field == "email":
        text = "<b>Напишите ваш Email</b>"
        state_name = Edit.email
    
    await call.message.answer(text, reply_markup=reply_markup)
    await state.set_state(state_name)

    await call.message.edit_reply_markup()

@router.callback_query(F.data.startswith("lesson:"))
async def lesson_id(call: CallbackQuery):
    lesson_id = call.data.replace("lesson:", "")

    lesson = lessons_files.get(lesson_id)
    if not lesson:
        await call.answer("Видео-урок недоступен")
        return

    await call.message.edit_media(
        media=InputMediaVideo(
            media=lesson['url'],
            caption=lesson['name']
        ),
        reply_markup=kb.lesson_kb(lesson_id)
    )


@router.callback_query()
async def development(call: CallbackQuery):
    await call.answer(f"В разработке")