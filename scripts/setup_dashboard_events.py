import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def setup_dashboard_events():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking dashboard_events table...")
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_events'"
        )
        if not cursor.fetchone():
            print("Table 'dashboard_events' NOT FOUND. Creating it...")
            cursor.execute("""
            CREATE TABLE dashboard_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                related_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
            print("Table 'dashboard_events' created successfully.")
        else:
            print("Table 'dashboard_events' already exists.")

        conn.commit()

    except Exception as e:
        print(f"Migration failed: {e}")

    conn.close()


if __name__ == "__main__":
    setup_dashboard_events()
