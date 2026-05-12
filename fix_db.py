import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Fix missing role
cursor.execute("UPDATE users SET role='employee' WHERE role IS NULL")

# Fix missing email
cursor.execute("UPDATE users SET email='default@gmail.com' WHERE email IS NULL")

conn.commit()

print("Database fixed successfully!")

conn.close()