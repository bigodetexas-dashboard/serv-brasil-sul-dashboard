"""
Script para criar índices de performance no banco de dados do heatmap.
Executa via Python para compatibilidade com PowerShell.
"""

import sqlite3
import os

DB_FILE = "bigode_unified.db"


def create_heatmap_indexes():
    """Cria índices otimizados para queries do heatmap."""
    print(f"[*] Conectando ao banco: {DB_FILE}")

    if not os.path.exists(DB_FILE):
        print(f"[X] ERRO: Banco {DB_FILE} nao encontrado!")
        return False

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    indexes = [
        (
            "idx_pvp_timestamp",
            "CREATE INDEX IF NOT EXISTS idx_pvp_timestamp ON pvp_kills(timestamp)",
        ),
        ("idx_pvp_weapon", "CREATE INDEX IF NOT EXISTS idx_pvp_weapon ON pvp_kills(weapon)"),
        (
            "idx_pvp_coords",
            "CREATE INDEX IF NOT EXISTS idx_pvp_coords ON pvp_kills(game_x, game_z)",
        ),
        (
            "idx_pvp_composite",
            "CREATE INDEX IF NOT EXISTS idx_pvp_composite ON pvp_kills(timestamp, weapon, game_x, game_z)",
        ),
        (
            "idx_pvp_event_type",
            "CREATE INDEX IF NOT EXISTS idx_pvp_event_type ON pvp_kills(event_type)",
        ),
    ]

    print("\n[+] Criando indices de performance...")
    for name, sql in indexes:
        try:
            cur.execute(sql)
            print(f"   [OK] {name}")
        except sqlite3.Error as e:
            print(f"   [X] Erro ao criar {name}: {e}")

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Indices criados com sucesso!")
    return True


if __name__ == "__main__":
    create_heatmap_indexes()
