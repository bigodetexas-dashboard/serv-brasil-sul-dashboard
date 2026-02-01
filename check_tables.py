import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def list_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Existing Tables ---")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(t[0])

    except Exception as e:
        print(f"Error listing tables: {e}")

    conn.close()


if __name__ == "__main__":
    list_tables()
