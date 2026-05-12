from app.models import get_db

def reset_system():
    conn = get_db()
    cursor = conn.cursor()

    print("⚠️ Clearing tasks and logs...")

    # Delete only tasks and logs
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM logs")

    # Reset auto-increment IDs (optional but good for demo)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='logs'")

    conn.commit()
    conn.close()

    print(" Reset complete (users preserved)")

if __name__ == "__main__":
    reset_system()
