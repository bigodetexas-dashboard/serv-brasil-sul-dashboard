-- Migration: Adiciona campos de geolocalização ao cache de jogadores
-- Data: 2026-01-25
-- Propósito: Armazenar IP e dados de localização (País, Estado, Cidade, ISP)
-- Adicionar colunas de geolocalização
ALTER TABLE player_guid_cache
ADD COLUMN last_ip TEXT;
ALTER TABLE player_guid_cache
ADD COLUMN country TEXT;
ALTER TABLE player_guid_cache
ADD COLUMN region TEXT;
ALTER TABLE player_guid_cache
ADD COLUMN city TEXT;
ALTER TABLE player_guid_cache
ADD COLUMN isp TEXT;
ALTER TABLE player_guid_cache
ADD COLUMN latitude REAL;
ALTER TABLE player_guid_cache
ADD COLUMN longitude REAL;
-- Índice para busca por IP
CREATE INDEX IF NOT EXISTS idx_guid_cache_ip ON player_guid_cache(last_ip);
-- Índice para busca por país/região
CREATE INDEX IF NOT EXISTS idx_guid_cache_location ON player_guid_cache(country, region, city);