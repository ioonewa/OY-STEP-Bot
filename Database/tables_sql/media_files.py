media_files_sql = """
CREATE TABLE IF NOT EXISTS media_files (
    id SERIAL PRIMARY KEY,

    post_id INT REFERENCES posts (id),
    style TEXT,
    
    file_name TEXT,
    description TEXT,
    source_path TEXT,
    telegram_file_id TEXT,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (post_id, style, file_type, file_name)
)"""