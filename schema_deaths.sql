-- ==========================================
-- Schema para Sistema de Deaths (Kill Feed)
-- ==========================================
-- Tabela principal de mortes
CREATE TABLE IF NOT EXISTS deaths_log (
    id SERIAL PRIMARY KEY,
    -- Jogadores
    killer_gamertag TEXT,
    killer_discord_id TEXT,
    victim_gamertag TEXT NOT NULL,
    victim_discord_id TEXT,
    -- Tipo de morte
    death_type TEXT NOT NULL CHECK (death_type IN ('pvp', 'animal')),
    death_cause TEXT NOT NULL,
    -- 'player', 'wolf', 'bear'
    -- Detalhes PvP (apenas para death_type = 'pvp')
    weapon TEXT,
    distance REAL,
    body_part TEXT,
    is_headshot BOOLEAN DEFAULT FALSE,
    -- Localização
    coord_x REAL,
    coord_z REAL,
    coord_y REAL,
    location_name TEXT,
    -- Calculado via função helper
    -- Recompensas
    coins_gained INTEGER DEFAULT 0,
    coins_lost INTEGER DEFAULT 0,
    -- Timestamp
    occurred_at TIMESTAMP DEFAULT NOW(),
    -- Metadados
    server_id TEXT DEFAULT 'serv-brasil-sul',
    session_id TEXT
);
-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_deaths_occurred_at ON deaths_log(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_deaths_killer ON deaths_log(killer_gamertag);
CREATE INDEX IF NOT EXISTS idx_deaths_victim ON deaths_log(victim_gamertag);
CREATE INDEX IF NOT EXISTS idx_deaths_type ON deaths_log(death_type);
CREATE INDEX IF NOT EXISTS idx_deaths_location ON deaths_log(location_name);
CREATE INDEX IF NOT EXISTS idx_deaths_weapon ON deaths_log(weapon);
-- View para estatísticas rápidas (últimas 24h)
CREATE OR REPLACE VIEW deaths_stats_24h AS
SELECT COUNT(*) as total_deaths,
    COUNT(*) FILTER (
        WHERE death_type = 'pvp'
    ) as pvp_deaths,
    COUNT(*) FILTER (
        WHERE death_type = 'animal'
    ) as animal_deaths,
    COUNT(*) FILTER (
        WHERE is_headshot = TRUE
    ) as headshots,
    MAX(distance) as longest_kill_distance,
    MODE() WITHIN GROUP (
        ORDER BY weapon
    ) as most_used_weapon,
    MODE() WITHIN GROUP (
        ORDER BY location_name
    ) as deadliest_location
FROM deaths_log
WHERE occurred_at >= NOW() - INTERVAL '24 hours';
-- Comentários para documentação
COMMENT ON TABLE deaths_log IS 'Registro de todas as mortes do servidor (PvP e animais)';
COMMENT ON COLUMN deaths_log.death_type IS 'Tipo: pvp ou animal';
COMMENT ON COLUMN deaths_log.death_cause IS 'Causa: player, wolf, bear';
COMMENT ON COLUMN deaths_log.is_headshot IS 'TRUE se foi headshot (apenas PvP)';
COMMENT ON COLUMN deaths_log.location_name IS 'Nome da cidade mais próxima';