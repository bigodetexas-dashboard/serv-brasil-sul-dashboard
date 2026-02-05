import sqlite3
import os
import datetime
from utils.nitrado import ban_player as nitrado_ban

# Unified DB Path
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


class IPIntelligence:
    """
    Advanced Security System for detecting alts and enforcing bans.
    Tracks relationships between: Gamertag <-> Xbox ID <-> IP Address.
    """

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def track_connection(self, gamertag, xbox_id, ip, port=None):
        """
        Logs a player connection. Updates their identity and IP history.
        """
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            # 1. Update Identity
            cur.execute(
                """
                INSERT INTO player_identities (gamertag, xbox_id, last_ip, last_port, last_seen)
                VALUES (?, ?, ?, ?, datetime('now'))
                ON CONFLICT(gamertag) DO UPDATE SET
                    xbox_id = excluded.xbox_id,
                    last_ip = excluded.last_ip,
                    last_port = excluded.last_port,
                    last_seen = datetime('now')
            """,
                (gamertag, xbox_id, ip, port),
            )

            # 2. Update IP History
            cur.execute(
                """
                INSERT INTO ip_history (gamertag, ip, port, first_seen, last_seen)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                ON CONFLICT(gamertag, ip) DO UPDATE SET
                    last_seen = datetime('now'),
                    port = excluded.port
            """,
                (gamertag, ip, port),
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"[IP INTEL] Error tracking connection: {e}")
            return False
        finally:
            conn.close()

    def is_banned_identity(self, xbox_id, ip):
        """
        Checks if the Xbox ID or IP is in the master ban list.
        Returns: (is_banned, reason)
        """
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            # Check Xbox ID
            if xbox_id:
                cur.execute(
                    "SELECT reason FROM security_bans WHERE identifier = ? AND type = 'xbox_id' AND is_active = 1",
                    (xbox_id,),
                )
                row = cur.fetchone()
                if row:
                    return True, f"Xbox ID Banned: {row[0]}"

            # Check IP
            if ip:
                cur.execute(
                    "SELECT reason FROM security_bans WHERE identifier = ? AND type = 'ip' AND is_active = 1",
                    (ip,),
                )
                row = cur.fetchone()
                if row:
                    return True, f"IP Banned: {row[0]}"

            return False, None
        finally:
            conn.close()

    def get_alts(self, gamertag, depth=2):
        """
        Finds all accounts linked to the gamertag by IP or Xbox ID.
        Uses recursive search (friends of friends) up to 'depth'.
        """
        # Simplified implementation: 1-level deep (Direct IP sharing)
        # TODO: Implement full graph traversal for deeper alt detection
        conn = self._get_conn()
        cur = conn.cursor()
        alts = set()
        try:
            # 1. Get targets IPs
            cur.execute("SELECT ip FROM ip_history WHERE gamertag = ?", (gamertag,))
            ips = [row[0] for row in cur.fetchall()]

            if not ips:
                return []

            # 2. Find everyone who used these IPs
            placeholders = ",".join("?" for _ in ips)
            cur.execute(
                f"SELECT DISTINCT gamertag FROM ip_history WHERE ip IN ({placeholders}) AND gamertag != ?",
                (*ips, gamertag),
            )

            for row in cur.fetchall():
                alts.add(row[0])

            return list(alts)
        finally:
            conn.close()

    async def ban_identity(self, gamertag, reason="Security Violation"):
        """
        EXECUTES THE NUCLEAR OPTION.
        1. Bans the Gamertag.
        2. Bans the Xbox ID.
        3. Bans the last known IP.
        4. Finds ALL alts and bans them too.
        """
        print(f"[IP INTEL] ðŸš¨ INITIATING BAN CASCADE FOR: {gamertag}")
        conn = self._get_conn()
        cur = conn.cursor()

        try:
            # 1. Get Identity Info
            cur.execute(
                "SELECT xbox_id, last_ip FROM player_identities WHERE gamertag = ?", (gamertag,)
            )
            row = cur.fetchone()

            xbox_id = row[0] if row else None
            last_ip = row[1] if row else None

            # 2. Ban Xbox ID (Reference)
            if xbox_id:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO security_bans (identifier, type, reason)
                    VALUES (?, 'xbox_id', ?)
                """,
                    (xbox_id, reason),
                )
                print(f"[IP INTEL] Blacklisted Xbox ID: {xbox_id}")

            # 3. Ban IP (Reference)
            if last_ip:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO security_bans (identifier, type, reason)
                    VALUES (?, 'ip', ?)
                """,
                    (last_ip, reason),
                )
                print(f"[IP INTEL] Blacklisted IP: {last_ip}")

            conn.commit()

            # 4. Ban Target on Nitrado
            await nitrado_ban(gamertag)

            # 5. FIND AND BAN ALTS (Cascade)
            alts = self.get_alts(gamertag)
            if alts:
                print(
                    f"[IP INTEL] âš ï¸  Found {len(alts)} linked accounts (Alts). Banning them all..."
                )
                for alt in alts:
                    print(f"[IP INTEL] ðŸ”¨ Banning Alt: {alt}")
                    await nitrado_ban(alt)

            return True, len(alts)

        except Exception as e:
            print(f"[IP INTEL] Error executing ban: {e}")
            return False, 0
        finally:
            conn.close()


# Global Instance
ip_intel = IPIntelligence()
