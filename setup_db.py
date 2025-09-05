from loader import database

from Database.enums.user import UserStatus
from Database.enums.media_files import FileTypes

from Bot.utils.stash import stash_img

from asyncio import sleep

from scripts.make_thumbnail import make_collage_for_folder

users = [
    {
        "username": "ionewa",
        "telegram_id": 752021281,
        "status": UserStatus.INVITED
    }
    # {
    #     "username": "Vitestate",
    #     "telegram_id": 133353194,
    #     "status": UserStatus.INVITED
    # }
    # ,
    # {
    #     "username": "Sameliya",
    #     "telegram_id": 264976221,
    #     "status": UserStatus.INVITED
    # }
    # ,
    # {
    #     "username": "negakaif",
    #     "telegram_id": 128562688,
    #     "status": UserStatus.INVITED
    # }
    # ,
    # {
    #     "username": "@eremichew",
    #     "telegram_id": 316341973,
    #     "status": UserStatus.INVITED
    # }
]

texts = {
    "Clos17": """<b>Clos17</b>.
Тихий Староваганьковский переулок, архитектура французского ар-деко, всего 26 резиденций.

Высокие потолки, панорамные окна, свой сад и SPA, а за дверью — весь культурный центр столицы.""",
    "Узоры": """<b>Узоры</b>.
Клубный дом класса de luxe в Хамовниках — это камерный проект на 72 квартиры, где классическая архитектура встречается с современным комфортом. 
Пространство продумано до мелочей: панорамные окна, террасы, wellness-зона, приватный сад с арт-объектами и подземный паркинг. 

Уют, статус и высокий уровень сервиса для тех, кто ценит эстетику и тишину в самом сердце Москвы.""",
    "ЖК Joice": """<b>Joice</b>.
Комфорт, стиль и современные решения в одном проекте. Узнайте больше и найдите свой идеальный дом"""
}

async def main():
    await database.connect()
            # await database.drop_tables()
    await database.create_tables()

    # for user in users:
    #     await database.add_user(**user)

    
    post_id = await database.add_post(
        name="Тестовый первый пост",
        styles=[
            "Black",
            "Red",
            "Blue"
        ]
    )

    styles = ["Pastel"]
    posts = []

    for name in ["Clos17", "Узоры", "ЖК Joice"]:
        post_id = await database.add_post(
            styles=styles,
            name=name,
            text=texts.get(name)
        )
        posts.append(post_id)

        for style in styles:
            print(f"Добаляем новый стиль - {style} для {post_id}")
            for obj in ["story"]:
                for i in "123456":
                    if i == "6":
                        continue
                    print(f"Обрабатывает {post_id}/{obj}/{i}.png")
                    root_path = f"content/templates/{post_id}/{style}/{obj}"
                    path = f"/{i}.png"
                    file_id = await stash_img(f"{root_path}/{path}")

                    if obj == "post":
                        file_type = FileTypes.POST_PHOTO
                    elif obj == "story":
                        file_type = FileTypes.STORY_PHOTO

                    await database.add_media_file(
                        post_id=post_id,
                        style=style,
                        file_name=f"{style}/{i}.png",
                        description=f"Часть шаблона {obj}",
                        source_path=f"{root_path}/{path}",
                        telegram_file_id=file_id,
                        file_type=file_type
                    )
                print(f"Ждем 60 секунду flood control")
                await sleep(60)

            thumbnail = make_collage_for_folder(root_path, f"content/templates/{post_id}/{style}.png")
            thumbnail_file_id = await stash_img(thumbnail)
            await database.add_media_file(
                    post_id=post_id,
                    style=style,
                    file_name=f"{style}.png",
                    description="Превью шаблона",
                    source_path=f"content/templates/{post_id}/{style}.png",
                    telegram_file_id=thumbnail_file_id,
                    file_type=FileTypes.STYLE_PREVIEW
                )


import asyncio

asyncio.run(main())