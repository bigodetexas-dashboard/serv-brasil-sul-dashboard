import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = ["bases_v2", "base_permissions"]
    for table in tables:
        print(f"--- Schema for {table} ---")
        try:
            cursor.execute(
                f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            result = cursor.fetchone()
            if result:
                print(result[0])
            else:
                print(f"Table {table} NOT FOUND")
        except Exception as e:
            print(f"Error checking {table}: {e}")

    conn.close()


if __name__ == "__main__":
    check_schema()
