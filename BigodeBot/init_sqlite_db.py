import sqlite3

DB_FILE = "bigode_unified.db"


def init_sqlite_db():
    print(f"Initializing SQLite DB: {DB_FILE}...")

    conn = sqlite3.connect(DB_FILE)
    # Enable WAL mode for concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    cur = conn.cursor()

    # 1. Users Table (Unified)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE NOT NULL,
        discord_username TEXT,
        nitrado_gamertag TEXT,
        balance INTEGER DEFAULT 0,
        kills INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0,
        best_killstreak INTEGER DEFAULT 0,
        total_playtime INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_daily_at TIMESTAMP
    )
    """
    )

    # 2. Inventory (User Items)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS user_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        discord_id TEXT NOT NULL,
        item_key TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, item_key)
    )
    """
    )

    # 3. Clans
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS clans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        leader_discord_id TEXT NOT NULL,
        balance INTEGER DEFAULT 0,
        banner_url TEXT,
        symbol_color1 TEXT DEFAULT '#8B0000',
        symbol_color2 TEXT DEFAULT '#000000',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # 4. Clan Members
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS clan_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clan_id INTEGER NOT NULL,
        discord_id TEXT NOT NULL,
        role TEXT DEFAULT 'member',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
        UNIQUE(clan_id, discord_id)
    )
    """
    )

    # 5. Transactions
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT NOT NULL,
        type TEXT NOT NULL,
        amount INTEGER NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # 6. Links (Optional, but if we want to store legacy links separately or just put in users)
    # We put in users, but for compatibility let's keep a table or just migrate to users.nitrado_gamertag
    # Let's keep a separate one if multiple gamertags allowed, but for now 1-to-1 -> Users table is best.

    # 7. User Favorites
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT NOT NULL,
        item_key TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(discord_id, item_key)
    )
    """
    )

    # 8. Bases (Alarms)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS bases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id TEXT NOT NULL,
        name TEXT,
        x REAL NOT NULL,
        y REAL,
        z REAL NOT NULL,
        radius REAL DEFAULT 100.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # 8. Shop Items
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS shop_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_key TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        description TEXT,
        is_active INTEGER DEFAULT 1
    )
    """
    )

    # 9. PvP Kills (Heatmap)
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS pvp_kills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        killer_name TEXT NOT NULL,
        victim_name TEXT NOT NULL,
        weapon TEXT,
        distance REAL,
        game_x REAL,
        game_y REAL,
        game_z REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pvp_timestamp ON pvp_kills(timestamp)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_pvp_coords ON pvp_kills(game_x, game_z)"
    )

    # 10. Bounties Table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS bounties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_gamertag TEXT UNIQUE NOT NULL,
        amount INTEGER DEFAULT 0,
        placed_by_discord_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_bounties_gt ON bounties(victim_gamertag)"
    )

    # 11. Clan Wars Table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS clan_wars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clan1_id INTEGER NOT NULL,
        clan2_id INTEGER NOT NULL,
        clan1_points INTEGER DEFAULT 0,
        clan2_points INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active', -- active, finished, truce
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY(clan1_id) REFERENCES clans(id) ON DELETE CASCADE,
        FOREIGN KEY(clan2_id) REFERENCES clans(id) ON DELETE CASCADE
    )
    """
    )

    # 12. User Achievements
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT NOT NULL,
        achievement_id TEXT NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(discord_id, achievement_id)
    )
    """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_achievements ON user_achievements(discord_id)"
    )

    # 13. Clan Invites
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS clan_invites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clan_id INTEGER NOT NULL,
        discord_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending', -- pending, accepted, rejected
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
        UNIQUE(clan_id, discord_id)
    )
    """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_clan_invites_discord ON clan_invites(discord_id)"
    )

    conn.commit()
    conn.close()
    print("SQLite DB initialized successfully.")


if __name__ == "__main__":
    init_sqlite_db()
