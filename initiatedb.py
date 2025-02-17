import sqlite3

DB_PATH = "database/business.db"

with sqlite3.connect(DB_PATH) as conn:
    with open("database/schema.sql", "r") as f:
        conn.executescript(f.read())

print("Database schema initialized successfully!")