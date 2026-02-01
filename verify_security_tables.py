import sqlite3
import os

DB_PATH = "bigode_unified.db"


def check_tables():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ["security_bans", "waf_logs"]
    all_exist = True

    for table in tables:
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        if cur.fetchone():
            print(f"[OK] Table '{table}' exists.")
        else:
            print(f"[MISSING] Table '{table}' NOT found.")
            all_exist = False

    conn.close()

    if all_exist:
        print("SUCCESS: All security tables present.")
    else:
        print("FAILURE: Some tables missing.")


if __name__ == "__main__":
    check_tables()
