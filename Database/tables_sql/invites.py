invites_sql = """CREATE TABLE IF NOT EXISTS invite_links (
    id SERIAL PRIMARY KEY,
    created_by BIGINT,
    used_by BIGINT,
    code TEXT UNIQUE,
    used_at TIMESTAMP DEFAULT current_timestamp,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""