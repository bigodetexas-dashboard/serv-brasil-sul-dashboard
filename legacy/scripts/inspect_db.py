import sqlite3
import os

db_path = "bigode_unified.db"
if not os.path.exists(db_path):
    print("DB file not found")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")
        cur.execute(f"PRAGMA table_info({table[0]})")
        columns = cur.fetchall()
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")
    conn.close()
