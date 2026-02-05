"""
Script de inicializaÃ§Ã£o do banco de dados para o sistema de Heatmap.
Valida schema, cria tabelas faltantes e popula com dados de exemplo.
"""
# -*- coding: utf-8 -*-

import os
import random
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "bigode_unified.db"


def init_heatmap_database():
    """Initialize heatmap database with proper schema and sample data."""
    print(f"[*] Verificando banco de dados: {DB_FILE}")

    if not os.path.exists(DB_FILE):
        print(f"[!] Banco nao encontrado. Criando {DB_FILE}...")

    conn = sqlite3.connect(DB_FILE, timeout=60)
    cur = conn.cursor()

    # Verificar se tabela existe
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='pvp_kills'
    """)

    if not cur.fetchone():
        print("[+] Criando tabela pvp_kills...")
        cur.execute("""
            CREATE TABLE pvp_kills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                killer_name TEXT,
                victim_name TEXT,
                weapon TEXT,
                distance INTEGER,
                game_x REAL NOT NULL,
                game_z REAL NOT NULL,
                event_type TEXT DEFAULT 'pvp'
            )
        """)
        print("[OK] Tabela criada com sucesso!")
    else:
        print("[OK] Tabela pvp_kills ja existe.")

        # Verificar se coluna event_type existe (migracao)
        cur.execute("PRAGMA table_info(pvp_kills)")
        columns = {row[1] for row in cur.fetchall()}

        if "event_type" not in columns:
            print("[+] Adicionando coluna event_type (migracao)...")
            cur.execute("ALTER TABLE pvp_kills ADD COLUMN event_type TEXT DEFAULT 'pvp'")
            print("[OK] Coluna adicionada!")

    # Verificar se estÃ¡ vazia
    cur.execute("SELECT COUNT(*) FROM pvp_kills")
    count = cur.fetchone()[0]

    if count == 0:
        print("[+] Populando com dados de exemplo...")
        populate_sample_data(conn)
    else:
        print(f"[OK] Banco contem {count} registros.")

    conn.commit()
    conn.close()
    print("[SUCCESS] Inicializacao concluida!")


def populate_sample_data(conn):
    """Populate with 100 realistic sample kills."""
    cur = conn.cursor()

    weapons = ["AKM", "M4A1", "Mosin", "SKS", "Winchester", "Pistol"]
    names = ["Player1", "Survivor2", "Hunter3", "Bandit4", "Hero5"]

    # Hotspots conhecidos no mapa Chernarus
    hotspots = [
        (7500, 7500),  # Centro (Gorka)
        (4500, 10200),  # Noroeste (NWAF)
        (10500, 2300),  # Sudeste (Elektro)
        (6400, 11800),  # Norte (Tisy)
        (13400, 3100),  # Leste (Berezino)
    ]

    base_time = datetime.now() - timedelta(hours=24)

    for _ in range(100):
        # Distribuir ~70% nos hotspots, ~30% aleatÃ³rio
        if random.random() < 0.7:
            base_x, base_z = random.choice(hotspots)
            x = base_x + random.randint(-500, 500)
            z = base_z + random.randint(-500, 500)
        else:
            x = random.uniform(1000, 14000)
            z = random.uniform(1000, 14000)

        timestamp = base_time + timedelta(minutes=random.randint(0, 1440))

        cur.execute(
            """
            INSERT INTO pvp_kills
            (timestamp, killer_name, victim_name, weapon, distance, game_x, game_z, event_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                timestamp.isoformat(),
                random.choice(names),
                random.choice(names),
                random.choice(weapons),
                random.randint(10, 500),
                x,
                z,
                "pvp" if random.random() < 0.8 else "pve",
            ),
        )

    print("[OK] Inseridos 100 registros de exemplo!")


if __name__ == "__main__":
    init_heatmap_database()
