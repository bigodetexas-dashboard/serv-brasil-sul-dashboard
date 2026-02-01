import sqlite3
import os

# Point to the unified database in the parent directory
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def init_security_db():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 1. Player Identities (Gamertag + Xbox ID + Last IP)
        print("Creating table 'player_identities'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS player_identities (
                gamertag TEXT PRIMARY KEY,
                xbox_id TEXT,
                last_ip TEXT,
                last_port INTEGER,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Index on Xbox ID for fast lookup of alts
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pi_xbox_id ON player_identities(xbox_id)")
        # Index on IP for fast lookup of alts
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pi_last_ip ON player_identities(last_ip)")

        # 2. IP History (To track all IPs a player has ever used)
        print("Creating table 'ip_history'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ip_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gamertag TEXT,
                ip TEXT,
                port INTEGER,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(gamertag, ip)
            )
        """)

        # 3. Security Bans (The Master Blacklist)
        print("Creating table 'security_bans'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS security_bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT,  -- Can be Xbox ID or IP
                type TEXT,        -- 'xbox_id' or 'ip'
                reason TEXT,
                banned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                banned_by TEXT DEFAULT 'System',
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(identifier, type)
            )
        """)

        # 4. WAF Logs (Persistent Attack History)
        print("Creating table 'waf_logs'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS waf_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                payload TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_waf_ip ON waf_logs(ip)")

        conn.commit()
        print("[OK] Security tables created successfully!")

    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    init_security_db()
