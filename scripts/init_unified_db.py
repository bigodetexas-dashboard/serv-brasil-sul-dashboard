import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def init_db():
    print(f"Initializing database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE NOT NULL,
        discord_username TEXT,
        discord_avatar TEXT,
        discord_email TEXT,
        nitrado_gamertag TEXT,
        nitrado_verified INTEGER DEFAULT 0,
        balance INTEGER DEFAULT 0,
        twofa_enabled INTEGER DEFAULT 0,
        twofa_otp_code TEXT,
        twofa_otp_expires INTEGER,
        twofa_last_code_sent INTEGER,
        twofa_backup_codes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Events Table (for Heatmap)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        game_x REAL,
        game_y REAL,
        game_z REAL,
        weapon TEXT,
        killer_name TEXT,
        victim_name TEXT,
        distance REAL,
        timestamp DATETIME
    )
    """)

    # Achievements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        achievement_key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        rarity TEXT,
        tier TEXT,
        points INTEGER DEFAULT 0,
        reward TEXT,
        icon TEXT,
        max_progress INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # User Achievements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT NOT NULL,
        achievement_key TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        unlocked INTEGER DEFAULT 0,
        unlocked_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(discord_id, achievement_key),
        FOREIGN KEY (achievement_key) REFERENCES achievements(achievement_key)
    )
    """)

    # Activity History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        icon TEXT,
        title TEXT NOT NULL,
        description TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
