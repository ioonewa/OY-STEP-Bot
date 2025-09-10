from .users import users_table_sql
from .media_files import media_files_sql
from .posts import posts_sql
from .setting import settings_sql
from .invites import invites_sql

from .waiting_list import waiting_list_sql

tables_sql = [
    users_table_sql,
    posts_sql,
    media_files_sql,
    settings_sql,

    invites_sql,
    waiting_list_sql
]