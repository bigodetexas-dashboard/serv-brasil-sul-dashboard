# -*- coding: utf-8 -*-
"""
Gerenciador de Sincronização para Sistema de Failover Inteligente.
Gerencia fila de eventos e sincronização entre sistemas principal e backup.
"""

import sqlite3
import json
import os
from datetime import datetime

# Caminho do banco de sincronização
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "sync_queue.db")


class SyncManager:
    """Gerenciador de sincronização de eventos entre sistemas"""

    def __init__(self):
        self.db_path = DB_PATH

    def queue_event(self, event_type, event_data, processed_by):
        """
        Adiciona evento à fila de sincronização.

        Args:
            event_type (str): Tipo do evento ('construction', 'ban', 'pvp', etc)
            event_data (dict): Dados do evento
            processed_by (str): Sistema que processou ('primary' ou 'backup')

        Returns:
            int: ID do evento na fila
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO sync_queue (event_type, event_data, processed_by, processed_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    event_type,
                    json.dumps(event_data, ensure_ascii=False),
                    processed_by,
                    datetime.now().isoformat(),
                ),
            )

            event_id = cur.lastrowid
            conn.commit()
            conn.close()

            return event_id

        except Exception as e:
            print(f"[SYNC] Erro ao adicionar evento à fila: {e}")
            return None

    def has_pending_sync(self):
        """
        Verifica se há eventos pendentes de sincronização.

        Returns:
            bool: True se há eventos pendentes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = FALSE")
            count = cur.fetchone()[0]
            conn.close()

            return count > 0

        except Exception as e:
            print(f"[SYNC] Erro ao verificar eventos pendentes: {e}")
            return False

    def get_pending_events(self, limit=100):
        """
        Obtém eventos pendentes de sincronização.

        Args:
            limit (int): Número máximo de eventos a retornar

        Returns:
            list: Lista de eventos pendentes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                """
                SELECT id, event_type, event_data, processed_by, processed_at
                FROM sync_queue
                WHERE synced = FALSE AND processed_by = 'backup'
                ORDER BY processed_at ASC
                LIMIT ?
            """,
                (limit,),
            )

            events = [dict(row) for row in cur.fetchall()]
            conn.close()

            # Deserializa JSON dos dados
            for event in events:
                event["event_data"] = json.loads(event["event_data"])

            return events

        except Exception as e:
            print(f"[SYNC] Erro ao obter eventos pendentes: {e}")
            return []

    def mark_synced(self, event_id):
        """
        Marca evento como sincronizado.

        Args:
            event_id (int): ID do evento

        Returns:
            bool: True se sucesso
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE sync_queue
                SET synced = TRUE, synced_at = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), event_id),
            )

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            print(f"[SYNC] Erro ao marcar evento como sincronizado: {e}")
            return False

    def process_backup_events(self):
        """
        Processa todos os eventos que foram executados pelo backup.
        Este método é chamado quando o sistema principal retorna.

        Returns:
            int: Número de eventos processados
        """
        events = self.get_pending_events()

        if not events:
            return 0

        print(f"[SYNC] Processando {len(events)} eventos do backup...")

        processed_count = 0

        for event in events:
            try:
                event_id = event["id"]
                event_type = event["event_type"]
                event_data = event["event_data"]

                print(
                    f"[SYNC] Evento {event_id} ({event_type}): {event_data.get('player', 'N/A')}"
                )

                # Aqui você pode adicionar lógica específica por tipo de evento
                # Por exemplo, registrar no banco principal, enviar notificações, etc.

                # Por enquanto, apenas marca como sincronizado
                # (os eventos já foram processados pelo backup, apenas registramos)

                self.mark_synced(event_id)
                processed_count += 1

            except Exception as e:
                print(f"[SYNC] Erro ao processar evento {event['id']}: {e}")
                continue

        print(f"[SYNC] ✅ {processed_count} eventos sincronizados com sucesso!")
        return processed_count

    def get_sync_stats(self):
        """
        Obtém estatísticas da fila de sincronização.

        Returns:
            dict: Estatísticas da fila
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            # Total de eventos
            cur.execute("SELECT COUNT(*) FROM sync_queue")
            total = cur.fetchone()[0]

            # Eventos pendentes
            cur.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = FALSE")
            pending = cur.fetchone()[0]

            # Eventos sincronizados
            cur.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = TRUE")
            synced = cur.fetchone()[0]

            # Eventos por sistema
            cur.execute("""
                SELECT processed_by, COUNT(*)
                FROM sync_queue
                GROUP BY processed_by
            """)
            by_system = dict(cur.fetchall())

            conn.close()

            return {
                "total": total,
                "pending": pending,
                "synced": synced,
                "by_system": by_system,
            }

        except Exception as e:
            print(f"[SYNC] Erro ao obter estatísticas: {e}")
            return {}

    def clear_old_events(self, days=7):
        """
        Remove eventos sincronizados com mais de X dias.

        Args:
            days (int): Número de dias para manter eventos

        Returns:
            int: Número de eventos removidos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

            cur.execute(
                """
                DELETE FROM sync_queue
                WHERE synced = TRUE AND synced_at < ?
            """,
                (cutoff_date.isoformat(),),
            )

            deleted = cur.rowcount
            conn.commit()
            conn.close()

            print(f"[SYNC] Removidos {deleted} eventos antigos (>{days} dias)")
            return deleted

        except Exception as e:
            print(f"[SYNC] Erro ao limpar eventos antigos: {e}")
            return 0
