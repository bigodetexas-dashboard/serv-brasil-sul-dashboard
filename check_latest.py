import sqlite3
import os

db_path = "bigode_unified.db"


def check_db():
    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("--- LATEST DEATHS ---")
    try:
        cur.execute(
            "SELECT id, victim_gamertag, killer_gamertag, weapon, occurred_at FROM deaths_log ORDER BY id DESC LIMIT 3"
        )
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error reading deaths_log: {e}")

    print("\n--- LATEST DASHBOARD EVENTS ---")
    try:
        cur.execute(
            "SELECT id, type, content, created_at FROM dashboard_events ORDER BY id DESC LIMIT 3"
        )
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error reading dashboard_events: {e}")

    conn.close()


if __name__ == "__main__":
    check_db()
