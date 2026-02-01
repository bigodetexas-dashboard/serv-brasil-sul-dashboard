"""
Player Repository Module

Manages all player-related data including:
- Balance and transactions
- Gamertag linking and verification
- Player statistics (kills, deaths, K/D, streaks)
- PvP kill tracking and heatmap data
- Inventory management
- Achievements system
- Daily rewards
- Base registration

This is the largest and most comprehensive repository in the system.
"""

import sqlite3
from datetime import datetime, timedelta

from repositories.base_repository import BaseRepository


class PlayerRepository(BaseRepository):
    """
    Comprehensive player data management repository.

    Handles all player-related database operations including:
    - Economy (balance, transactions)
    - Identity (Discord ID, gamertag linking, verification)
    - Statistics (kills, deaths, K/D ratio, killstreaks, playtime)
    - PvP tracking and heatmap generation
    - Inventory and shop items
    - Achievements and rewards
    - Base registration and management

    Uses caching for frequently accessed data (balance, gamertag mappings).
    """

    def __init__(self, db_path: str | None = None) -> None:
        """
        Initialize the PlayerRepository.

        Args:
            db_path: Optional custom database path (mainly for testing)
        """
        super().__init__(db_path)
        # Caches for performance
        self._cache_balance: dict[str, int] = {}
        self._cache_discord_to_gt: dict[str, str] = {}
        self._cache_gt_to_discord: dict[str, str] = {}

    # get_conn is now inherited from BaseRepository

    def _ensure_user_exists(self, discord_id):
        discord_id = str(discord_id)
        conn = self.get_conn()
        user_db_id = None
        if conn:
            try:
                cur = conn.cursor()
                try:
                    cur.execute("SELECT id FROM users WHERE discord_id = ?", (discord_id,))
                    row = cur.fetchone()
                    if row:
                        user_db_id = row["id"]
                    else:
                        cur.execute(
                            "INSERT INTO users (discord_id, created_at) "
                            "VALUES (?, datetime('now'))",
                            (discord_id,),
                        )
                        conn.commit()
                        user_db_id = cur.lastrowid
                finally:
                    cur.close()
            except sqlite3.Error as e:
                print(f"[ERROR] DB Ensure User: {e}")
            finally:
                conn.close()
        return user_db_id

    # --- BALANCE HANDLING ---

    def get_balance(self, discord_id):
        """Get the current balance of a user."""
        discord_id = str(discord_id)
        if discord_id in self._cache_balance:
            return self._cache_balance[discord_id]

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT balance FROM users WHERE discord_id = ?", (discord_id,))
                row = cur.fetchone()
                if row:
                    balance = row["balance"]
                    self._cache_balance[discord_id] = balance
                    return balance
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Balance: {e}")
            finally:
                conn.close()
        return 0

    def update_balance(self, discord_id, amount, reason="other"):
        """Update user balance and log transaction."""
        discord_id = str(discord_id)
        current_balance = self.get_balance(discord_id)
        self._ensure_user_exists(discord_id)

        new_balance = max(0, current_balance + amount)
        self._cache_balance[discord_id] = new_balance

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET balance = ?, updated_at = datetime('now') "
                    "WHERE discord_id = ?",
                    (new_balance, discord_id),
                )
                cur.execute(
                    "INSERT INTO transactions (discord_id, type, amount, description, created_at) "
                    "VALUES (?, ?, ?, ?, datetime('now'))",
                    (discord_id, reason, amount, f"Update: {reason}"),
                )
                conn.commit()
            except sqlite3.Error as e:
                print(f"[ERROR] DB Update Balance: {e}")
                conn.rollback()
            finally:
                conn.close()
        return new_balance

    def transfer_funds(
        self, from_discord_id: str, to_discord_id: str, amount: int, reason: str = "transfer"
    ):
        """
        Atomically transfer funds between two users.
        """
        from_discord_id = str(from_discord_id)
        to_discord_id = str(to_discord_id)

        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        balance_from = self.get_balance(from_discord_id)
        if balance_from < amount:
            return False, "Saldo insuficiente."

        self._ensure_user_exists(to_discord_id)

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                # Deduct
                cur.execute(
                    "UPDATE users SET balance = balance - ?, updated_at = datetime('now') WHERE discord_id = ?",
                    (amount, from_discord_id),
                )
                # Add
                cur.execute(
                    "UPDATE users SET balance = balance + ?, updated_at = datetime('now') WHERE discord_id = ?",
                    (amount, to_discord_id),
                )
                # Logs
                cur.execute(
                    "INSERT INTO transactions (discord_id, type, amount, description) VALUES (?, ?, ?, ?)",
                    (
                        from_discord_id,
                        "transfer_out",
                        -amount,
                        f"Transferencia para {to_discord_id}: {reason}",
                    ),
                )
                cur.execute(
                    "INSERT INTO transactions (discord_id, type, amount, description) VALUES (?, ?, ?, ?)",
                    (
                        to_discord_id,
                        "transfer_in",
                        amount,
                        f"Transferencia de {from_discord_id}: {reason}",
                    ),
                )
                conn.commit()
                # Invalidate caches
                if from_discord_id in self._cache_balance:
                    del self._cache_balance[from_discord_id]
                if to_discord_id in self._cache_balance:
                    del self._cache_balance[to_discord_id]
                return True, "Transferência concluída com sucesso!"
            except sqlite3.Error as e:
                conn.rollback()
                print(f"[ERROR] DB Transfer Funds: {e}")
                return False, f"Erro no banco de dados: {e}"
            finally:
                conn.close()
        return False, "Erro ao conectar ao banco de dados."

    # --- GAMERTAG / LINKING ---

    def get_discord_id_by_gamertag(self, gamertag):
        """Retrieve Discord ID associated with a gamertag."""
        if gamertag in self._cache_gt_to_discord:
            return self._cache_gt_to_discord[gamertag]

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT discord_id FROM users WHERE nitrado_gamertag = ?",
                    (gamertag,),
                )
                row = cur.fetchone()
                if row:
                    did = row["discord_id"]
                    self._cache_gt_to_discord[gamertag] = did
                    return did
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get ID by GT: {e}")
            finally:
                conn.close()
        return None

    def set_gamertag(self, discord_id, gamertag, verified=False):
        """Link a gamertag to a Discord ID."""
        discord_id = str(discord_id)
        self._ensure_user_exists(discord_id)

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                if verified:
                    cur.execute(
                        "UPDATE users SET nitrado_gamertag = ?, nitrado_verified = 1, "
                        "nitrado_verified_at = datetime('now'), updated_at = datetime('now') "
                        "WHERE discord_id = ?",
                        (gamertag, discord_id),
                    )
                else:
                    cur.execute(
                        "UPDATE users SET nitrado_gamertag = ?, updated_at = datetime('now') WHERE discord_id = ?",
                        (gamertag, discord_id),
                    )
                conn.commit()
                self._cache_gt_to_discord[gamertag] = discord_id
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Set Gamertag: {e}")
            finally:
                conn.close()
        return False

    def set_verified(self, discord_id, verified=True):
        """Set verification status for a user."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                if verified:
                    cur.execute(
                        "UPDATE users SET nitrado_verified = 1, "
                        "nitrado_verified_at = datetime('now'), "
                        "updated_at = datetime('now') WHERE discord_id = ?",
                        (discord_id,),
                    )
                else:
                    cur.execute(
                        "UPDATE users SET nitrado_verified = 0, nitrado_verified_at = NULL, "
                        "updated_at = datetime('now') WHERE discord_id = ?",
                        (discord_id,),
                    )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Set Verified: {e}")
            finally:
                conn.close()
        return False

    def is_verified(self, discord_id):
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT nitrado_verified FROM users WHERE discord_id = ?",
                    (discord_id,),
                )
                row = cur.fetchone()
                if row:
                    return bool(row["nitrado_verified"])
            except sqlite3.Error as e:
                print(f"[ERROR] DB Is Verified: {e}")
            finally:
                conn.close()
        return False

    def remove_gamertag(self, gamertag):
        """Unlink a gamertag."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET nitrado_gamertag = NULL, updated_at = datetime('now') "
                    "WHERE nitrado_gamertag = ?",
                    (gamertag,),
                )
                conn.commit()
                if gamertag in self._cache_gt_to_discord:
                    del self._cache_gt_to_discord[gamertag]
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Remove Gamertag: {e}")
            finally:
                conn.close()
        return False

    def get_all_bases(self):
        """Retrieve all registered bases."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT owner_id, name, x, z, radius FROM bases")
                return [dict(row) for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Bases: {e}")
            finally:
                conn.close()
        return []

    def add_base(self, discord_id, x, y, z, name=None, radius=50.0):
        """Register a new base for a player."""
        # Enforce 1 base per user limit
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()

                # Check if exists
                cur.execute("SELECT id FROM bases WHERE owner_id = ?", (str(discord_id),))
                if cur.fetchone():
                    return False, "Você já possui uma base registrada."

                cur.execute(
                    "INSERT INTO bases (owner_id, x, y, z, name, radius) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(discord_id),
                        float(x),
                        float(y),
                        float(z),
                        name,
                        float(radius),
                    ),
                )
                conn.commit()
                return True, "Base registrada com sucesso!"
            except sqlite3.Error as e:
                print(f"[ERROR] DB Add Base: {e}")
                return False, str(e)
            finally:
                conn.close()
        return False, "Database error"

    def get_player_stats(self, gamertag):
        """Get stats by gamertag."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT kills, deaths, best_killstreak, balance, total_playtime "
                    "FROM users WHERE nitrado_gamertag = ?",
                    (gamertag,),
                )
                row = cur.fetchone()
                if row:
                    return dict(row)
            finally:
                conn.close()
        return None

    def get_player_stats_by_discord_id(self, discord_id):
        """Get stats by Discord ID."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT nitrado_gamertag, kills, deaths, best_killstreak, "
                    "balance, total_playtime, last_interest_at, "
                    "bio_type, bio_content, banner_url, avatar_url, show_stats, "
                    "pinned_achievements, zombie_kills, buildings_placed, "
                    "trees_cut, fish_caught, meters_traveled "
                    "FROM users WHERE discord_id = ?",
                    (discord_id,),
                )
                row = cur.fetchone()
                if row:
                    return dict(row)
            finally:
                conn.close()
        return None

    def update_profile(self, discord_id, data):
        """Update user profile customization."""
        discord_id = str(discord_id)
        allowed_fields = [
            "bio_type",
            "bio_content",
            "banner_url",
            "avatar_url",
            "show_stats",
            "pinned_achievements",
        ]

        updates = []
        params = []
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                params.append(data[field])

        if not updates:
            return False

        params.append(discord_id)
        query = f"UPDATE users SET {', '.join(updates)}, updated_at = datetime('now') WHERE discord_id = ?"

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(query, tuple(params))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Update Profile: {e}")
            finally:
                conn.close()
        return False

    # --- INTEREST & LOANS ---

    def apply_interest(self, discord_id, rate=0.01):
        """
        Calculate and apply interest based on the time since last_interest_at.
        Recommended to call this on every login.
        """
        user = self.get_player_stats_by_discord_id(discord_id)
        if not user or user["balance"] <= 0:
            return 0

        now = datetime.now()
        last_interest = user.get("last_interest_at")

        if last_interest:
            # If last interest was less than 24h ago, don't apply (or apply proportional)
            # For simplicity, let's do a daily check

            last_dt = (
                datetime.fromisoformat(last_interest)
                if isinstance(last_interest, str)
                else last_interest
            )
            if (now - last_dt) < timedelta(days=1):
                return 0

        interest_amount = int(user["balance"] * rate)
        if interest_amount > 0:
            self.update_balance(discord_id, interest_amount, reason="interest_gain")

        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET last_interest_at = ? WHERE discord_id = ?",
                    (now, str(discord_id)),
                )
                conn.commit()
            finally:
                conn.close()

        return interest_amount

    # --- BASE ADVANCED MANAGEMENT ---

    def log_base_event(self, base_id, event_type, description):
        """Log events like raids or intruder alerts."""
        query = "INSERT INTO base_logs (base_id, type, description) VALUES (?, ?, ?)"
        self.execute_query(query, (base_id, event_type, description))

    def get_base_inventory(self, base_id):
        """Retrieve virtual items stored in a base."""
        query = "SELECT item_key, quantity, updated_at FROM base_inventory WHERE base_id = ?"
        return self.execute_query(query, (base_id,))

    def update_base_inventory(self, base_id, item_key, quantity, updated_by):
        """Add or remove items from base inventory."""
        conn = self.get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, quantity FROM base_inventory WHERE base_id = ? AND item_key = ?",
                (base_id, item_key),
            )
            row = cur.fetchone()
            if row:
                new_qty = max(0, row["quantity"] + quantity)
                if new_qty == 0:
                    cur.execute("DELETE FROM base_inventory WHERE id = ?", (row["id"],))
                else:
                    cur.execute(
                        "UPDATE base_inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP, last_updated_by = ? WHERE id = ?",
                        (new_qty, updated_by, row["id"]),
                    )
            else:
                if quantity > 0:
                    cur.execute(
                        "INSERT INTO base_inventory (base_id, item_key, quantity, last_updated_by) VALUES (?, ?, ?, ?)",
                        (base_id, item_key, quantity, updated_by),
                    )
            conn.commit()
            return True
        finally:
            conn.close()
        return False

    def get_gamertag(self, discord_id):
        """Get verified gamertag for Discord ID."""
        stats = self.get_player_stats_by_discord_id(discord_id)
        if stats:
            return stats.get("nitrado_gamertag")
        return None

    def get_transactions(self, discord_id, limit=10):
        """Get recent transactions."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM transactions WHERE discord_id = ? "
                    "ORDER BY created_at DESC LIMIT ?",
                    (discord_id, limit),
                )
                return [dict(row) for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Transactions: {e}")
            finally:
                conn.close()
        return []

    # --- PLAYER STATISTICS & PVP ---

    def register_kill(self, gamertag):
        """Register a kill for a player."""
        conn = self.get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, kills FROM users WHERE nitrado_gamertag = ?", (gamertag,))
            row = cur.fetchone()
            if row:
                new_kills = row["kills"] + 1
                cur.execute(
                    "UPDATE users SET kills = ?, updated_at = datetime('now') "
                    "WHERE nitrado_gamertag = ?",
                    (new_kills, gamertag),
                )
                conn.commit()
                return {"kills": new_kills}
            else:
                did = f"LEGACY_GT:{gamertag}"
                cur.execute(
                    "INSERT INTO users (discord_id, nitrado_gamertag, kills, created_at) "
                    "VALUES (?, ?, 1, datetime('now'))",
                    (did, gamertag),
                )
                conn.commit()
                return {"kills": 1}
        except sqlite3.Error as e:
            print(f"[ERROR] DB Register Kill: {e}")
        finally:
            conn.close()
        return None

    def register_death(self, gamertag):
        """Register a death for a player."""
        conn = self.get_conn()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, deaths FROM users WHERE nitrado_gamertag = ?", (gamertag,))
            row = cur.fetchone()
            if row:
                new_deaths = row["deaths"] + 1
                cur.execute(
                    "UPDATE users SET deaths = ?, updated_at = datetime('now') "
                    "WHERE nitrado_gamertag = ?",
                    (new_deaths, gamertag),
                )
            else:
                cur.execute(
                    "INSERT INTO users (discord_id, nitrado_gamertag, deaths) VALUES (?, ?, 1)",
                    (f"LEGACY_GT:{gamertag}", gamertag),
                )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] DB Register Death: {e}")
        finally:
            conn.close()
        return False

    def update_best_streak(self, gamertag, streak):
        """Update best killstreak if higher."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET best_killstreak = ? "
                    "WHERE nitrado_gamertag = ? AND best_killstreak < ?",
                    (streak, gamertag, streak),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Update Streak: {e}")
            finally:
                conn.close()
        return False

    def record_pvp_kill(self, killer, victim, weapon, dist, x, y, z):
        """Record a PvP kill event."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO pvp_kills (killer_name, victim_name, weapon, distance,
                    game_x, game_y, game_z, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    """,
                    (killer, victim, weapon, dist, x, y, z),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Record PvP: {e}")
            finally:
                conn.close()
        return False

    def get_heatmap_points(self, limit=500):
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT game_x, game_z FROM pvp_kills ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Heatmap Data: {e}")
            finally:
                conn.close()
        return []

    # --- LEADERBOARDS ---

    def get_top_kills(self, limit=10):
        """Get leaderboard for kills."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT nitrado_gamertag, kills, deaths FROM users "
                    "WHERE nitrado_gamertag IS NOT NULL ORDER BY kills DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        return []

    def get_top_kd(self, limit=10, min_kills=5):
        """Get leaderboard for K/D ratio."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT nitrado_gamertag, kills, deaths,
                    CASE WHEN deaths = 0 THEN kills ELSE CAST(kills AS FLOAT) / deaths END as kd
                    FROM users WHERE kills >= ? ORDER BY kd DESC LIMIT ?
                    """,
                    (min_kills, limit),
                )
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        return []

    def get_top_streak(self, limit=10):
        """Get leaderboard for killstreaks."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT nitrado_gamertag, best_killstreak FROM users "
                    "WHERE best_killstreak > 0 ORDER BY best_killstreak DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        return []

    def get_top_balances(self, limit=10):
        """Get leaderboard for balance."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT discord_id, nitrado_gamertag, balance FROM users "
                    "ORDER BY balance DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        return []

    def get_top_playtime(self, limit=10):
        """Get leaderboard for playtime."""
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT nitrado_gamertag, total_playtime FROM users "
                    "WHERE total_playtime > 0 ORDER BY total_playtime DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()
        return []

    # --- INVENTORY ---

    def get_inventory(self, discord_id):
        """Retrieve user inventory."""
        discord_id = str(discord_id)
        inventory = {}
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT item_key, quantity FROM user_items WHERE discord_id = ?",
                    (discord_id,),
                )
                for row in cur.fetchall():
                    inventory[row["item_key"]] = {
                        "name": row["item_key"],
                        "count": row["quantity"],
                    }
            finally:
                conn.close()
        return inventory

    def add_to_inventory(self, discord_id, item_key, _item_name, quantity=1):
        """Add item to user inventory."""
        discord_id = str(discord_id)
        user_db_id = self._ensure_user_exists(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO user_items (user_id, discord_id, item_key, quantity, added_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(user_id, item_key)
                    DO UPDATE SET quantity = quantity + excluded.quantity
                    """,
                    (user_db_id, discord_id, item_key, quantity),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Add Inventory: {e}")
            finally:
                conn.close()
        return False

    def remove_from_inventory(self, discord_id, item_key, quantity=1):
        """Remove item from user inventory."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, quantity FROM user_items WHERE discord_id = ? AND item_key = ?",
                    (discord_id, item_key),
                )
                row = cur.fetchone()
                if row:
                    if row["quantity"] > quantity:
                        cur.execute(
                            "UPDATE user_items SET quantity = quantity - ? WHERE id = ?",
                            (quantity, row["id"]),
                        )
                    else:
                        cur.execute("DELETE FROM user_items WHERE id = ?", (row["id"],))
                    conn.commit()
                    return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Remove Inventory: {e}")
            finally:
                conn.close()
        return False

    # --- UTILS ---

    def get_unlocked_achievements(self, discord_id):
        """Get list of unlocked achievements."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT achievement_id FROM user_achievements WHERE discord_id = ?",
                    (discord_id,),
                )
                return [row["achievement_id"] for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Achievements: {e}")
            finally:
                conn.close()
        return []

    def unlock_achievement(self, discord_id, achievement_id):
        """Unlock an achievement for a user."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO user_achievements (discord_id, achievement_id, unlocked_at) "
                    "VALUES (?, ?, datetime('now'))",
                    (discord_id, achievement_id),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Unlock Achievement: {e}")
            finally:
                conn.close()
        return False

    def check_and_unlock_achievements(self, discord_id):
        """
        Check all achievements for a player and unlock them if criteria met.
        Returns a list of newly unlocked achievement definitions.
        """
        discord_id = str(discord_id)

        # 1. Get current data
        stats = self.get_player_stats_by_discord_id(discord_id)
        if not stats:
            return []

        balance = self.get_balance(discord_id)

        # 2. Get transactions for 'shopper' achievement
        transactions = []
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT type FROM transactions WHERE discord_id = ?", (discord_id,))
                transactions = [dict(row) for row in cur.fetchall()]
            finally:
                conn.close()

        # 3. Get currently unlocked
        current_unlocked = self.get_unlocked_achievements(discord_id)

        # 4. Check for new ones
        from utils.achievements import check_new_achievements

        new_achs = check_new_achievements(
            discord_id, current_unlocked, stats, balance, transactions
        )

        unlocked_defs = []
        for ach_id, ach_def in new_achs:
            if self.unlock_achievement(discord_id, ach_id):
                unlocked_defs.append(ach_def)

                # 5. Award reward if applicable
                reward_val = ach_def.get("reward_value", 0)
                if reward_val > 0:
                    self.update_balance(discord_id, reward_val, reason=f"Achievement: {ach_id}")

        return unlocked_defs

    def get_last_daily(self, discord_id):
        """Get timestamp of last daily reward."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT last_daily_at FROM users WHERE discord_id = ?",
                    (discord_id,),
                )
                row = cur.fetchone()
                if row:
                    return row["last_daily_at"]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Daily: {e}")
            finally:
                conn.close()
        return None

    def update_last_daily(self, discord_id):
        """Update last daily reward timestamp."""
        discord_id = str(discord_id)
        self._ensure_user_exists(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET last_daily_at = datetime('now') WHERE discord_id = ?",
                    (discord_id,),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Update Daily: {e}")
            finally:
                conn.close()
        return False

    def get_favorites(self, discord_id):
        """Retrieve user favorite items."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT item_key FROM user_favorites WHERE discord_id = ?",
                    (discord_id,),
                )
                return [row["item_key"] for row in cur.fetchall()]
            except sqlite3.Error as e:
                print(f"[ERROR] DB Get Favorites: {e}")
            finally:
                conn.close()
        return []

    def add_favorite(self, discord_id, item_key):
        """Add item to favorites."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO user_favorites (discord_id, item_key, created_at) "
                    "VALUES (?, ?, datetime('now'))",
                    (discord_id, item_key.lower()),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"[ERROR] DB Add Favorite: {e}")
            finally:
                conn.close()
        return False

    def remove_favorite(self, discord_id, item_key):
        """Remove item from favorites."""
        discord_id = str(discord_id)
        conn = self.get_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM user_favorites WHERE discord_id = ? AND item_key = ?",
                    (discord_id, item_key.lower()),
                )
                conn.commit()
                return True
            except Exception as e:
                print(f"[ERROR] DB Remove Favorite: {e}")
            finally:
                conn.close()
        return False
