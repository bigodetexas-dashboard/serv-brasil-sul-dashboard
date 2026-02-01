import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "bigode_unified.db")
MIGRATION_FILE = os.path.join(os.getcwd(), "migrations", "001_security_tables.sql")


def apply_migration():
    print(f"Applying migration to {DB_PATH}...")

    if not os.path.exists(MIGRATION_FILE):
        print(f"Error: Migration file not found at {MIGRATION_FILE}")
        return

    with open(MIGRATION_FILE, "r") as f:
        sql_script = f.read()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        print("✅ Migration applied successfully!")
    except Exception as e:
        print(f"❌ Error applying migration: {e}")


if __name__ == "__main__":
    apply_migration()
