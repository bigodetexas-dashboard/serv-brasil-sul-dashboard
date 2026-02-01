from repositories.base_repository import BaseRepository
import sqlite3


class MuralRepository(BaseRepository):
    """
    Repository for managing Mural da Vergonha (Hall of Shame).
    Handles banning logic and retrieving banned players.
    """

    def get_active_bans(self):
        """Get all currently banned players."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT discord_id, discord_username, nitrado_gamertag,
                           ban_reason, banned_at, banned_by
                    FROM users
                    WHERE is_banned = 1
                    ORDER BY banned_at DESC
                    """
                )
                return [dict(row) for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Bans: {e}")
            finally:
                conn.close()
        return []

    def ban_player(self, discord_id, reason, admin_name="System"):
        """Ban a player and record it in the Mural."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE users
                    SET is_banned = 1,
                        ban_reason = ?,
                        banned_at = datetime('now'),
                        banned_by = ?
                    WHERE discord_id = ?
                    """,
                    (reason, admin_name, discord_id),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Ban Player: {e}")
            finally:
                conn.close()
        return False

    def unban_player(self, discord_id):
        """Unban a player."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE users
                    SET is_banned = 0,
                        ban_reason = NULL,
                        banned_at = NULL,
                        banned_by = NULL
                    WHERE discord_id = ?
                    """,
                    (discord_id,),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Unban Player: {e}")
            finally:
                conn.close()
        return False

    def get_mural_stats(self):
        """Get statistics for the Mural."""
        conn = self.get_conn()
        stats = {"total_banned": 0, "recent_bans": 0, "by_category": []}
        if conn:
            try:
                cur = conn.cursor()
                # Total Banned
                cur.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
                row = cur.fetchone()
                stats["total_banned"] = row[0] if row else 0

                # Recent Bans (last 7 days)
                cur.execute(
                    "SELECT COUNT(*) FROM users WHERE is_banned = 1 AND banned_at > date('now', '-7 days')"
                )
                row = cur.fetchone()
                stats["recent_bans"] = row[0] if row else 0

                # By Category
                cur.execute(
                    "SELECT ban_reason, COUNT(*) FROM users WHERE is_banned = 1 GROUP BY ban_reason"
                )
                rows = cur.fetchall()
                stats["by_category"] = [
                    {"category": row[0] if row[0] else "Sem motivo", "count": row[1]}
                    for row in rows
                ]

            except sqlite3.Error as e:
                print(f"[ERROR] DB Mural Stats: {e}")
            finally:
                conn.close()
        return stats
