# -*- coding: utf-8 -*-
"""
Script para popular banco com mortes simuladas para testes
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Caminho do banco
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db")

# Dados simulados
PLAYERS = [
    "Jogador1",
    "Jogador2",
    "Jogador3",
    "Jogador4",
    "Jogador5",
    "Sniper_Pro",
    "Rambo_BR",
    "Survivor_123",
    "Hunter_Wolf",
    "Bear_Slayer",
    "Noob_Player",
    "Pro_Gamer",
    "Tactical_Ops",
    "Silent_Killer",
    "Medic_Hero",
]

WEAPONS = [
    "M4A1",
    "AKM",
    "Mosin",
    "SVD",
    "SKS",
    "Winchester",
    "KA-M",
    "LAR",
    "VSS",
    "Blaze",
    "Tundra",
    "FX-45",
]

LOCATIONS = [
    "Cherno",
    "Elektro",
    "Berezino",
    "Novo",
    "Severograd",
    "Vybor",
    "Zelenogorsk",
    "NWAF",
    "NEAF",
    "Floresta",
]

ANIMALS = ["wolf", "bear"]


def create_deaths_table():
    """Cria tabela deaths_log se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deaths_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            killer_gamertag TEXT,
            victim_gamertag TEXT NOT NULL,
            death_type TEXT NOT NULL CHECK (death_type IN ('pvp', 'animal')),
            death_cause TEXT NOT NULL,
            weapon TEXT,
            distance REAL,
            body_part TEXT,
            is_headshot INTEGER DEFAULT 0,
            coord_x REAL,
            coord_z REAL,
            coord_y REAL,
            location_name TEXT,
            coins_gained INTEGER DEFAULT 0,
            coins_lost INTEGER DEFAULT 0,
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            server_id TEXT DEFAULT 'serv-brasil-sul',
            session_id TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] Tabela deaths_log criada/verificada")


def insert_test_deaths(count=50):
    """Insere mortes de teste no banco"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now()

    for i in range(count):
        # 70% PvP, 30% Animal
        is_pvp = random.random() < 0.7

        # Timestamp aleatório nas últimas 24h
        hours_ago = random.uniform(0, 24)
        occurred_at = now - timedelta(hours=hours_ago)

        if is_pvp:
            # Morte PvP
            killer = random.choice(PLAYERS)
            victim = random.choice([p for p in PLAYERS if p != killer])
            weapon = random.choice(WEAPONS)
            distance = random.randint(5, 500)
            is_headshot = 1 if random.random() < 0.3 else 0  # 30% headshots
            location = random.choice(LOCATIONS)

            # Coordenadas fictícias
            coord_x = random.uniform(2000, 15000)
            coord_z = random.uniform(2000, 15000)

            cur.execute(
                """
                INSERT INTO deaths_log (
                    killer_gamertag, victim_gamertag, death_type, death_cause,
                    weapon, distance, is_headshot, location_name,
                    coord_x, coord_z, occurred_at, coins_gained
                ) VALUES (?, ?, 'pvp', 'player', ?, ?, ?, ?, ?, ?, ?, 50)
            """,
                (
                    killer,
                    victim,
                    weapon,
                    distance,
                    is_headshot,
                    location,
                    coord_x,
                    coord_z,
                    occurred_at,
                ),
            )

        else:
            # Morte por animal
            victim = random.choice(PLAYERS)
            animal = random.choice(ANIMALS)
            location = random.choice(LOCATIONS)

            coord_x = random.uniform(2000, 15000)
            coord_z = random.uniform(2000, 15000)
            coord_y = random.uniform(0, 100)

            cur.execute(
                """
                INSERT INTO deaths_log (
                    victim_gamertag, death_type, death_cause,
                    location_name, coord_x, coord_z, coord_y, occurred_at
                ) VALUES (?, 'animal', ?, ?, ?, ?, ?, ?)
            """,
                (victim, animal, location, coord_x, coord_z, coord_y, occurred_at),
            )

    conn.commit()
    conn.close()
    print(f"[OK] {count} mortes de teste inseridas!")


def show_stats():
    """Mostra estatísticas do banco"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Total
    cur.execute("SELECT COUNT(*) FROM deaths_log")
    total = cur.fetchone()[0]

    # PvP
    cur.execute("SELECT COUNT(*) FROM deaths_log WHERE death_type = 'pvp'")
    pvp = cur.fetchone()[0]

    # Animal
    cur.execute("SELECT COUNT(*) FROM deaths_log WHERE death_type = 'animal'")
    animal = cur.fetchone()[0]

    # Headshots
    cur.execute("SELECT COUNT(*) FROM deaths_log WHERE is_headshot = 1")
    headshots = cur.fetchone()[0]

    # Arma mais usada
    cur.execute("""
        SELECT weapon, COUNT(*) as count
        FROM deaths_log
        WHERE death_type = 'pvp'
        GROUP BY weapon
        ORDER BY count DESC
        LIMIT 1
    """)
    most_weapon = cur.fetchone()

    # Local mais mortal
    cur.execute("""
        SELECT location_name, COUNT(*) as count
        FROM deaths_log
        GROUP BY location_name
        ORDER BY count DESC
        LIMIT 1
    """)
    most_location = cur.fetchone()

    conn.close()

    print("\n" + "=" * 50)
    print("ESTATÍSTICAS DO BANCO")
    print("=" * 50)
    print(f"Total de mortes: {total}")
    print(f"PvP: {pvp}")
    print(f"Animais: {animal}")
    print(f"Headshots: {headshots}")
    if most_weapon:
        print(f"Arma mais usada: {most_weapon[0]} ({most_weapon[1]}x)")
    if most_location:
        print(f"Local mais mortal: {most_location[0]} ({most_location[1]}x)")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    print("[*] Criando/verificando tabela...")
    create_deaths_table()

    print("[*] Inserindo mortes de teste...")
    insert_test_deaths(50)

    print("[*] Mostrando estatísticas...")
    show_stats()

    print("[OK] Pronto! Acesse http://localhost:5001/deaths para ver o feed!")
