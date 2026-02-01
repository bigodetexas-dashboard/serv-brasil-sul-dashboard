"""
Script para verificar e criar a tabela shop_items no banco de dados.
"""

import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join("new_dashboard", "bigode_unified.db")


def check_and_create_shop_items_table():
    """Verifica se a tabela shop_items existe e a cria se necessário."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Listar todas as tabelas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print("Tabelas existentes no banco:")
    for table in tables:
        print(f"  - {table[0]}")

    # Verificar se shop_items existe
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='shop_items'"
    )
    exists = cur.fetchone()

    if not exists:
        print("\n❌ Tabela shop_items NÃO existe. Criando...")

        # Criar tabela shop_items
        cur.execute("""
            CREATE TABLE shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_key TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                image_url TEXT DEFAULT '/static/img/items/default.png',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Tabela shop_items criada com sucesso!")
    else:
        print("\n✅ Tabela shop_items já existe.")

        # Mostrar estrutura da tabela
        cur.execute("PRAGMA table_info(shop_items)")
        columns = cur.fetchall()
        print("\nEstrutura da tabela shop_items:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # Contar itens
        cur.execute("SELECT COUNT(*) FROM shop_items")
        count = cur.fetchone()[0]
        print(f"\nTotal de itens na loja: {count}")

    conn.close()


if __name__ == "__main__":
    check_and_create_shop_items_table()
