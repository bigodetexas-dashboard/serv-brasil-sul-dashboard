from repositories.base_repository import BaseRepository


class PlayerBaseRepository(BaseRepository):
    """
    Repository for managing Player Bases and Permissions.
    """

    def create_base(self, owner_id: str, name: str, location: str = "") -> int | None:
        """
        Creates a new base for a player.
        """
        query = """
            INSERT INTO bases_v2 (owner_id, name, location, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """
        return self.execute_query(query, (str(owner_id), name, location))

    def get_player_bases(self, owner_id: str | int) -> list[dict]:
        """
        Get all bases owned by a specific player.
        """
        query = "SELECT * FROM bases_v2 WHERE owner_id = ?"
        rows = self.execute_query(query, (str(owner_id),))
        return [dict(row) for row in rows] if rows else []

    def get_base_by_id(self, base_id: int) -> dict | None:
        """
        Get base details by ID.
        """
        query = "SELECT * FROM bases_v2 WHERE id = ?"
        rows = self.execute_query(query, (base_id,))
        return dict(rows[0]) if rows else None

    def add_permission(
        self, base_id: int, target_discord_id: str | int, level: str
    ) -> bool:
        """
        Add a permission (BUILDER, GUEST, CO_OWNER) for a user on a base.
        """
        # Valid levels: 'BUILDER', 'GUEST', 'CO_OWNER'
        # Check if permission already exists, update if so
        check_query = (
            "SELECT id FROM base_permissions WHERE base_id = ? AND discord_id = ?"
        )
        existing = self.execute_query(check_query, (base_id, str(target_discord_id)))

        if existing:
            query = "UPDATE base_permissions SET level = ?, granted_at = datetime('now') WHERE id = ?"
            return self.execute_query(query, (level, existing[0]["id"])) is not None
        else:
            query = """
                INSERT INTO base_permissions (base_id, discord_id, level, granted_at)
                VALUES (?, ?, ?, datetime('now'))
            """
            return (
                self.execute_query(query, (base_id, str(target_discord_id), level))
                is not None
            )

    def revoke_permission(self, base_id: int, target_discord_id: str | int) -> bool:
        """
        Remove permission for a user on a base.
        """
        query = "DELETE FROM base_permissions WHERE base_id = ? AND discord_id = ?"
        return self.execute_query(query, (base_id, str(target_discord_id))) is not None

    def get_base_permissions(self, base_id: int) -> list[dict]:
        """
        List all permissions for a specific base.
        """
        query = "SELECT * FROM base_permissions WHERE base_id = ?"
        rows = self.execute_query(query, (base_id,))
        return [dict(row) for row in rows] if rows else []
