"""
Item Repository Module

Manages shop items and inventory operations in the database.
Provides methods to query, filter, and retrieve shop items by category.
"""

from repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get_all_shop_items(self, active_only: bool = True) -> list[dict]:
        """Retorna todos os itens da loja."""
        query = "SELECT * FROM shop_items"
        if active_only:
            query += " WHERE is_active = 1"

        rows = self.execute_query(query)
        return [self._row_to_dict(row) for row in rows]

    def get_items_by_category(self, category: str, active_only: bool = True) -> list[dict]:
        """Retorna itens de uma categoria específica."""
        query = "SELECT * FROM shop_items WHERE category = ?"
        params = [category]
        if active_only:
            query += " AND is_active = 1"

        rows = self.execute_query(query, params)
        return [self._row_to_dict(row) for row in rows]

    def get_item_by_key(self, item_key: str) -> dict | None:
        """Busca um item pela sua chave única."""
        query = "SELECT * FROM shop_items WHERE item_key = ?"
        rows = self.execute_query(query, (item_key,))
        if rows:
            return self._row_to_dict(rows[0])
        return None

    def get_all_categories(self, active_only: bool = True) -> list[str]:
        """Retorna a lista de categorias únicas."""
        query = "SELECT DISTINCT category FROM shop_items"
        if active_only:
            query += " WHERE is_active = 1"

        rows = self.execute_query(query)
        return [row[0] for row in rows]

    def _row_to_dict(self, row) -> dict:
        """Converte uma linha do SQLite em dicionário."""
        if not row:
            return {}
        return {
            "id": row[0],
            "item_key": row[1],
            "category": row[2],
            "name": row[3],
            "price": row[4],
            "description": row[5],
            "is_active": row[6],
        }
