import sqlite3
from datetime import datetime

from Lib import email

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # ✅ THIS FIXES EVERYTHING
    return conn


# ================= USERS =================
def create_user(username, password, role, email):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password, role, email, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (username, password, role, email, datetime.now()))

    conn.commit()
    conn.close()


def get_user_by_username(username):
    import sqlite3
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    conn.close()
    return user


def get_all_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return users


def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()


# ================= TASKS =================
def create_task(title, assigned_to, deadline):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, assigned_to, status, deadline, created_at)
        VALUES (?, ?, 'pending', ?, ?)
    """, (title, assigned_to, deadline, datetime.now()))

    conn.commit()
    conn.close()


def get_tasks_by_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE assigned_to=?", (user_id,))
    tasks = cursor.fetchall()

    conn.close()
    return tasks

def get_tasks_assigned_to_manager(manager_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM tasks WHERE assigned_to = ?
    """, (manager_id,))

    tasks = cursor.fetchall()
    conn.close()
    return tasks


def update_task_status(task_id, status):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks SET status=? WHERE id=?
    """, (status, task_id))

    conn.commit()
    conn.close()

def update_task_file(task_id, filename):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks SET file_path=? WHERE id=?
    """, (filename, task_id))

    conn.commit()
    conn.close()


# ================= LOGS =================
def log_action(user_id, action, ip, device, location):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (user_id, action, ip, device, location, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
    """, (user_id, action, ip, device, location))

    conn.commit()
    conn.close()


def get_logs():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        logs.id,
        users.username,
        logs.action,
        logs.ip,
        logs.timestamp
    FROM logs
    LEFT JOIN users ON logs.user_id = users.id
    ORDER BY logs.timestamp DESC
""")
    logs = cursor.fetchall()

    conn.close()
    return logs


def get_all_employees():
        conn = get_db()
        cursor = conn.cursor()
    
        cursor.execute("SELECT id, username FROM users WHERE role='employee'")
        users = cursor.fetchall()
    
        conn.close()
        return users


def get_all_tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, assigned_to, status, deadline, file_path, manager_file
        FROM tasks
    """)

    tasks = cursor.fetchall()
    conn.close()
    return tasks

def reject_task(task_id, reason):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status=?, reject_reason=?
        WHERE id=?
    """, ("rejected", reason, task_id))

    conn.commit()
    conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user

def update_manager_file(task_id, filename):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks SET manager_file=? WHERE id=?
    """, (filename, task_id))

    print("rows affected:", cursor.rowcount)
    conn.commit()
    conn.close()