import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table: bases_v2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bases_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id TEXT NOT NULL,
        name TEXT NOT NULL,
        location TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: base_permissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS base_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_id INTEGER NOT NULL,
        discord_id TEXT NOT NULL,
        level TEXT NOT NULL,
        granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(base_id) REFERENCES bases_v2(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
    print("Tables 'bases_v2' and 'base_permissions' created (if they didn't exist).")


if __name__ == "__main__":
    create_tables()
