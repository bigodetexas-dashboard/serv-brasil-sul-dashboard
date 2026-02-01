-- Migration: Adiciona cache de GUIDs Xbox dos jogadores
-- Data: 2026-01-25
-- Propósito: Armazenar permanentemente o mapeamento Gamertag -> GUID Xbox
CREATE TABLE IF NOT EXISTS player_guid_cache (
    gamertag TEXT PRIMARY KEY COLLATE NOCASE,
    xbox_guid TEXT NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Índice para busca rápida por GUID
CREATE INDEX IF NOT EXISTS idx_guid_cache_xbox_guid ON player_guid_cache(xbox_guid);
-- Índice para ordenação por último visto
CREATE INDEX IF NOT EXISTS idx_guid_cache_last_seen ON player_guid_cache(last_seen DESC);