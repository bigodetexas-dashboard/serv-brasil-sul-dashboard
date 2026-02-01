import sqlite3
import os

DB_FILE = "bigode_unified.db"


def migrate():
    print(f"Iniciando migração de Perfil Premium: {DB_FILE}...")

    if not os.path.exists(DB_FILE):
        print("ERRO: Banco de dados não encontrado!")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:
        # 1. Campos de Personalização e Privacidade
        print("Adicionando campos de personalização...")
        columns_to_add = [
            ("bio_type", "TEXT DEFAULT 'auto'"),
            ("bio_content", "TEXT"),
            ("banner_url", "TEXT"),
            ("avatar_url", "TEXT"),
            ("show_stats", "INTEGER DEFAULT 1"),
            ("pinned_achievements", "TEXT"),  # JSON list
            # Métricas de Playstyle
            ("zombie_kills", "INTEGER DEFAULT 0"),
            ("buildings_placed", "INTEGER DEFAULT 0"),
            ("trees_cut", "INTEGER DEFAULT 0"),
            ("fish_caught", "INTEGER DEFAULT 0"),
            ("meters_traveled", "REAL DEFAULT 0.0"),
        ]

        for col_name, col_type in columns_to_add:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"  + Coluna {col_name} adicionada.")
            except sqlite3.OperationalError:
                print(f"  - Coluna {col_name} já existe.")

        # 2. Tabela de Histórico de Clãs
        print("Criando tabela clan_history...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL,
            clan_name TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        print("MIGRAÇÃO CONCLUÍDA: Banco de dados atualizado para Perfil Premium.")

    except Exception as e:
        print(f"ERRO durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
