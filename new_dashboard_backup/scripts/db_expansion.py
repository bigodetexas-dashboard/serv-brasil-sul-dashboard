import sqlite3
import os

DB_FILE = "bigode_unified.db"


def expand_db():
    print(f"Iniciando expansão do banco: {DB_FILE}...")

    if not os.path.exists(DB_FILE):
        print("ERRO: Banco de dados não encontrado! Execute init_sqlite_db.py primeiro.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # 1. Tabela de Chat de Clã
        print("Criando tabela clan_messages...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clan_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clan_id INTEGER NOT NULL,
            sender_discord_id TEXT NOT NULL,
            sender_name TEXT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE
        )
        """)

        # 2. Tabela de Empréstimos (Loans)
        print("Criando tabela user_loans...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            remaining_amount INTEGER NOT NULL,
            interest_rate REAL DEFAULT 0.05,
            status TEXT DEFAULT 'active', -- active, paid, overdue
            due_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
        )
        """)

        # 3. Tabela de Inventário de Base
        print("Criando tabela base_inventory...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS base_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            last_updated_by TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(base_id) REFERENCES bases(id) ON DELETE CASCADE
        )
        """)

        # 4. Tabela de Logs de Base (Ataques/Defesas)
        print("Criando tabela base_logs...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS base_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- raid, intruder, defense, permission_change
            description TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(base_id) REFERENCES bases(id) ON DELETE CASCADE
        )
        """)

        # 5. Adicionando campos extras na tabela users
        print("Adicionando campos extras na tabela users...")
        try:
            cur.execute("ALTER TABLE users ADD COLUMN last_interest_at TIMESTAMP")
        except sqlite3.OperationalError:
            print("Campo last_interest_at já existe.")

        try:
            cur.execute("ALTER TABLE users ADD COLUMN clan_rank TEXT DEFAULT 'member'")
        except sqlite3.OperationalError:
            print("Campo clan_rank já existe.")

        conn.commit()
        print("SUCCESS: Expansao concluida com sucesso!")

    except Exception as e:
        print(f"ERROR: Erro durante a expansao: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    expand_db()
