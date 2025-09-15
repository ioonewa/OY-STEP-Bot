from asyncpg import Pool, create_pool

from typing import List, Optional, Literal
from datetime import datetime

import json

from . import enums

from .models import (
    Settings
)

from config import ObjParams
import logging

logger = logging.getLogger(__name__)

class Database:
    _pool: Pool
    _credentials: dict

    def __init__(self, credentials):
        self._credentials = credentials
        logger.info(f"dns - {credentials}")
    
    async def connect(self):
        logger.debug('Initializing pool.')
        self._pool = await create_pool(**self._credentials)
        logger.info('Pool initialized')

    async def execute(self,
                      command: str,
                      *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      executemany: bool = False):
        if self._pool is None:
            return

        async with self._pool.acquire() as connection:
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                    if result:
                        result = dict(result)
                elif executemany:
                    result = await connection.executemany(command, *args)
                else:
                    result = await connection.execute(command, *args)

            return result
    
    async def create_tables(self):
        from .tables_sql import tables_sql

        logger.info(f"Создаем ({len(tables_sql)}) таблиц")
        for table in tables_sql:
            await self.execute(table)
        logger.info(f"({len(tables_sql)}) таблиц успешно созданы")

    async def drop_tables(self):
        # await self.execute("DROP SCHEMA public CASCADE")
        await self.execute("DROP TABLE media_files")
        await self.execute("DROP TABLE posts")
        # await self.execute("CREATE SCHEMA public")

    async def add_user(self, telegram_id: int, username: str, status: str):
        await self.execute(
            'INSERT INTO users (telegram_id, username, status) VALUES ($1, $2, $3) '
            'ON CONFLICT (telegram_id) DO UPDATE SET username = $2, updated_at = current_timestamp',
            telegram_id, username, status
        )
        await self.add_user_to_settings(telegram_id)

    async def get_users(self) -> List[int]:
        res = await self.execute('SELECT telegram_id FROM users WHERE status = $1', enums.UserStatus.ACTIVE, fetch=True)

        return [_['telegram_id'] for _ in res]

    async def add_user_to_settings(self, telegram_id: int):
        await self.execute(
            'INSERT INTO settings (telegram_id, device) VALUES ($1, $2) '
            'ON CONFLICT (telegram_id) DO NOTHING',
            telegram_id, enums.DeviceTypes.IOS
        )

    async def get_settings(self, telegram_id: int) -> Optional[Settings]:
        result = await self.execute(
            'SELECT * FROM settings WHERE telegram_id = $1',
            telegram_id,
            fetchrow=True
        )
        if result:
            return Settings(**result)
        else:
            await self.add_user_to_settings(telegram_id)
            return await self.get_settings(telegram_id)

    async def update_device(self, telegram_id: int, device: str):
        await self.execute(
            'UPDATE settings SET device = $1, updated_at = current_timestamp WHERE telegram_id = $2',
            device, telegram_id
        )

    async def update_notifications(self, telegram_id: int, enabled: bool):
        await self.execute(
            'UPDATE settings SET notifications_enabled = $1, updated_at = current_timestamp WHERE telegram_id = $2',
            enabled, telegram_id
        )

    async def registrate_user(
        self,
        telegram_id: int,
        name: str, 
        phone_number: str,
        email: str,
        photo_source: str,
        photo_tg: str
    ):
        await self.execute(
            'UPDATE users SET name = $1, phone_number = $2, '
            'email = $3, photo_tg = $4, photo_source = $5, '
            'status = $6, updated_at = current_timestamp '
            'WHERE telegram_id = $7',
            name, phone_number, email,
            photo_tg, photo_source,
            enums.UserStatus.ACTIVE,
            telegram_id
        )

    async def update_name(
        self,
        telegram_id: int,
        name: str
    ):
        await self.execute(
            'UPDATE users SET name = $1, updated_at = current_timestamp '
            'WHERE telegram_id = $2',
            name, telegram_id
        )

    async def get_user_data_dict(self, telegram_id: int) -> dict:
        return await self.execute(
            'SELECT username, phone_number, email, photo_source, photo_tg, name FROM users WHERE telegram_id = $1',
            telegram_id,
            fetchrow=True
        )

    async def get_user_status(self, telegram_id: int) -> Optional[str]:
        return await self.execute(
            'SELECT status FROM users WHERE telegram_id = $1',
            telegram_id,
            fetchval=True
        )
    
    async def update_user_status(self, telegram_id: int, status: str):
        if status not in enums.UserStatus.ALL:
            raise ValueError(f"\"{status}\" не входит в список доступных статусов")
        
        logger.info(f"Обновляем статус пользователя ({telegram_id}) - {status}")
        await self.execute(
            'UPDATE users SET status = $2 WHERE telegram_id = $1',
            telegram_id, status
        )

    async def get_user(self, telegram_id: int):
        return await self.execute(
            'SELECT * FROM users WHERE telegram_id = $1',
            telegram_id,
            fetchrow=True
        )

    async def add_post(
        self, 
        name: str,
        styles: List[str],
        text: str
    ) -> int:
        return await self.execute(
            'INSERT INTO posts (name, styles, text) VALUES ($1,$2,$3)'
            'ON CONFLICT (name) DO UPDATE SET text = $3 '
            'RETURNING id',
            name, styles, text,
            fetchval=True
        )

    async def get_post_styles(self, post_id: int) -> List[str]:
        return await self.execute(
            'SELECT styles FROM posts WHERE id = $1', post_id,
            fetchval=True
        )
    
    async def get_posts_id(self) -> List[int]:
        res = await self.execute(
            'SELECT id FROM posts',
            fetch=True
        )

        return [_['id'] for _ in res]
    
    async def get_post_text(self, post_id: int) -> Optional[str]:
        return await self.execute(
            'SELECT text FROM posts WHERE id = $1',
            post_id,
            fetchval=True
        )
    
    async def get_content_files(
        self,
        post_id: int,
        style: str,
        file_type: str
    ) -> List[str]:
        res = await self.execute(
            'SELECT telegram_file_id FROM media_files WHERE post_id = $1 and style = $2 and file_type = $3',
            post_id, style, file_type,
            fetch=True
        )
        return [_['telegram_file_id'] for _ in res]

    async def add_media_file(
        self,
        post_id: Optional[int],
        style: Optional[str],
        file_name: str,
        description: str,
        source_path: str,
        telegram_file_id: str,
        file_type: str
    ):
        await self.execute(
            'INSERT INTO media_files (post_id, style, file_name, description, source_path, telegram_file_id, file_type) '
            'VALUES ($1,$2,$3,$4,$5,$6,$7) '
            'ON CONFLICT (post_id, style, file_type, file_name) DO UPDATE SET '
            'description = $4, source_path = $5, telegram_file_id = $6, file_type = $7',
            post_id, style,
            file_name, description,
            source_path, telegram_file_id, file_type
        )
    
    async def add_invite_link(
        self,
        creator_id: int,
        code: str,
        status: str = enums.InviteStatuses.ACTIVE
    ):
        await self.execute(
            'INSERT INTO invite_links (created_by, code, status) VALUES ($1,$2,$3)',
            creator_id, code, status
        )

    async def is_code_exists(
        self,
        code
    ) -> bool:
        res = await self.execute(
            'SELECT id FROM ivite_links WHERE code = $1 and status = $2',
            code, enums.InviteStatuses.ACTIVE,
            fetchval=True
        )

        if res:
            return True
        else:
            return False
        
    async def use_invite_link(
        self,
        code: str,
        user_id: int
    ) -> bool:
        res = await self.execute(
            '''
            UPDATE invite_links
            SET used_by = $1,
                used_at = CURRENT_TIMESTAMP,
                status = $2
            WHERE code = $3 AND status = $4
            RETURNING created_by
            ''',
            user_id, enums.InviteStatuses.USED, code, enums.InviteStatuses.ACTIVE,
            fetchval=True
        )

        return res

    async def add_content_rules(
        self,
        post_id: int,
        post_rules: dict,
        story_rules: dict
    ):
        await self.execute(
            'INSERT INTO content_rules (post_id, post, story) VALUES ($1,$2,$3) '
            'ON CONFLICT(post_id) DO UPDATE SET '
            'post = $2, story = $3',
            post_id, json.dumps(post_rules), json.dumps(story_rules)
        )

    async def get_content_rules(
        self,
        post_id: int,
        obj: Literal['post', 'story']
    ) -> ObjParams:
        result = await self.execute(
            f'SELECT {obj} FROM content_rules WHERE post_id = $1',
            post_id,
            fetchval=True
        )
        return json.loads(result)