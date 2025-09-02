from loader import database

from Database.enums.user import UserStatus
from Database.enums.media_files import FileTypes

from Bot.utils.stash import stash_img

from asyncio import sleep

users = [
    {
        "username": "ionewa",
        "telegram_id": 752021281,
        "status": UserStatus.INVITED
    },
    {
        "username": "Vitestate",
        "telegram_id": 133353194,
        "status": UserStatus.INVITED
    }
    ,
    {
        "username": "Sameliya",
        "telegram_id": 264976221,
        "status": UserStatus.INVITED
    }
    ,
    {
        "username": "negakaif",
        "telegram_id": 128562688,
        "status": UserStatus.INVITED
    }
    ,
    {
        "username": "@eremichew",
        "telegram_id": 316341973,
        "status": UserStatus.INVITED
    }
]

async def main():
    await database.connect()
    await database.drop_tables()
    await database.create_tables()

    for user in users:
        await database.add_user(**user)

    styles = [
            "Black",
            "Red",
            "Blue"
        ]

    post_id = await database.add_post(
        name="Тестовый первый пост",
        styles=styles
    )

    for style in styles:
        for i in "123456":
            if style == "Blue" and i == "6":
                continue

            path = f"content/templates/1/{style}/post/{i}.png"
            file_id = await stash_img(path)
            await database.add_media_file(
                post_id=post_id,
                style=style,
                file_name=f"{style}/{i}.png",
                description="Часть шаблона",
                source_path=path,
                telegram_file_id=file_id,
                file_type=FileTypes.PHOTO
            )
        print(f"Ждем 60 секунду flood control")
        await sleep(60)


import asyncio

asyncio.run(main())