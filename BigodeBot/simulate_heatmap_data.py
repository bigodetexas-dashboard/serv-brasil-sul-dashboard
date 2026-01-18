import sqlite3
import random
import os
from datetime import datetime

# DB Path
DB_FILE = "bigode_unified.db"

# Locations (Central points)
LOCATIONS = [
    (4600, 10000),  # NWAF
    (12000, 9000),  # Berezino
    (6500, 2500),  # Cherno
    (10500, 2300),  # Elektro
    (1700, 14000),  # Tisy
    (6000, 7700),  # Stary
]

WEAPONS = ["M4A1", "Mosin", "Lar", "Kame", "Tundra", "SKS"]


def populate():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Generating simulated Heatmap data...")
    count = 0

    for _ in range(50):
        # Pick random location
        bx, bz = random.choice(LOCATIONS)

        # Add spread (Gaussian distribution for more natural hotspots)
        gx = bx + random.gauss(0, 200)
        gz = bz + random.gauss(0, 200)

        # Clamp to map bounds
        gx = max(0, min(15360, gx))
        gz = max(0, min(15360, gz))

        killer = f"Survivor_{random.randint(100, 999)}"
        victim = f"Victim_{random.randint(100, 999)}"
        weapon = random.choice(WEAPONS)
        dist = random.randint(10, 800)

        cursor.execute(
            """
            INSERT INTO pvp_kills (killer_name, victim_name, weapon, distance, game_x, game_y, game_z, timestamp)
            VALUES (?, ?, ?, ?, ?, 0, ?, datetime('now'))
        """,
            (killer, victim, weapon, dist, gx, gz),
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"Success! Inserted {count} fake kills.")


if __name__ == "__main__":
    populate()
