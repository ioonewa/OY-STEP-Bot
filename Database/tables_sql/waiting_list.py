waiting_list_sql = """
CREATE TABLE IF NOT EXISTS waiting_list (
    id SERIAL PRIMARY KEY,

    telegram_id BIGINT UNIQUE,
    username TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""