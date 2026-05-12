import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    created_at TIMESTAMP
)
""")

# TASKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    assigned_to INTEGER,
    status TEXT,
    deadline DATE,
    file_path TEXT,
    created_at TIMESTAMP
)
""")

# LOGS
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    ip TEXT,
    device TEXT,
    location TEXT,
    timestamp TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database initialized successfully ")