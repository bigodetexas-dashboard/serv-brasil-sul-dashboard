import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(events)")
        columns = cursor.fetchall()
        print("Events Table Columns:")
        for col in columns:
            print(col)
    except Exception as e:
        print(e)
    conn.close()


if __name__ == "__main__":
    check_schema()
