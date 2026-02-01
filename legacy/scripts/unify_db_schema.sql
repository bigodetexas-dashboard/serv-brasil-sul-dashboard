-- ==========================================
-- UNIFICAÇÃO DE DADOS NO POSTGRESQL
-- Objetivo: Centralizar jogadores, economia e inventário
-- ==========================================
-- 1. Tabela Unificada de Usuários (Substitui bank_accounts, economy, players)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    discord_username VARCHAR(100),
    nitrado_gamertag VARCHAR(100),
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_daily_at TIMESTAMP
);
-- 2. Tabela de Inventário (Substitui inventory no JSON)
CREATE TABLE IF NOT EXISTS user_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    discord_id VARCHAR(50),
    -- Redundante para performance/facilidade se não usar JOIN sempre
    item_key VARCHAR(100) NOT NULL,
    quantity INTEGER DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_key)
);
-- 3. Migração de dados de tabelas antigas (se existirem)
-- Tentar migrar de bank_accounts se ela existir
DO $$ BEGIN IF EXISTS (
    SELECT
    FROM information_schema.tables
    WHERE table_name = 'bank_accounts'
) THEN
INSERT INTO users (discord_id, balance, created_at)
SELECT discord_id,
    balance,
    created_at
FROM bank_accounts ON CONFLICT (discord_id) DO
UPDATE
SET balance = EXCLUDED.balance;
END IF;
END $$;
-- Tentar migrar de economy se ela existir e for tabela (o app.py usa economy)
DO $$ BEGIN IF EXISTS (
    SELECT
    FROM information_schema.tables
    WHERE table_name = 'economy'
) THEN
INSERT INTO users (discord_id, balance)
SELECT discord_id,
    balance
FROM economy ON CONFLICT (discord_id) DO
UPDATE
SET balance = GREATEST(users.balance, EXCLUDED.balance);
-- Pega o maior saldo
END IF;
END $$;
-- 4. Tabela de Transações (Histórico)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    -- daily, purchase, transfer, admin
    amount INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_users_updated_at BEFORE
UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();