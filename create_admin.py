import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

password = bcrypt.generate_password_hash("admin123").decode('utf-8')

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (username, password, role, created_at)
VALUES (?, ?, ?, datetime('now'))
""", ("admin", password, "admin"))

conn.commit()
conn.close()

print("Admin created successfully")