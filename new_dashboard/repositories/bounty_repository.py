"""
Bounty Repository Module

Manages bounty (reward) data in the database.
Provides methods to create, update, retrieve, and remove bounties on players.
"""

from repositories.base_repository import BaseRepository


class BountyRepository(BaseRepository):
    """
    Repository for managing player bounties.

    Bounties are rewards placed on players for killing them.
    Multiple players can add to the same bounty, increasing the total reward.
    """

    def get_all_bounties(self) -> list[dict]:
        """
        Retrieve all active bounties ordered by amount (highest first).

        Returns:
            List of bounty dictionaries with keys:
            - id: Bounty ID
            - victim_gamertag: Target player's gamertag
            - amount: Total bounty amount
            - placed_by_discord_id: Discord ID of who placed it
            - created_at: When bounty was created
            - updated_at: Last update timestamp

        Example:
            >>> repo = BountyRepository()
            >>> bounties = repo.get_all_bounties()
            >>> for bounty in bounties:
            ...     print(f"{bounty['victim_gamertag']}: ${bounty['amount']}")
        """
        query = "SELECT * FROM bounties ORDER BY amount DESC"
        rows = self.execute_query(query)
        return [dict(row) for row in rows] if rows else []

    def get_bounty(self, gamertag: str) -> dict | None:
        """
        Get bounty information for a specific player.

        Args:
            gamertag: Player's gamertag (case-insensitive)

        Returns:
            Bounty dictionary if exists, None otherwise

        Example:
            >>> repo = BountyRepository()
            >>> bounty = repo.get_bounty("PlayerName")
            >>> if bounty:
            ...     print(f"Bounty: ${bounty['amount']}")
        """
        query = "SELECT * FROM bounties WHERE victim_gamertag = ?"
        rows = self.execute_query(query, (gamertag.lower(),))
        return dict(rows[0]) if rows else None

    def add_or_update_bounty(
        self, gamertag: str, amount: int, placed_by: str | None = None
    ) -> bool:
        """
        Add a new bounty or increase existing bounty amount.

        If a bounty already exists for this player, the amount is added
        to the existing bounty. Otherwise, a new bounty is created.

        Args:
            gamertag: Target player's gamertag
            amount: Bounty amount to add (must be positive)
            placed_by: Discord ID of player placing bounty (optional)

        Returns:
            True if successful, False otherwise

        Example:
            >>> repo = BountyRepository()
            >>> # Place initial bounty
            >>> repo.add_or_update_bounty("BadPlayer", 1000, "123456")
            True
            >>> # Add to existing bounty
            >>> repo.add_or_update_bounty("BadPlayer", 500, "789012")
            True
            >>> # Total bounty is now 1500
        """
        if amount <= 0:
            print("[ERROR] Bounty amount must be positive")
            return False

        query = """
            INSERT INTO bounties (victim_gamertag, amount, placed_by_discord_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(victim_gamertag) DO UPDATE SET
                amount = amount + excluded.amount,
                updated_at = datetime('now')
        """
        result = self.execute_query(
            query, (gamertag.lower(), amount, str(placed_by) if placed_by else None)
        )
        return result is not None

    def remove_bounty(self, gamertag: str) -> bool:
        """
        Remove a bounty from a player.

        Typically called when the bounty is claimed (player is killed).

        Args:
            gamertag: Target player's gamertag

        Returns:
            True if bounty was removed, False otherwise

        Example:
            >>> repo = BountyRepository()
            >>> # Player was killed, remove bounty
            >>> repo.remove_bounty("BadPlayer")
            True
        """
        query = "DELETE FROM bounties WHERE victim_gamertag = ?"
        result = self.execute_query(query, (gamertag.lower(),))
        return result is not None

    def get_top_bounties(self, limit: int = 10) -> list[dict]:
        """
        Get the highest bounties.

        Args:
            limit: Maximum number of bounties to return (default: 10)

        Returns:
            List of top bounty dictionaries

        Example:
            >>> repo = BountyRepository()
            >>> top_bounties = repo.get_top_bounties(5)
            >>> for i, bounty in enumerate(top_bounties, 1):
            ...     print(f"{i}. {bounty['victim_gamertag']}: ${bounty['amount']}")
        """
        query = "SELECT * FROM bounties ORDER BY amount DESC LIMIT ?"
        rows = self.execute_query(query, (limit,))
        return [dict(row) for row in rows] if rows else []

    def get_total_bounty_pool(self) -> int:
        """
        Get the total amount of all active bounties.

        Returns:
            Total bounty amount across all players

        Example:
            >>> repo = BountyRepository()
            >>> total = repo.get_total_bounty_pool()
            >>> print(f"Total bounty pool: ${total}")
        """
        query = "SELECT SUM(amount) as total FROM bounties"
        rows = self.execute_query(query)
        return rows[0]["total"] if rows and rows[0]["total"] else 0
