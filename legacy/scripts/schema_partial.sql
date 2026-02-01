-- ============================================
-- SCHEMA PARCIAL - Apenas tabelas que faltam
-- NÃO modifica achievements existente
-- ============================================

-- Tabela de Histórico de Atividades (NOVA)
CREATE TABLE IF NOT EXISTS activity_history (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- kill, death, login, logout, achievement, trade, purchase
    icon VARCHAR(10),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    details JSONB, -- Detalhes específicos do evento
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Configurações do Usuário (NOVA)
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    -- Perfil
    display_name VARCHAR(100),
    bio TEXT,
    discord_username VARCHAR(100),
    -- Aparência
    dark_mode BOOLEAN DEFAULT TRUE,
    primary_color VARCHAR(7) DEFAULT '#4facfe',
    font_size VARCHAR(20) DEFAULT 'medium', -- small, medium, large
    animations_enabled BOOLEAN DEFAULT TRUE,
    -- Notificações
    notify_kills BOOLEAN DEFAULT TRUE,
    notify_achievements BOOLEAN DEFAULT TRUE,
    notify_events BOOLEAN DEFAULT TRUE,
    notify_group_messages BOOLEAN DEFAULT TRUE,
    notify_weekly_summary BOOLEAN DEFAULT FALSE,
    notify_server_updates BOOLEAN DEFAULT TRUE,
    -- Privacidade
    profile_public BOOLEAN DEFAULT TRUE,
    show_stats BOOLEAN DEFAULT TRUE,
    show_history BOOLEAN DEFAULT FALSE,
    show_online_status BOOLEAN DEFAULT TRUE,
    -- Jogo
    favorite_server VARCHAR(50) DEFAULT 'BRASIL SUL #1',
    auto_join BOOLEAN DEFAULT FALSE,
    crosshair_type VARCHAR(20) DEFAULT 'cruz',
    -- Segurança
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_activity_history_discord ON activity_history(discord_id);
CREATE INDEX IF NOT EXISTS idx_activity_history_type ON activity_history(event_type);
CREATE INDEX IF NOT EXISTS idx_activity_history_timestamp ON activity_history(timestamp DESC);

-- ============================================
-- FUNÇÕES AUXILIARES
-- ============================================

-- Função para adicionar evento ao histórico
CREATE OR REPLACE FUNCTION add_activity_event(
    p_discord_id VARCHAR(50),
    p_event_type VARCHAR(50),
    p_icon VARCHAR(10),
    p_title VARCHAR(200),
    p_description TEXT,
    p_details JSONB DEFAULT '{}'::JSONB
) RETURNS INTEGER AS $$
DECLARE
    v_event_id INTEGER;
BEGIN
    INSERT INTO activity_history (discord_id, event_type, icon, title, description, details)
    VALUES (p_discord_id, p_event_type, p_icon, p_title, p_description, p_details)
    RETURNING id INTO v_event_id;
    
    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE activity_history IS 'Histórico de todas as atividades dos usuários';
COMMENT ON TABLE user_settings IS 'Configurações personalizadas de cada usuário';
