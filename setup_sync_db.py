# -*- coding: utf-8 -*-
"""
Script para criar banco de dados de sincronização do sistema de failover.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sync_queue.db")


def create_database():
    """Cria as tabelas necessárias para o sistema de failover"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabela de fila de sincronização
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            processed_by TEXT NOT NULL,
            processed_at TIMESTAMP NOT NULL,
            synced BOOLEAN DEFAULT FALSE,
            synced_at TIMESTAMP
        )
    """)

    # Tabela de status dos sistemas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_status (
            id INTEGER PRIMARY KEY,
            system_name TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            last_heartbeat TIMESTAMP,
            status TEXT
        )
    """)

    # Inicializa status dos sistemas
    cur.execute("""
        INSERT OR IGNORE INTO system_status (id, system_name, is_active, status)
        VALUES (1, 'primary', FALSE, 'stopped')
    """)

    cur.execute("""
        INSERT OR IGNORE INTO system_status (id, system_name, is_active, status)
        VALUES (2, 'backup', FALSE, 'stopped')
    """)

    conn.commit()
    conn.close()

    print(f"Banco de dados criado com sucesso em: {DB_PATH}")
    print("Tabelas criadas:")
    print("  - sync_queue (fila de sincronização)")
    print("  - system_status (status dos sistemas)")


if __name__ == "__main__":
    create_database()
