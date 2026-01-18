-- ✅ Índices de Performance para Heatmap
-- Otimiza queries de filtro por tempo, arma e coordenadas
-- Índice para filtro de timestamp (usado em todos os filtros de tempo)
CREATE INDEX IF NOT EXISTS idx_pvp_timestamp ON pvp_kills(timestamp);
-- Índice para filtro de arma
CREATE INDEX IF NOT EXISTS idx_pvp_weapon ON pvp_kills(weapon);
-- Índice composto para coordenadas (usado no clustering)
CREATE INDEX IF NOT EXISTS idx_pvp_coords ON pvp_kills(game_x, game_z);
-- Índice composto para queries combinadas (timestamp + weapon)
CREATE INDEX IF NOT EXISTS idx_pvp_composite ON pvp_kills(timestamp, weapon, game_x, game_z);
-- Índice para event_type (PvP vs PvE)
CREATE INDEX IF NOT EXISTS idx_pvp_event_type ON pvp_kills(event_type);