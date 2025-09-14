content_rules_sql = """CREATE TABLE IF NOT EXISTS content_rules (
    post_id INT PRIMARY KEY REFERENCES posts(id),
    post JSONB NOT NULL,
    story JSONB NOT NULL
)"""