-- ==========================================
-- SCHEMA SQLITE - BIGODETEXAS DAYZ SERVER
-- Sistema: BASE + CLAN + BANCO SUL + PVP
-- Versão: 2.0 (SQLite Compatible)
-- ==========================================
-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
-- ==========================================
-- TABELA DE USUÁRIOS (PRINCIPAL)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT UNIQUE NOT NULL,
    discord_username TEXT NOT NULL,
    discord_avatar TEXT,
    nitrado_gamertag TEXT,
    -- Gamertag do Xbox/Nitrado
    nitrado_verified INTEGER DEFAULT 0,
    -- 0=false, 1=true (SQLite boolean)
    nitrado_verified_at TEXT,
    -- ISO8601 timestamp
    balance INTEGER DEFAULT 0,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    best_killstreak INTEGER DEFAULT 0,
    total_playtime INTEGER DEFAULT 0,
    -- Em minutos
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    last_daily_at TEXT -- Último daily claim
);
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);
CREATE INDEX IF NOT EXISTS idx_users_gamertag ON users(nitrado_gamertag);
-- ==========================================
-- TABELA DE CLÃS
-- ==========================================
CREATE TABLE IF NOT EXISTS clans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    leader_discord_id TEXT NOT NULL,
    balance INTEGER DEFAULT 0,
    -- Banco do clã
    banner_url TEXT,
    symbol_color1 TEXT DEFAULT '#8B0000',
    -- Cor 1 do símbolo (hex)
    symbol_color2 TEXT DEFAULT '#000000',
    -- Cor 2 do símbolo (hex)
    symbol_icon TEXT DEFAULT 'shield',
    -- Ícone do clã
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(leader_discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_clans_leader ON clans(leader_discord_id);
-- ==========================================
-- TABELA DE MEMBROS DO CLÃ
-- ==========================================
CREATE TABLE IF NOT EXISTS clan_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan_id INTEGER NOT NULL,
    discord_id TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    -- leader, moderator, member
    joined_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    UNIQUE(clan_id, discord_id)
);
CREATE INDEX IF NOT EXISTS idx_clan_members_clan ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_discord ON clan_members(discord_id);
-- ==========================================
-- TABELA DE CONVITES DE CLÃ
-- ==========================================
CREATE TABLE IF NOT EXISTS clan_invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan_id INTEGER NOT NULL,
    discord_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    -- pending, accepted, rejected
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    UNIQUE(clan_id, discord_id)
);
CREATE INDEX IF NOT EXISTS idx_clan_invites_discord ON clan_invites(discord_id);
CREATE INDEX IF NOT EXISTS idx_clan_invites_status ON clan_invites(status);
-- ==========================================
-- TABELA DE GUERRAS ENTRE CLÃS
-- ==========================================
CREATE TABLE IF NOT EXISTS clan_wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clan1_id INTEGER NOT NULL,
    clan2_id INTEGER NOT NULL,
    clan1_points INTEGER DEFAULT 0,
    clan2_points INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    -- active, finished, truce
    started_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,
    FOREIGN KEY(clan1_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY(clan2_id) REFERENCES clans(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_clan_wars_status ON clan_wars(status);
-- ==========================================
-- TABELA DE BASES (ALARMES)
-- ==========================================
CREATE TABLE IF NOT EXISTS bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id TEXT NOT NULL,
    -- discord_id do dono
    clan_id INTEGER,
    -- Opcional: base de clã
    name TEXT,
    coord_x REAL NOT NULL,
    coord_y REAL,
    coord_z REAL NOT NULL,
    radius REAL DEFAULT 100.0,
    -- Raio de proteção em metros
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(owner_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_bases_owner ON bases(owner_id);
CREATE INDEX IF NOT EXISTS idx_bases_clan ON bases(clan_id);
CREATE INDEX IF NOT EXISTS idx_bases_coords ON bases(coord_x, coord_z);
-- ==========================================
-- TABELA DE TRANSAÇÕES BANCÁRIAS
-- ==========================================
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_discord_id TEXT,
    -- NULL para sistema
    to_discord_id TEXT,
    -- NULL para sistema
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    -- transfer, deposit, withdrawal, reward, purchase
    description TEXT,
    clan_id INTEGER,
    -- Se for transação do clã
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(from_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL,
        FOREIGN KEY(to_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL,
        FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_transactions_from ON transactions(from_discord_id);
CREATE INDEX IF NOT EXISTS idx_transactions_to ON transactions(to_discord_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at);
-- ==========================================
-- TABELA DE ITENS DA LOJA
-- ==========================================
CREATE TABLE IF NOT EXISTS shop_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_key TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    -- weapons, vehicles, supplies, etc
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    -- 0=inactive, 1=active
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_shop_items_category ON shop_items(category);
CREATE INDEX IF NOT EXISTS idx_shop_items_active ON shop_items(is_active);
-- ==========================================
-- TABELA DE INVENTÁRIO DE USUÁRIOS
-- ==========================================
CREATE TABLE IF NOT EXISTS user_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    discord_id TEXT NOT NULL,
    item_key TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    added_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    FOREIGN KEY(item_key) REFERENCES shop_items(item_key) ON DELETE CASCADE,
    UNIQUE(user_id, item_key)
);
CREATE INDEX IF NOT EXISTS idx_user_items_discord ON user_items(discord_id);
-- ==========================================
-- TABELA DE FAVORITOS
-- ==========================================
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    item_key TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    FOREIGN KEY(item_key) REFERENCES shop_items(item_key) ON DELETE CASCADE,
    UNIQUE(discord_id, item_key)
);
CREATE INDEX IF NOT EXISTS idx_user_favorites_discord ON user_favorites(discord_id);
-- ==========================================
-- TABELA DE PVP KILLS (HEATMAP)
-- ==========================================
CREATE TABLE IF NOT EXISTS pvp_kills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    killer_name TEXT NOT NULL,
    victim_name TEXT NOT NULL,
    weapon TEXT,
    distance REAL,
    game_x REAL,
    game_y REAL,
    game_z REAL,
    timestamp TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pvp_timestamp ON pvp_kills(timestamp);
CREATE INDEX IF NOT EXISTS idx_pvp_coords ON pvp_kills(game_x, game_z);
CREATE INDEX IF NOT EXISTS idx_pvp_killer ON pvp_kills(killer_name);
CREATE INDEX IF NOT EXISTS idx_pvp_victim ON pvp_kills(victim_name);
-- ==========================================
-- TABELA DE BOUNTIES (RECOMPENSAS)
-- ==========================================
CREATE TABLE IF NOT EXISTS bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    victim_gamertag TEXT UNIQUE NOT NULL,
    amount INTEGER DEFAULT 0,
    placed_by_discord_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(placed_by_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_bounties_gamertag ON bounties(victim_gamertag);
CREATE INDEX IF NOT EXISTS idx_bounties_amount ON bounties(amount DESC);
-- ==========================================
-- TABELA DE CONQUISTAS (ACHIEVEMENTS)
-- ==========================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    achievement_id TEXT NOT NULL,
    unlocked_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id, achievement_id)
);
CREATE INDEX IF NOT EXISTS idx_user_achievements_discord ON user_achievements(discord_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_id ON user_achievements(achievement_id);
-- ==========================================
-- TRIGGERS PARA UPDATED_AT
-- ==========================================
-- Trigger para users
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER
UPDATE ON users BEGIN
UPDATE users
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- Trigger para clans
CREATE TRIGGER IF NOT EXISTS update_clans_timestamp
AFTER
UPDATE ON clans BEGIN
UPDATE clans
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- Trigger para bases
CREATE TRIGGER IF NOT EXISTS update_bases_timestamp
AFTER
UPDATE ON bases BEGIN
UPDATE bases
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- Trigger para bounties
CREATE TRIGGER IF NOT EXISTS update_bounties_timestamp
AFTER
UPDATE ON bounties BEGIN
UPDATE bounties
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- ==========================================
-- VIEWS ÚTEIS
-- ==========================================
-- View de estatísticas de usuários
CREATE VIEW IF NOT EXISTS user_stats AS
SELECT u.discord_id,
    u.discord_username,
    u.nitrado_gamertag,
    u.balance,
    u.kills,
    u.deaths,
    CASE
        WHEN u.deaths > 0 THEN CAST(u.kills AS REAL) / u.deaths
        ELSE u.kills
    END as kd_ratio,
    u.best_killstreak,
    u.total_playtime,
    COUNT(DISTINCT ua.achievement_id) as achievements_count,
    c.name as clan_name
FROM users u
    LEFT JOIN user_achievements ua ON u.discord_id = ua.discord_id
    LEFT JOIN clan_members cm ON u.discord_id = cm.discord_id
    LEFT JOIN clans c ON cm.clan_id = c.id
GROUP BY u.discord_id;
-- View de ranking de kills
CREATE VIEW IF NOT EXISTS leaderboard_kills AS
SELECT discord_id,
    discord_username,
    nitrado_gamertag,
    kills,
    deaths,
    CASE
        WHEN deaths > 0 THEN CAST(kills AS REAL) / deaths
        ELSE kills
    END as kd_ratio
FROM users
WHERE kills > 0
ORDER BY kills DESC
LIMIT 100;
-- View de ranking de coins
CREATE VIEW IF NOT EXISTS leaderboard_coins AS
SELECT discord_id,
    discord_username,
    nitrado_gamertag,
    balance
FROM users
WHERE balance > 0
ORDER BY balance DESC
LIMIT 100;
-- ==========================================
-- FIM DO SCHEMA
-- ==========================================