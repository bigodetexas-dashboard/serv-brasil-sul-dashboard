# -*- coding: utf-8 -*-
"""
Módulo de Heartbeat para Sistema de Failover Inteligente.
Gerencia sinais de vida dos sistemas principal e backup.
"""

import sqlite3
import os
from datetime import datetime, timedelta

# Caminho do banco de sincronização
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "sync_queue.db")


def send_heartbeat(system_name):
    """
    Envia heartbeat para indicar que o sistema está vivo.

    Args:
        system_name (str): Nome do sistema ('primary' ou 'backup')
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE system_status
            SET is_active = TRUE,
                last_heartbeat = ?,
                status = 'running'
            WHERE system_name = ?
        """,
            (datetime.now().isoformat(), system_name),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[HEARTBEAT] Erro ao enviar heartbeat: {e}")


def check_primary_alive(timeout_seconds=120):
    """
    Verifica se o sistema principal está vivo.

    Args:
        timeout_seconds (int): Tempo máximo sem heartbeat (padrão: 120s)

    Returns:
        bool: True se está vivo, False caso contrário
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT last_heartbeat, status
            FROM system_status
            WHERE system_name = 'primary'
        """)
        row = cur.fetchone()
        conn.close()

        if not row or not row[0]:
            return False

        last_heartbeat = datetime.fromisoformat(row[0])
        elapsed = (datetime.now() - last_heartbeat).total_seconds()

        # Considera morto se não responder há X segundos
        return elapsed < timeout_seconds

    except Exception as e:
        print(f"[HEARTBEAT] Erro ao verificar sistema principal: {e}")
        return False


def get_system_status(system_name):
    """
    Obtém status completo de um sistema.

    Args:
        system_name (str): Nome do sistema ('primary' ou 'backup')

    Returns:
        dict: Status do sistema ou None se não encontrado
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            """
            SELECT * FROM system_status
            WHERE system_name = ?
        """,
            (system_name,),
        )

        row = cur.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        print(f"[HEARTBEAT] Erro ao obter status: {e}")
        return None


def mark_system_stopped(system_name):
    """
    Marca um sistema como parado.

    Args:
        system_name (str): Nome do sistema ('primary' ou 'backup')
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE system_status
            SET is_active = FALSE,
                status = 'stopped'
            WHERE system_name = ?
        """,
            (system_name,),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[HEARTBEAT] Erro ao marcar sistema como parado: {e}")


def mark_system_failed(system_name):
    """
    Marca um sistema como falho.

    Args:
        system_name (str): Nome do sistema ('primary' ou 'backup')
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE system_status
            SET is_active = FALSE,
                status = 'failed'
            WHERE system_name = ?
        """,
            (system_name,),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[HEARTBEAT] Erro ao marcar sistema como falho: {e}")
