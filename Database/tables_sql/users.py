users_table_sql = """CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(50),

    
    name TEXT,                      --Содержит Имя и Фамилию
    phone_number TEXT,
    email TEXT,
    photo_tg TEXT,
    photo_source TEXT,

    status TEXT,
    subscription TEXT,
    
    updated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""