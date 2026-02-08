# -*- coding: utf-8 -*-
"""
Garante que a tabela connection_logs existe no banco de dados
BigodeTexas v2.4
"""
import sqlite3
import os
import sys

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db")


def ensure_connection_logs_table():
    """Cria tabela connection_logs se não existir"""

    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Criar tabela connection_logs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gamertag TEXT NOT NULL,
                discord_id TEXT,
                ip_address TEXT,
                xuid TEXT,
                server_name TEXT,
                connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                disconnected_at DATETIME,
                session_duration INTEGER,
                is_suspicious BOOLEAN DEFAULT 0,
                notes TEXT
            )
        """)

        # Índices para performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connection_gamertag ON connection_logs(gamertag)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connection_ip ON connection_logs(ip_address)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connection_xuid ON connection_logs(xuid)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connection_date ON connection_logs(connected_at)")

        conn.commit()

        print("[OK] Tabela connection_logs criada/verificada com sucesso!")
        print("     - Índices: gamertag, ip_address, xuid, connected_at")

        # Verificar se existe dados
        cur.execute("SELECT COUNT(*) FROM connection_logs")
        count = cur.fetchone()[0]
        print(f"     - Registros existentes: {count}")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao criar tabela connection_logs: {e}")
        return False


if __name__ == "__main__":
    print("BigodeTexas - Garantindo tabela connection_logs\n")
    success = ensure_connection_logs_table()
    sys.exit(0 if success else 1)
