from asyncpg import Pool, create_pool

from typing import List, Optional
from datetime import datetime

from .enums.user import (
    UserStatus
)

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
        await self.execute("DROP SCHEMA public CASCADE")
        await self.execute("CREATE SCHEMA public")

    async def add_user(self, telegram_id: int, username: str, status: str):
        await self.execute(
            'INSERT INTO users (telegram_id, username, status) VALUES ($1, $2, $3) '
            'ON CONFLICT (telegram_id) DO UPDATE SET username = $2, updated_at = current_timestamp',
            telegram_id, username, status
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
            'status = $6 '
            'WHERE telegram_id = $7',
            name, phone_number, email,
            photo_tg, photo_source,
            UserStatus.ACTIVE,
            telegram_id
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
        if status not in UserStatus.ALL:
            raise ValueError(f"\"{status}\" не входит в список доступных статусов")

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
        styles: List[str]
    ) -> int:
        return await self.execute(
            'INSERT INTO posts (name, styles) VALUES ($1,$2) returning id',
            name, styles,
            fetchval=True
        )

    async def get_post_styles(self, post_id: int) -> List[str]:
        return await self.execute(
            'SELECT styles FROM posts WHERE id = $', post_id,
            fetchval=True
        )
    
    async def get_post_files(
        self, post_id: int, style: str
    ) -> List[str]:
        res = await self.execute(
            'SELECT telegram_file_id FROM media_files WHERE post_id = $1 and style = $2',
            post_id, style,
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
            'VALUES ($1,$2,$3,$4,$5,$6,$7)',
            post_id, style,
            file_name, description,
            source_path, telegram_file_id, file_type
        )
    
