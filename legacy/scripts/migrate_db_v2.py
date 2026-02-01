import sqlite3
import os

db_path = "bigode_unified.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if columns exist in clans
    cur.execute("PRAGMA table_info(clans)")
    columns = [col[1] for col in cur.fetchall()]

    if "symbol_color1" not in columns:
        print("Adding symbol_color1 to clans...")
        cur.execute("ALTER TABLE clans ADD COLUMN symbol_color1 TEXT DEFAULT '#8B0000'")

    if "symbol_color2" not in columns:
        print("Adding symbol_color2 to clans...")
        cur.execute("ALTER TABLE clans ADD COLUMN symbol_color2 TEXT DEFAULT '#000000'")

    conn.commit()
    conn.close()
    print("Database migration complete.")
else:
    print("DB file not found, nothing to migrate.")
