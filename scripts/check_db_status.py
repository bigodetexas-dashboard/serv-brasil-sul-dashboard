import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def check_db():
    if not os.path.exists(DB_PATH):
        print(f"DATABASE FILE NOT FOUND AT: {DB_PATH}")
        return

    print(f"Checking database at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"\nTotal Tables: {len(tables)}")
        print("-" * 30)

        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"Table '{table_name}': {count} rows")
            except Exception as e:
                print(f"Table '{table_name}': Error getting count ({e})")

        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")


if __name__ == "__main__":
    check_db()
