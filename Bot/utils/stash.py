from loader import bot
from config import STASH_GROUP

from aiogram.types import FSInputFile

from typing import Optional

import logging

logger = logging.getLogger(__name__)

async def stash_video(path: str) -> str:
    message = await bot.send_video(
        chat_id=STASH_GROUP,
        video=FSInputFile(path)
    )

    file_id = message.video.file_id

    await message.edit_caption(caption=f"<code>{file_id}</code>")

    return file_id

async def stash_img(path: str) -> Optional[str]:
    try:
        message = await bot.send_photo(
            chat_id=STASH_GROUP,
            photo=FSInputFile(path)
        )

        file_id = message.photo[-1].file_id

        await message.edit_caption(caption=f"<code>{file_id}</code>")
        logger.info(f"Фотография ({path}) сохранена - {file_id}")
        return file_id
    except Exception as ex:
        logger.error(f"Не получилось сохранить фотографию ({path}) - {ex}")
        return None
    
async def stash_file(path: str) -> Optional[str]:
    try:
        message = await bot.send_document(
            chat_id=STASH_GROUP,
            document=FSInputFile(path)
        )

        file_id = message.document.file_id

        await message.edit_caption(caption=f"<code>{file_id}</code>")
        logger.info(f"Фотография ({path}) сохранена - {file_id}")
        return file_id
    except Exception as ex:
        logger.error(f"Не получилось сохранить фотографию ({path}) - {ex}")
        return None