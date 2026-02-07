import sqlite3
import os

dbs = ["pvp_events.db", "bigode_unified.db", "sync_queue.db"]
for db in dbs:
    if os.path.exists(db):
        print(f"\n--- {db} ---")
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                print(f"Table: {table[0]}")
                # Print columns
                cursor.execute(f"PRAGMA table_info({table[0]})")
                cols = cursor.fetchall()
                col_names = [c[1] for c in cols]
                print(f"  Columns: {col_names}")
            conn.close()
        except Exception as e:
            print(f"Error reading {db}: {e}")
    else:
        print(f"\n{db} not found")
