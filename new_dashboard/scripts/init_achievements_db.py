import sqlite3
import os

# Unified DB Path
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def init_achievements_db():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 1. Tabela Achievements
        print("Creating table 'achievements'...")
        cur.execute("""
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tabela User Achievements
        print("Creating table 'user_achievements'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                achievement_key TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                unlocked BOOLEAN DEFAULT 0,
                unlocked_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(discord_id, achievement_key),
                FOREIGN KEY (achievement_key) REFERENCES achievements(achievement_key)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ua_discord ON user_achievements(discord_id)")

        # 3. Tabela Activity History
        print("Creating table 'activity_history'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activity_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                icon TEXT,
                title TEXT NOT NULL,
                description TEXT,
                details TEXT, -- JSON stored as CSV or JSON string
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ah_discord ON activity_history(discord_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ah_type ON activity_history(event_type)")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_ah_timestamp ON activity_history(timestamp DESC)"
        )

        # 4. Tabela User Settings
        print("Creating table 'user_settings'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                -- Perfil
                display_name TEXT,
                bio TEXT,
                discord_username TEXT,
                -- Aparência
                dark_mode BOOLEAN DEFAULT 1,
                primary_color TEXT DEFAULT '#4facfe',
                font_size TEXT DEFAULT 'medium',
                animations_enabled BOOLEAN DEFAULT 1,
                -- Notificações
                notify_kills BOOLEAN DEFAULT 1,
                notify_achievements BOOLEAN DEFAULT 1,
                notify_events BOOLEAN DEFAULT 1,
                notify_group_messages BOOLEAN DEFAULT 1,
                notify_weekly_summary BOOLEAN DEFAULT 0,
                notify_server_updates BOOLEAN DEFAULT 1,
                -- Privacidade
                profile_public BOOLEAN DEFAULT 1,
                show_stats BOOLEAN DEFAULT 1,
                show_history BOOLEAN DEFAULT 0,
                show_online_status BOOLEAN DEFAULT 1,
                -- Jogo
                favorite_server TEXT DEFAULT 'BRASIL SUL #1',
                auto_join BOOLEAN DEFAULT 0,
                crosshair_type TEXT DEFAULT 'cruz',
                -- Segurança
                two_factor_enabled BOOLEAN DEFAULT 0,
                -- Timestamps
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Populate Default Achievements
        print("Populating default achievements...")
        achievements_data = [
            # Combate
            (
                "first_kill",
                "Primeiro Sangue",
                "Elimine seu primeiro jogador em combate PvP",
                "combat",
                "common",
                "bronze",
                10,
                "100 moedas",
                "⚔️",
                1,
            ),
            (
                "killer_10",
                "Assassino",
                "Elimine 10 jogadores",
                "combat",
                "common",
                "bronze",
                15,
                "150 moedas",
                "🔪",
                10,
            ),
            (
                "killer_50",
                "Caçador",
                "Elimine 50 jogadores",
                "combat",
                "rare",
                "silver",
                30,
                "300 moedas",
                "🎯",
                50,
            ),
            (
                "killer_100",
                "Lenda",
                "Elimine 100 jogadores",
                "combat",
                "epic",
                "gold",
                50,
                "500 moedas + Skin exclusiva",
                "🏆",
                100,
            ),
            (
                "killer_500",
                "Exterminador",
                "Elimine 500 jogadores",
                "combat",
                "legendary",
                "platinum",
                100,
                "1000 moedas + Título especial",
                "💀",
                500,
            ),
            (
                "headshot_50",
                "Headshot Master",
                "Consiga 50 headshots em combate",
                "combat",
                "epic",
                "gold",
                60,
                "600 moedas",
                "🎯",
                50,
            ),
            # Sobrevivencia
            (
                "survivor_24h",
                "Sobrevivente Experiente",
                "Sobreviva por 24 horas consecutivas",
                "survival",
                "rare",
                "silver",
                25,
                "250 moedas",
                "🏕️",
                24,
            ),
            (
                "survivor_7d",
                "Mestre da Sobrevivência",
                "Sobreviva por 7 dias consecutivos",
                "survival",
                "legendary",
                "platinum",
                100,
                "1000 moedas + Título especial",
                "👑",
                7,
            ),
            (
                "survivor_30d",
                "Imortal",
                "Sobreviva por 30 dias consecutivos",
                "survival",
                "mythic",
                "diamond",
                200,
                "2000 moedas + Avatar exclusivo",
                "💎",
                30,
            ),
            (
                "builder_10",
                "Construtor",
                "Construa uma base com 10 estruturas",
                "survival",
                "rare",
                "silver",
                40,
                "400 moedas",
                "🏗️",
                10,
            ),
            # Exploracao
            (
                "explorer_cities",
                "Explorador do Mapa",
                "Visite todas as cidades principais de Chernarus",
                "exploration",
                "rare",
                "silver",
                30,
                "300 moedas",
                "🗺️",
                15,
            ),
            (
                "collector_weapons",
                "Colecionador de Armas",
                "Possua todas as armas raras do jogo",
                "exploration",
                "epic",
                "gold",
                75,
                "750 moedas + Caixa de armas",
                "🎖️",
                12,
            ),
            # Social
            (
                "group_leader",
                "Líder de Grupo",
                "Forme um grupo com 5 ou mais jogadores",
                "social",
                "common",
                "bronze",
                15,
                "150 moedas",
                "👥",
                5,
            ),
            (
                "medic_50",
                "Médico de Campo",
                "Cure 50 jogadores usando itens médicos",
                "social",
                "rare",
                "silver",
                35,
                "350 moedas",
                "💊",
                50,
            ),
            # Riqueza
            (
                "rich_10k",
                "Empreendedor",
                "Acumule 10.000 DZCoins",
                "wealth",
                "common",
                "bronze",
                20,
                "200 moedas",
                "💰",
                10000,
            ),
            (
                "rich_50k",
                "Milionário",
                "Acumule 50.000 DZCoins",
                "wealth",
                "rare",
                "silver",
                50,
                "500 moedas",
                "💎",
                50000,
            ),
            (
                "rich_100k",
                "Magnata",
                "Acumule 100.000 DZCoins",
                "wealth",
                "epic",
                "gold",
                100,
                "1000 moedas + Título VIP",
                "👑",
                100000,
            ),
        ]

        cur.executemany(
            """
            INSERT INTO achievements (achievement_key, name, description, category, rarity, tier, points, reward, icon, max_progress)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(achievement_key) DO UPDATE SET
                name=excluded.name,
                description=excluded.description,
                points=excluded.points,
                reward=excluded.reward,
                max_progress=excluded.max_progress
        """,
            achievements_data,
        )

        conn.commit()
        print("[OK] Achievements DB initialized successfully!")

    except Exception as e:
        print(f"[ERROR] Failed to init DB: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    init_achievements_db()
