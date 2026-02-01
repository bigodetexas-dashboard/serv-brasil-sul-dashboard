"""
Events Repository Module

Manages system events for the dashboard (Killfeed, Notifications, Status).
"""

from repositories.base_repository import BaseRepository
from datetime import datetime


class EventsRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add_event(self, event_type: str, content: str, related_id: int = None) -> bool:
        """
        Adiciona um novo evento ao banco de dados.
        :param event_type: Tipo do evento (KILLFEED, SYSTEM, WAR, SHOP)
        :param content: Conteúdo/Mensagem do evento
        :param related_id: ID opcional relacionado (ex: ID do usuário ou clã)
        """
        query = """
        INSERT INTO dashboard_events (type, content, related_id, created_at)
        VALUES (?, ?, ?, datetime('now'))
        """
        try:
            self.execute_query(query, (event_type, content, related_id))
            return True
        except Exception as e:
            print(f"Error adding event: {e}")
            return False

    def get_recent_events(self, limit: int = 20, event_type: str = None) -> list[dict]:
        """Retorna os eventos mais recentes."""
        if event_type:
            query = "SELECT * FROM dashboard_events WHERE type = ? ORDER BY created_at DESC LIMIT ?"
            params = (event_type, limit)
        else:
            query = "SELECT * FROM dashboard_events ORDER BY created_at DESC LIMIT ?"
            params = (limit,)

        rows = self.execute_query(query, params)
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row) -> dict:
        """Converte uma linha do banco em dicionário."""
        if not row:
            return {}
        # Assumes schema: id, type, content, related_id, created_at
        # Check if row has enough columns
        if len(row) < 5:
            return {}

        return {
            "id": row[0],
            "type": row[1],
            "content": row[2],
            "related_id": row[3],
            "created_at": row[4],
        }
