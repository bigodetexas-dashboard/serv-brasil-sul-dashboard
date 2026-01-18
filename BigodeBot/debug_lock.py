"""
Database lock debugging utility.
Helps identify and diagnose database locking issues.
"""

import sqlite3

try:
    conn = sqlite3.connect("bigode_unified.db", timeout=5)
    print("Connected.")
    cursor = conn.cursor()
    print("Trying to write...")
    cursor.execute("CREATE TABLE IF NOT EXISTS _lock_check (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO _lock_check DEFAULT VALUES")
    print("Write successful.")
    conn.commit()
    print("Commit successful.")
except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
    print(f"Database error: {e}")
finally:
    if "conn" in locals():
        conn.close()
