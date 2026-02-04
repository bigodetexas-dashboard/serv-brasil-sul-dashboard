import sqlite3
import os

DB_PATH = "bigode_unified.db"


def check_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        tables = [
            "shop_orders",
            "clan_members_v2",
            "clans",
            "player_identities",
            "ip_history",
        ]
        all_ok = True

        print(f"--- Checking Database: {DB_PATH} ---")

        for table in tables:
            try:
                cursor.execute(f"SELECT count(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ Table '{table}' exists. Rows: {count}")
            except sqlite3.OperationalError as e:
                print(f"❌ Table '{table}' check FAILED: {e}")
                all_ok = False

        conn.close()

        if all_ok:
            print("\nSUCCESS: All critical tables verify successfully.")
        else:
            print("\nFAILURE: Some tables are missing or corrupt.")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")


if __name__ == "__main__":
    check_db()
