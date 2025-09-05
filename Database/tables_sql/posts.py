posts_sql = """CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    text TEXT,
    styles TEXT[],

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""