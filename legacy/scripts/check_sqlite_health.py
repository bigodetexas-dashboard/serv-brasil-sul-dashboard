import sqlite3
import os

DB_FILE = "bigode_unified.db"


def check_sqlite_health():
    print("=" * 80)
    print("VERIFICANDO SAÚDE DO SQLITE (UNIFICADO)")
    print("=" * 80)

    if not os.path.exists(DB_FILE):
        print(f"[ERRO] Arquivo {DB_FILE} não encontrado!")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Listar tabelas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cur.fetchall()]
        print(f"Tabelas encontradas ({len(tables)}): {', '.join(tables)}")
        print("-" * 40)

        critical_tables = [
            "users",
            "clans",
            "clan_members",
            "shop_items",
            "pvp_kills",
            "bounties",
            "clan_wars",
            "transactions",
        ]
        for table in critical_tables:
            if table in tables:
                cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cur.fetchone()["count"]
                print(f"[OK] {table:15} | Registros: {count}")
            else:
                print(f"[FALHA] {table:14} | NÃO ENCONTRADA!")

        print("-" * 40)

        # Verificar se há usuários vinculados
        cur.execute(
            "SELECT COUNT(*) as count FROM users WHERE discord_id IS NOT NULL AND nitrado_gamertag IS NOT NULL"
        )
        linked_users = cur.fetchone()["count"]
        print(f"Usuários Vinculados (Discord + GT): {linked_users}")

        # Verificar saldo total na economia
        cur.execute("SELECT SUM(balance) as total FROM users")
        total_balance = cur.fetchone()["total"] or 0
        print(f"Saldo Total em Circulação: {total_balance} DZCoins")

        conn.close()
        print("=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA")
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao ler banco: {e}")


if __name__ == "__main__":
    check_sqlite_health()
