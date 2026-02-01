import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def check_shop_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Schema for shop_items ---")
    try:
        # Get column info
        cursor.execute("PRAGMA table_info(shop_items)")
        columns = cursor.fetchall()

        found_image_url = False
        for col in columns:
            print(col)
            if col[1] == "image_url":
                found_image_url = True

        if found_image_url:
            print("\nSUCCESS: 'image_url' column exists.")
        else:
            print("\nWARNING: 'image_url' column MISSING.")

    except Exception as e:
        print(f"Error checking shop_items: {e}")

    conn.close()


if __name__ == "__main__":
    check_shop_table()
