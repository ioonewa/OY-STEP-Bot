from loader import database

import asyncio

from config import content_rules

async def main():
    await database.connect()
    await database.create_tables()

    for post_id, content_rule in content_rules.items():
        post_id = int(post_id)
        await database.add_content_rules(
            post_id,
            post_rules=content_rule['post'],
            story_rules=content_rule['story']
        )
    

asyncio.run(main())