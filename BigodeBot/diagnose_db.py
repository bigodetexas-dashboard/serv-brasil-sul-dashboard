"""
Database diagnostic utility.
Provides functions to check database health and integrity.
"""

import sqlite3
import os

DB_FILE = "bigode_unified.db"


def diagnose():
    """
    Performs a series of diagnostic checks on the SQLite database.
    Checks WAL mode, table row counts, indexes, and schema.
    """
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found!")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 1. Check WAL Mode
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        print(f"Journal Mode: {journal_mode}")

        # 2. Check pvp_kills count
        try:
            cursor.execute("SELECT count(*) FROM pvp_kills")
            count = cursor.fetchone()[0]
            print(f"Rows in pvp_kills: {count}")
        except sqlite3.OperationalError:
            print("Table pvp_kills does not exist.")

        # 3. Check indexes on pvp_kills
        print("\nIndexes on pvp_kills:")
        cursor.execute("PRAGMA index_list(pvp_kills)")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"  - Name: {idx[1]}, Unique: {idx[2]}")
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            cols = cursor.fetchall()
            for col in cols:
                print(f"      Column: {col[2]}")

        # 4. Check schema
        print("\nSchema of pvp_kills:")
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='pvp_kills'"
        )
        schema = cursor.fetchone()
        if schema:
            print(schema[0])

        conn.close()

    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f"Erro ao verificar integridade: {e}")


def check_db_integrity():
    """Check database integrity and report any issues."""
    # This function is added based on the user's instruction,
    # but its implementation is not provided in the prompt.
    # A basic placeholder is added to make it syntactically correct.
    print("Performing database integrity check...")
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found!")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        if result == "ok":
            print("Integrity check: OK")
        else:
            print(f"Integrity check failed: {result}")
        conn.close()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f"Error during integrity check: {e}")


if __name__ == "__main__":
    diagnose()
    # If the user intended to call check_db_integrity, it would be here.
    # For now, only diagnose() is called as per original __main__ block.
    # check_db_integrity()
