import sqlite3
import os

db_path = r"d:\dayz xbox\BigodeBot\new_dashboard\bigode_unified.db"


def update_delivery_queue():
    if not os.path.exists(db_path):
        print(f"Banco nÃ£o encontrado em {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Check if table exists and column exists
        cur.execute("PRAGMA table_info(delivery_queue)")
        columns = [row[1] for row in cur.fetchall()]

        if not columns:
            # Create table if it doesn't exist (fallback)
            print("Criando tabela delivery_queue...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS delivery_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT,
                    gamertag TEXT,
                    item_name TEXT,
                    item_code TEXT,
                    quantity INTEGER DEFAULT 1,
                    coordinates TEXT,
                    purchase_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    attempts INTEGER DEFAULT 0,
                    priority INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME
                )
            """)
        elif "gamertag" not in columns:
            print("Adicionando coluna gamertag Ã  delivery_queue...")
            cur.execute("ALTER TABLE delivery_queue ADD COLUMN gamertag TEXT")

        conn.commit()
        print("[OK] Tabela delivery_queue atualizada!")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    update_delivery_queue()
