import sqlite3
import os

DB_FILE = "bigode_unified.db"


def check_table(table_name):
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        return False

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        result = cur.fetchone()
        conn.close()

        if result:
            print(f"[OK] Table '{table_name}' exists.")
            return True
        else:
            print(f"[MISSING] Table '{table_name}' NOT found.")
            return False
    except Exception as e:
        print(f"Error checking DB: {e}")
        return False


if __name__ == "__main__":
    check_table("dashboard_events")
    check_table("bases_v2")
    check_table("shop_items")
