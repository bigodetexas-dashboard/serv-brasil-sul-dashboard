import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def optimize_db():
    if not os.path.exists(DB_PATH):
        print(f"DATABASE FILE NOT FOUND AT: {DB_PATH}")
        return

    print(f"Optimizing database at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Enable Write-Ahead Logging (WAL) for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        mode = cursor.fetchone()[0]
        print(f"Journal Mode set to: {mode}")

        # Enable Foreign Keys enforcement
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA foreign_keys;")
        fk = cursor.fetchone()[0]
        print(f"Foreign Keys enabled: {bool(fk)}")

        # Optimize size
        cursor.execute("VACUUM;")
        print("Database vacuumed (compacted).")

        conn.commit()
        conn.close()
        print("Optimization complete.")
    except Exception as e:
        print(f"Error optimizing database: {e}")


if __name__ == "__main__":
    optimize_db()
