import sqlite3
import os

DB_PATH = r"d:\dayz xbox\BigodeBot\bigode_unified.db"


def migrate_shop_images():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking shop_items table...")
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='shop_items'"
        )
        if not cursor.fetchone():
            print("Table 'shop_items' NOT FOUND. Creating it...")
            cursor.execute("""
            CREATE TABLE shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_key TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                image_url TEXT DEFAULT '/static/img/items/default.png'
            );
            """)
            print("Table 'shop_items' created successfully.")

            # Insert some sample data
            print("Inserting sample items...")
            samples = [
                (
                    "m4a1",
                    "armas",
                    "M4-A1 Assault Rifle",
                    5000,
                    "Rifle de assalto 5.56mm",
                    1,
                    "/static/img/items/m4a1.png",
                ),
                (
                    "akm",
                    "armas",
                    "AKM Assault Rifle",
                    4500,
                    "Rifle de assalto 7.62mm",
                    1,
                    "/static/img/items/akm.png",
                ),
                (
                    "food_can",
                    "comidas",
                    "Canned Bacon",
                    200,
                    "Comida enlatada",
                    1,
                    "/static/img/items/bacon.png",
                ),
                (
                    "bandage",
                    "medico",
                    "Bandage",
                    100,
                    "Bandagem esterilizada",
                    1,
                    "/static/img/items/bandage.png",
                ),
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO shop_items (item_key, category, name, price, description, is_active, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                samples,
            )
            print("Sample items inserted.")

        else:
            print("Table 'shop_items' EXISTS. Checking column...")
            cursor.execute("PRAGMA table_info(shop_items)")
            columns = [col[1] for col in cursor.fetchall()]

            if "image_url" not in columns:
                print("Adding 'image_url' column...")
                cursor.execute(
                    "ALTER TABLE shop_items ADD COLUMN image_url TEXT DEFAULT '/static/img/items/default.png'"
                )
                print("'image_url' column added.")
            else:
                print("'image_url' column already exists.")

        conn.commit()

    except Exception as e:
        print(f"Migration failed: {e}")

    conn.close()


if __name__ == "__main__":
    migrate_shop_images()
