# -*- coding: utf-8 -*-
"""
Migração: Adiciona colunas faltantes no leaderboard
- zombie_kills (mortes de zombies)
- distance_traveled (distância percorrida)
- vehicle_distance (distância de veículo)
- reconnects (reconexões)
- buildings_placed (construções)
- raids_completed (raids)
"""
import sqlite3
import os
import sys

# Adicionar raiz do projeto ao sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import database

def run_migration():
    """Adiciona colunas faltantes à tabela players"""
    # Conectar diretamente ao SQLite
    db_path = os.path.join(project_root, "bigode_unified.db")
    if not os.path.exists(db_path):
        print(f"[ERROR] Banco de dados nao encontrado: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    if not conn:
        print("[ERROR] Nao foi possivel conectar ao banco de dados")
        return False

    columns_to_add = [
        ("zombie_kills", "INTEGER DEFAULT 0"),
        ("distance_traveled", "REAL DEFAULT 0.0"),
        ("vehicle_distance", "REAL DEFAULT 0.0"),
        ("reconnects", "INTEGER DEFAULT 0"),
        ("buildings_placed", "INTEGER DEFAULT 0"),
        ("raids_completed", "INTEGER DEFAULT 0"),
    ]

    try:
        cur = conn.cursor()

        # Verificar quais colunas já existem
        cur.execute("PRAGMA table_info(players)")
        existing_columns = [row[1] for row in cur.fetchall()]

        added_count = 0
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                print(f"+ Adicionando coluna: {column_name}")
                cur.execute(f"ALTER TABLE players ADD COLUMN {column_name} {column_type}")
                added_count += 1
            else:
                print(f"OK  Coluna já existe: {column_name}")

        conn.commit()
        print(f"\n[OK] Migração concluída! {added_count} colunas adicionadas.")
        return True

    except Exception as e:
        print(f"[ERROR] Erro durante migração: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO: Adicionar colunas ao leaderboard")
    print("=" * 60)
    run_migration()
