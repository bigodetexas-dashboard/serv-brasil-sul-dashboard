"""
Clan Repository Module

Manages clan data, members, wars, and invitations in the database.
Provides comprehensive clan management functionality including:
- Clan CRUD operations
- Member management
- Clan wars system
- Invitation system
"""

from repositories.base_repository import BaseRepository


class ClanRepository(BaseRepository):
    """
    Repository for clan database operations.

    Handles all clan-related database interactions including
    clan creation, member management, wars, and invitations.
    """

    def get_clan_by_tag(self, tag: str) -> dict | None:
        """
        Fetch clan details by tag (name) from database.

        Args:
            tag: Clan name/tag (case-insensitive)

        Returns:
            Dictionary with clan info and members list, or None if not found

        Example:
            >>> repo = ClanRepository()
            >>> clan = repo.get_clan_by_tag("Warriors")
            >>> if clan:
            ...     print(f"Clan: {clan['name']}, Members: {len(clan['members'])}")
        """
        query = """
            SELECT id, name, leader_discord_id, balance, banner_url, created_at
            FROM clans
            WHERE UPPER(name) = ?
        """
        rows = self.execute_query(query, (tag.upper(),))

        if not rows:
            return None

        clan_dict = dict(rows[0])

        # Fetch members
        members_query = """
            SELECT discord_id, role, joined_at
            FROM clan_members
            WHERE clan_id = ?
        """
        members = self.execute_query(members_query, (clan_dict["id"],))
        clan_dict["members"] = [dict(m) for m in members] if members else []

        return clan_dict

    def get_user_clan(self, discord_id: str | int) -> dict | None:
        """
        Find which clan a user belongs to.

        Args:
            discord_id: Discord ID of the user

        Returns:
            Dictionary with clan info and user's role, or None if not in any clan

        Example:
            >>> repo = ClanRepository()
            >>> clan = repo.get_user_clan("123456789")
            >>> if clan:
            ...     print(f"Member of {clan['name']} as {clan['role']}")
        """
        query = """
            SELECT c.id, c.name, c.leader_discord_id, c.balance, c.banner_url, cm.role
            FROM clan_members cm
            JOIN clans c ON cm.clan_id = c.id
            WHERE cm.discord_id = ?
        """
        rows = self.execute_query(query, (str(discord_id),))
        return dict(rows[0]) if rows else None

    def create_clan(self, name: str, leader_discord_id: str | int) -> int | None:
        """
        Create a new clan and add the leader as the first member.

        Args:
            name: Clan name/tag
            leader_discord_id: Discord ID of the clan leader

        Returns:
            Clan ID if successful, None otherwise

        Example:
            >>> repo = ClanRepository()
            >>> clan_id = repo.create_clan("Warriors", "123456789")
            >>> if clan_id:
            ...     print(f"Clan created with ID: {clan_id}")
        """
        # Insert clan
        query = """
            INSERT INTO clans (name, leader_discord_id, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
        """
        clan_id = self.execute_query(query, (name, str(leader_discord_id)))

        if not clan_id:
            return None

        # Add leader as member
        member_query = """
            INSERT INTO clan_members (clan_id, discord_id, role, joined_at)
            VALUES (?, ?, 'leader', datetime('now'))
        """
        result = self.execute_query(member_query, (clan_id, str(leader_discord_id)))

        return clan_id if result else None

    def add_member(
        self, clan_id: int, discord_id: str | int, role: str = "member"
    ) -> bool:
        """
        Add a member to a clan.

        Args:
            clan_id: ID of the clan
            discord_id: Discord ID of the user to add
            role: Role in clan (default: "member", can be "leader", "moderator")

        Returns:
            True if successful, False otherwise

        Example:
            >>> repo = ClanRepository()
            >>> repo.add_member(1, "987654321", "member")
            True
        """
        query = """
            INSERT OR IGNORE INTO clan_members (clan_id, discord_id, role, joined_at)
            VALUES (?, ?, ?, datetime('now'))
        """
        result = self.execute_query(query, (clan_id, str(discord_id), role))
        return result is not None

    def remove_member(self, clan_id: int, discord_id: str | int) -> bool:
        """
        Remove a member from a clan.

        Args:
            clan_id: ID of the clan
            discord_id: Discord ID of the user to remove

        Returns:
            True if successful, False otherwise

        Example:
            >>> repo = ClanRepository()
            >>> repo.remove_member(1, "987654321")
            True
        """
        query = """
            DELETE FROM clan_members
            WHERE clan_id = ? AND discord_id = ?
        """
        result = self.execute_query(query, (clan_id, str(discord_id)))
        return result is not None

    def update_balance(self, clan_id: int, amount: int) -> bool:
        """
        Update clan bank balance.

        Args:
            clan_id: ID of the clan
            amount: Amount to add (can be negative to subtract)

        Returns:
            True if successful, False otherwise

        Example:
            >>> repo = ClanRepository()
            >>> repo.update_balance(1, 1000)  # Add 1000
            True
            >>> repo.update_balance(1, -500)  # Subtract 500
            True
        """
        query = """
            UPDATE clans
            SET balance = balance + ?, updated_at = datetime('now')
            WHERE id = ?
        """
        result = self.execute_query(query, (amount, clan_id))
        return result is not None

    def get_all_clans(self) -> list[dict]:
        """
        List all clans ordered by balance (richest first).

        Returns:
            List of clan dictionaries

        Example:
            >>> repo = ClanRepository()
            >>> clans = repo.get_all_clans()
            >>> for clan in clans:
            ...     print(f"{clan['name']}: ${clan['balance']}")
        """
        query = """
            SELECT id, name, leader_discord_id, balance, banner_url
            FROM clans
            ORDER BY balance DESC
        """
        rows = self.execute_query(query)
        return [dict(row) for row in rows] if rows else []

    def declare_war(
        self, clan1_id: int, clan2_id: int, duration_hours: int = 48
    ) -> int | None:
        """
        Create a war record between two clans.

        Args:
            clan1_id: ID of first clan
            clan2_id: ID of second clan
            duration_hours: War duration in hours (default: 48)

        Returns:
            War ID if successful, None otherwise
        """
        query = """
            INSERT INTO clan_wars (clan1_id, clan2_id, expires_at)
            VALUES (?, ?, datetime('now', '+' || ? || ' hours'))
        """
        return self.execute_query(query, (clan1_id, clan2_id, duration_hours))

    def get_active_war(self, clan_id: int) -> dict | None:
        """
        Find if a clan is in an active war.

        Args:
            clan_id: ID of the clan

        Returns:
            War dictionary if active war exists, None otherwise
        """
        query = """
            SELECT * FROM clan_wars
            WHERE (clan1_id = ? OR clan2_id = ?)
            AND status = 'active'
            AND (expires_at IS NULL OR expires_at > datetime('now'))
        """
        rows = self.execute_query(query, (clan_id, clan_id))
        return dict(rows[0]) if rows else None

    def add_war_points(self, war_id: int, clan_id: int, points: int) -> bool:
        """
        Add score to a clan in an active war.

        Args:
            war_id: ID of the war
            clan_id: ID of the clan to add points to
            points: Points to add

        Returns:
            True if successful, False otherwise
        """
        # Get war info
        war_query = "SELECT clan1_id, clan2_id FROM clan_wars WHERE id = ?"
        war_rows = self.execute_query(war_query, (war_id,))

        if not war_rows:
            return False

        war = dict(war_rows[0])

        # Update appropriate clan's points
        if war["clan1_id"] == clan_id:
            update_query = (
                "UPDATE clan_wars SET clan1_points = clan1_points + ? WHERE id = ?"
            )
        elif war["clan2_id"] == clan_id:
            update_query = (
                "UPDATE clan_wars SET clan2_points = clan2_points + ? WHERE id = ?"
            )
        else:
            return False

        result = self.execute_query(update_query, (points, war_id))
        return result is not None

    def end_war(self, war_id: int, status: str = "finished") -> bool:
        """
        End a war manually or by expiration.

        Args:
            war_id: ID of the war
            status: New status (default: "finished", can be "truce")

        Returns:
            True if successful, False otherwise
        """
        query = (
            "UPDATE clan_wars SET status = ?, expires_at = datetime('now') WHERE id = ?"
        )
        result = self.execute_query(query, (status, war_id))
        return result is not None

    def create_invite(self, clan_id: int, discord_id: str | int) -> bool:
        """
        Create a pending invite for a user.

        Args:
            clan_id: ID of the clan
            discord_id: Discord ID of user to invite

        Returns:
            True if successful, False otherwise
        """
        query = "INSERT INTO clan_invites (clan_id, discord_id) VALUES (?, ?)"
        result = self.execute_query(query, (clan_id, str(discord_id)))
        return result is not None

    def get_user_invites(self, discord_id: str | int) -> list[dict]:
        """
        Get all pending invites for a user.

        Args:
            discord_id: Discord ID of the user

        Returns:
            List of pending invite dictionaries with clan info
        """
        query = """
            SELECT i.*, c.name as clan_name
            FROM clan_invites i
            JOIN clans c ON i.clan_id = c.id
            WHERE i.discord_id = ? AND i.status = 'pending'
        """
        rows = self.execute_query(query, (str(discord_id),))
        return [dict(row) for row in rows] if rows else []

    def respond_invite(self, invite_id: int, accept: bool = True) -> bool:
        """
        Accept or reject a clan invite.

        Args:
            invite_id: ID of the invite
            accept: True to accept, False to reject (default: True)

        Returns:
            True if successful, False otherwise
        """
        # Get invite info
        invite_query = "SELECT * FROM clan_invites WHERE id = ?"
        invite_rows = self.execute_query(invite_query, (invite_id,))

        if not invite_rows or dict(invite_rows[0])["status"] != "pending":
            return False

        invite = dict(invite_rows[0])

        if accept:
            # Add to members
            member_query = """
                INSERT INTO clan_members (clan_id, discord_id, role)
                VALUES (?, ?, 'member')
            """
            self.execute_query(member_query, (invite["clan_id"], invite["discord_id"]))

            # Update invite status
            update_query = "UPDATE clan_invites SET status = 'accepted' WHERE id = ?"
        else:
            update_query = "UPDATE clan_invites SET status = 'rejected' WHERE id = ?"

        result = self.execute_query(update_query, (invite_id,))
        return result is not None

    def create_chat_table(self):
        """Ensure clan_chat table exists."""
        query = """
            CREATE TABLE IF NOT EXISTS clan_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER NOT NULL,
                sender_discord_id TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (clan_id) REFERENCES clans (id)
            )
        """
        self.execute_query(query)

    def get_messages(self, clan_id: int, limit: int = 50) -> list[dict]:
        """Get recent chat messages for a clan."""
        self.create_chat_table()
        query = """
            SELECT id, sender_discord_id, sender_name, content, timestamp
            FROM clan_chat
            WHERE clan_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (clan_id, limit))
        return [dict(row) for row in rows][::-1] if rows else []

    def send_message(self, clan_id: int, message_data: dict) -> bool:
        """Send a message to clan chat."""
        self.create_chat_table()
        query = """
            INSERT INTO clan_chat (clan_id, sender_discord_id, sender_name, content)
            VALUES (?, ?, ?, ?)
        """
        result = self.execute_query(
            query,
            (
                clan_id,
                str(message_data.get("sender_id")),
                message_data.get("sender_name"),
                message_data.get("content"),
            ),
        )
        return result is not None
