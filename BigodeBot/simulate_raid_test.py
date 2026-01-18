import sqlite3
import math
import os

DB_PATH = "bigode_unified.db"


def setup_dummy_base():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Insert a test base at 5000, 5000. Schema: owner_id, name, x, y, z, radius
    cursor.execute(
        "INSERT INTO bases (name, owner_id, x, z, y, radius, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        ("Base Teste Alpha", "test_user_001", 5000.0, 5000.0, 100.0, 100.0),
    )
    conn.commit()
    print("[INFO] Base de Teste criada em X: 5000, Z: 5000")
    conn.close()


def cleanup_dummy_base():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bases WHERE name = 'Base Teste Alpha'")
    conn.commit()
    print("[INFO] Base de Teste removida.")
    conn.close()


def check_raid(x, z):
    print(f"\n[SCAN] Verificando Coordenadas: X={x}, Z={z}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name, x, z FROM bases")
    bases = cursor.fetchall()

    triggered = []

    for b in bases:
        bx, bz = b["x"], b["z"]
        dist = math.sqrt((x - bx) ** 2 + (z - bz) ** 2)

        if dist <= 100.0:
            print(f"   [VIOLACAO] Perto de '{b['name']}' (Dist: {dist:.1f}m)")
        elif dist <= 300.0:
            print(f"   [ALERTA] Proximo a '{b['name']}' (Dist: {dist:.1f}m)")
        else:
            print(f"   [OK] Seguro em relacao a '{b['name']}' (Dist: {dist:.1f}m)")

    conn.close()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Erro: DB nao encontrado.")
    else:
        try:
            setup_dummy_base()

            # Test Case 1: Violation (Close)
            check_raid(5020, 5020)  # Sqrt(20^2 + 20^2) = ~28m

            # Test Case 2: Warning (Medium)
            check_raid(5150, 5150)  # Sqrt(150^2 + 150^2) = ~212m

            # Test Case 3: Safe (Far)
            check_raid(1000, 1000)

        except Exception as e:
            print(f"Erro no teste: {e}")
        finally:
            cleanup_dummy_base()
