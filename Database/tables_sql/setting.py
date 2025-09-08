settings_sql = """CREATE TABLE IF NOT EXISTS settings (
    telegram_id BIGINT REFERENCES users(telegram_id) UNIQUE,
    device TEXT,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""