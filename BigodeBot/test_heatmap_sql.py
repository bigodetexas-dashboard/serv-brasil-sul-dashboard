"""
Script de teste para validar as consultas SQL utilizadas no Heatmap.
Verifica se as estatísticas de kills, localização e timeline estão funcionando corretamente.
"""

import sqlite3

DB_FILE = "bigode_unified.db"


def validate_database_schema():
    """Validate that pvp_kills table exists with correct schema."""
    print("[*] Validando schema do banco...")
    try:
        conn = sqlite3.connect(DB_FILE, timeout=60)
        cur = conn.cursor()

        # Verificar se tabela existe
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='pvp_kills'
        """)

        if not cur.fetchone():
            print("   [X] ERRO: Tabela pvp_kills nao existe!")
            print("   [!] Execute: python scripts/init_heatmap_db.py")
            conn.close()
            return False

        # Verificar colunas essenciais
        cur.execute("PRAGMA table_info(pvp_kills)")
        columns = {row[1] for row in cur.fetchall()}
        required = {"timestamp", "game_x", "game_z", "event_type"}

        if not required.issubset(columns):
            missing = required - columns
            print(f"   [X] ERRO: Colunas faltando: {missing}")
            conn.close()
            return False

        print("   [OK] Schema valido!")
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"   [X] ERRO: {e}")
        return False


def test_heatmap_sql():
    """Executa consultas de teste no banco de dados para validar a lógica do Heatmap."""
    print(f"Testing Heatmap SQL on {DB_FILE}...")

    # Validar schema antes de executar testes
    if not validate_database_schema():
        print("\n[!] Abortando testes. Corrija o schema primeiro.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # 1. Base Heatmap Query
        print("1. Testing Base Heatmap Query...")
        cur.execute(
            "SELECT game_x as x, game_z as z FROM pvp_kills "
            "WHERE timestamp >= datetime('now', '-24 hours')"
        )
        rows = cur.fetchall()
        if not rows:
            print("   [INFO] No data found (Table empty?).")
        else:
            print(f"   Success. Rows: {len(rows)}")

        # 2. Top Locations Query
        print("2. Testing Top Locations Query...")
        cur.execute("""
            SELECT
                CAST(game_x/1000 AS INTEGER)*1000 + 500 as center_x,
                CAST(game_z/1000 AS INTEGER)*1000 + 500 as center_z,
                COUNT(*) as deaths
            FROM pvp_kills
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY CAST(game_x/1000 AS INTEGER), CAST(game_z/1000 AS INTEGER)
            ORDER BY deaths DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        print(f"   Success. Rows: {len(rows)}")

        # 3. Timeline Query
        print("3. Testing Timeline Query...")
        fmt = "%Y-%m-%d %H:00:00"
        # Using parameterized query to prevent SQL Injection (Bandit B608)
        query = """
            SELECT strftime(?, timestamp) as period, COUNT(*) as pvp
            FROM pvp_kills
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY period
            ORDER BY period
        """
        cur.execute(query, (fmt,))
        rows = cur.fetchall()
        print(f"   Success. Rows: {len(rows)}")

        conn.close()
        print("\nAll Heatmap SQL queries are valid.")
    except sqlite3.Error as e:
        print(f"\n[DATABASE ERROR] SQL Test Failed: {e}")
    except (IOError, ValueError) as e:
        print(f"\n[SYSTEM ERROR] Test Failed: {e}")


if __name__ == "__main__":
    test_heatmap_sql()
