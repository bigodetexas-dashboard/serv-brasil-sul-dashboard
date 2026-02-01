# -*- coding: utf-8 -*-
"""
Script para sincronizar itens em AMBOS os bancos de dados.
"""

import sqlite3
import json
import os

# Caminhos dos bancos
DB_PATHS = [
    "bigode_unified.db",  # Banco raiz (usado pelos repositórios)
    os.path.join("new_dashboard", "bigode_unified.db"),  # Banco do dashboard
]
ITEMS_JSON = "items.json"


def sync_items_to_db(db_path):
    """Sincroniza itens do JSON para um banco específico."""
    print(f"\n{'=' * 60}")
    print(f"  Sincronizando: {db_path}")
    print(f"{'=' * 60}")

    # Carregar items.json
    with open(ITEMS_JSON, "r", encoding="utf-8") as f:
        items_data = json.load(f)

    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Criar tabela se não existir
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop_items (
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

    # Sincronizar itens
    inserted = 0
    updated = 0

    for category, items in items_data.items():
        for item_key, item_info in items.items():
            # Verificar se item já existe
            cur.execute("SELECT id FROM shop_items WHERE item_key = ?", (item_key,))
            exists = cur.fetchone()

            if exists:
                # Atualizar item existente
                cur.execute(
                    """
                    UPDATE shop_items
                    SET category = ?, name = ?, price = ?, description = ?
                    WHERE item_key = ?
                """,
                    (
                        category,
                        item_info["name"],
                        item_info["price"],
                        item_info.get("description", ""),
                        item_key,
                    ),
                )
                updated += 1
            else:
                # Inserir novo item
                cur.execute(
                    """
                    INSERT INTO shop_items (item_key, category, name, price, description)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        item_key,
                        category,
                        item_info["name"],
                        item_info["price"],
                        item_info.get("description", ""),
                    ),
                )
                inserted += 1

    conn.commit()

    # Verificar contagem final
    cur.execute("SELECT COUNT(*) FROM shop_items")
    final_count = cur.fetchone()[0]

    print(f"  Novos: {inserted} | Atualizados: {updated} | Total: {final_count}")

    conn.close()
    return final_count


def main():
    print("=" * 60)
    print("  SINCRONIZACAO COMPLETA DE ITENS - BigodeTexas")
    print("=" * 60)

    total_synced = 0
    for db_path in DB_PATHS:
        if os.path.exists(db_path) or "new_dashboard" in db_path:
            count = sync_items_to_db(db_path)
            total_synced += count
        else:
            print(f"\n  Pulando {db_path} (não existe)")

    print(f"\n{'=' * 60}")
    print(f"  CONCLUIDO! Total de itens em todos os bancos: {total_synced}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
