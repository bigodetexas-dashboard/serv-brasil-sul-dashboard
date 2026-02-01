-- ==========================================
-- SCHEMA POSTGRESQL - BIGODETEXAS DAYZ SERVER
-- Sistema: BASE + CLAN + BANCO SUL + PVP
-- Versão: 2.1 (PostgreSQL Migration)
-- ==========================================
-- ==========================================
-- TABELA DE USUÁRIOS (PRINCIPAL)
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    discord_username VARCHAR(100) NOT NULL,
    discord_avatar TEXT,
    email VARCHAR(255),
    nitrado_gamertag VARCHAR(100),
    nitrado_verified BOOLEAN DEFAULT FALSE,
    nitrado_verified_at TIMESTAMP,
    balance INTEGER DEFAULT 0,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    best_killstreak INTEGER DEFAULT 0,
    total_playtime INTEGER DEFAULT 0,
    -- Em minutos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_daily_at TIMESTAMP,
    -- Premium Profile
    bio_type VARCHAR(20) DEFAULT 'auto',
    bio_content TEXT,
    banner_url TEXT,
    avatar_url TEXT,
    show_stats BOOLEAN DEFAULT TRUE,
    pinned_achievements TEXT,
    -- JSON string or proper JSONB later
    -- Playstyle Metrics
    zombie_kills INTEGER DEFAULT 0,
    buildings_placed INTEGER DEFAULT 0,
    trees_cut INTEGER DEFAULT 0,
    fish_caught INTEGER DEFAULT 0,
    meters_traveled FLOAT DEFAULT 0.0,
    -- Security
    twofa_enabled BOOLEAN DEFAULT FALSE,
    twofa_secret VARCHAR(100),
    twofa_otp_code VARCHAR(255),
    twofa_otp_expires INTEGER,
    twofa_last_code_sent INTEGER
);
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);
CREATE INDEX IF NOT EXISTS idx_users_gamertag ON users(nitrado_gamertag);
-- ==========================================
-- TABELA DE CLÃS
-- ==========================================
CREATE TABLE IF NOT EXISTS clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    leader_discord_id VARCHAR(50) NOT NULL,
    balance INTEGER DEFAULT 0,
    banner_url TEXT,
    symbol_color1 VARCHAR(20) DEFAULT '#8B0000',
    symbol_color2 VARCHAR(20) DEFAULT '#000000',
    symbol_icon VARCHAR(50) DEFAULT 'shield',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(leader_discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
);
-- ==========================================
-- TABELA DE MEMBROS DO CLÃ
-- ==========================================
CREATE TABLE IF NOT EXISTS clan_members (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER NOT NULL,
    discord_id VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    -- leader, moderator, member
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    UNIQUE(clan_id, discord_id)
);
-- ==========================================
-- TABELA DE CONVITES DE CLÃ
-- ==========================================
CREATE TABLE IF NOT EXISTS clan_invites (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER NOT NULL,
    discord_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- pending, accepted, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE,
    UNIQUE(clan_id, discord_id)
);
-- ==========================================
-- TABELA DE ITENS DA LOJA
-- ==========================================
CREATE TABLE IF NOT EXISTS shop_items (
    id SERIAL PRIMARY KEY,
    item_key VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ==========================================
-- TABELA DE TRANSAÇÕES
-- ==========================================
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    from_discord_id VARCHAR(50),
    to_discord_id VARCHAR(50),
    amount INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    -- Renamed from transaction_type to match some code usage, or alias
    description TEXT,
    clan_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(from_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL,
        FOREIGN KEY(to_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL
);
-- ==========================================
-- TABELA DE BOUNTIES
-- ==========================================
CREATE TABLE IF NOT EXISTS bounties (
    id SERIAL PRIMARY KEY,
    victim_gamertag VARCHAR(100) UNIQUE NOT NULL,
    amount INTEGER DEFAULT 0,
    placed_by_discord_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(placed_by_discord_id) REFERENCES users(discord_id) ON DELETE
    SET NULL
);
-- ==========================================
-- TABELA DE PVP KILLS (HEATMAP)
-- ==========================================
CREATE TABLE IF NOT EXISTS pvp_kills (
    id SERIAL PRIMARY KEY,
    killer_name VARCHAR(100) NOT NULL,
    victim_name VARCHAR(100) NOT NULL,
    weapon VARCHAR(100),
    distance FLOAT,
    game_x FLOAT,
    game_z FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ==========================================
-- TABELA DE SEGURANÇA
-- ==========================================
CREATE TABLE IF NOT EXISTS player_identities (
    gamertag VARCHAR(100) PRIMARY KEY,
    xbox_id VARCHAR(50),
    last_ip VARCHAR(50),
    last_port INTEGER,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ip_history (
    id SERIAL PRIMARY KEY,
    gamertag VARCHAR(100),
    ip VARCHAR(50),
    port INTEGER,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gamertag, ip)
);
CREATE TABLE IF NOT EXISTS security_bans (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(100),
    type VARCHAR(20),
    -- xbox_id, ip
    reason TEXT,
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    banned_by VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(identifier, type)
);
CREATE TABLE IF NOT EXISTS waf_logs (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(50) NOT NULL,
    attack_type VARCHAR(50) NOT NULL,
    payload TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);