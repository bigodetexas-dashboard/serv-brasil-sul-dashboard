"""
Item Repository Module

Manages shop items and inventory operations in the database.
Provides methods to query, filter, and retrieve shop items by category.
"""

from repositories.base_repository import BaseRepository
from flask_babel import gettext as _


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

    def get_items_by_category(
        self, category: str, active_only: bool = True
    ) -> list[dict]:
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
        return [_(row[0]) for row in rows]  # Traduz categoria

    def update_item_image(self, item_id: str, image_url: str) -> bool:
        """Atualiza a URL da imagem de um item."""
        query = "UPDATE shop_items SET image_url = ? WHERE id = ?"
        return self.execute_non_query(query, (image_url, item_id))

    def _row_to_dict(self, row) -> dict:
        """Converte uma linha do SQLite em dicionário."""
        if not row:
            return {}

        # Localizamos o nome e descrição caso existam traduções no .po
        return {
            "id": row[0],
            "item_key": row[1],
            "category": _(row[2]),  # Traduz categoria (ex: "armas")
            "name": _(row[3]),  # Traduz nome (ex: "M4A1 Tática")
            "price": row[4],
            "description": _(row[5]),  # Traduz descrição
            "is_active": row[6],
        }
