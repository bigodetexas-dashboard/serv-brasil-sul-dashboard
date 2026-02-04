import sqlite3
import os

DB_PATH = "bigode_unified.db"
REQUIRED_TABLES = [
    "shop_orders",
    "clan_members_v2",
    "clans",
    "player_identities",
    "ip_history",
]


def verify_tables():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    print("\n=== Database Verification ===")
    all_exist = True
    for table in REQUIRED_TABLES:
        if table in existing_tables:
            print(f"✅ Table '{table}' exists.")
        else:
            print(f"❌ Table '{table}' MISSING.")
            all_exist = False

    return all_exist


if __name__ == "__main__":
    verify_tables()
