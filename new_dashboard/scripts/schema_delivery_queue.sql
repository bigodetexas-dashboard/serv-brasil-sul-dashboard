-- ============================================
-- DELIVERY QUEUE SCHEMA
-- Sistema de Fila Assíncrona para Entregas
-- ============================================
-- Tabela principal de fila de entregas
CREATE TABLE IF NOT EXISTS delivery_queue (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL,
    -- Item details
    item_name VARCHAR(100) NOT NULL,
    item_code VARCHAR(100) NOT NULL,
    -- DayZ class name
    quantity INTEGER DEFAULT 1,
    -- Delivery location
    coordinates VARCHAR(100),
    -- "X Y Z" format
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',
    -- pending, processing, delivered, failed
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 5,
    -- Error handling
    last_error TEXT,
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_started_at TIMESTAMP,
    processed_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    -- Metadata
    purchase_id INTEGER,
    -- Link to transaction if exists
    priority INTEGER DEFAULT 0,
    -- Higher = process first
    FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
);
-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_delivery_status ON delivery_queue(status);
CREATE INDEX IF NOT EXISTS idx_delivery_discord ON delivery_queue(discord_id);
CREATE INDEX IF NOT EXISTS idx_delivery_next_retry ON delivery_queue(next_retry_at)
WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_delivery_created ON delivery_queue(created_at DESC);
-- View for pending deliveries ready to process
CREATE OR REPLACE VIEW v_deliveries_ready AS
SELECT *
FROM delivery_queue
WHERE status = 'pending'
    AND attempts < max_attempts
    AND (
        next_retry_at IS NULL
        OR next_retry_at <= CURRENT_TIMESTAMP
    )
ORDER BY priority DESC,
    created_at ASC;
-- View for user delivery history
CREATE OR REPLACE VIEW v_user_delivery_history AS
SELECT dq.id,
    dq.discord_id,
    u.discord_username,
    dq.item_name,
    dq.quantity,
    dq.status,
    dq.attempts,
    dq.created_at,
    dq.processed_at,
    CASE
        WHEN dq.status = 'delivered' THEN 'Entregue'
        WHEN dq.status = 'processing' THEN 'Processando...'
        WHEN dq.status = 'pending' THEN 'Aguardando'
        WHEN dq.status = 'failed' THEN 'Falhou'
    END as status_pt
FROM delivery_queue dq
    JOIN users u ON dq.discord_id = u.discord_id
ORDER BY dq.created_at DESC;
-- Function to calculate next retry time with exponential backoff
CREATE OR REPLACE FUNCTION calculate_next_retry(attempt_count INTEGER) RETURNS TIMESTAMP AS $$ BEGIN -- Exponential backoff: 1min, 2min, 4min, 8min, 16min
    RETURN CURRENT_TIMESTAMP + (POWER(2, attempt_count) || ' minutes')::INTERVAL;
END;
$$ LANGUAGE plpgsql;
-- Function to add item to delivery queue
CREATE OR REPLACE FUNCTION queue_delivery(
        p_discord_id VARCHAR(50),
        p_item_name VARCHAR(100),
        p_item_code VARCHAR(100),
        p_quantity INTEGER DEFAULT 1,
        p_coordinates VARCHAR(100) DEFAULT NULL,
        p_purchase_id INTEGER DEFAULT NULL
    ) RETURNS INTEGER AS $$
DECLARE v_delivery_id INTEGER;
BEGIN
INSERT INTO delivery_queue (
        discord_id,
        item_name,
        item_code,
        quantity,
        coordinates,
        purchase_id,
        status
    )
VALUES (
        p_discord_id,
        p_item_name,
        p_item_code,
        p_quantity,
        p_coordinates,
        p_purchase_id,
        'pending'
    )
RETURNING id INTO v_delivery_id;
RETURN v_delivery_id;
END;
$$ LANGUAGE plpgsql;
-- Function to mark delivery as processing
CREATE OR REPLACE FUNCTION start_delivery_processing(p_delivery_id INTEGER) RETURNS BOOLEAN AS $$ BEGIN
UPDATE delivery_queue
SET status = 'processing',
    processing_started_at = CURRENT_TIMESTAMP,
    attempts = attempts + 1
WHERE id = p_delivery_id
    AND status = 'pending';
RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
-- Function to mark delivery as successful
CREATE OR REPLACE FUNCTION mark_delivery_success(p_delivery_id INTEGER) RETURNS BOOLEAN AS $$ BEGIN
UPDATE delivery_queue
SET status = 'delivered',
    processed_at = CURRENT_TIMESTAMP,
    last_error = NULL
WHERE id = p_delivery_id;
RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
-- Function to mark delivery as failed with retry
CREATE OR REPLACE FUNCTION mark_delivery_failed(
        p_delivery_id INTEGER,
        p_error_message TEXT
    ) RETURNS BOOLEAN AS $$
DECLARE v_attempts INTEGER;
v_max_attempts INTEGER;
BEGIN -- Get current attempts
SELECT attempts,
    max_attempts INTO v_attempts,
    v_max_attempts
FROM delivery_queue
WHERE id = p_delivery_id;
-- If max attempts reached, mark as permanently failed
IF v_attempts >= v_max_attempts THEN
UPDATE delivery_queue
SET status = 'failed',
    processed_at = CURRENT_TIMESTAMP,
    last_error = p_error_message
WHERE id = p_delivery_id;
ELSE -- Schedule retry with exponential backoff
UPDATE delivery_queue
SET status = 'pending',
    last_error = p_error_message,
    next_retry_at = calculate_next_retry(v_attempts)
WHERE id = p_delivery_id;
END IF;
RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE delivery_queue IS 'Fila assíncrona de entregas de itens para proteção contra falhas de FTP';
COMMENT ON FUNCTION queue_delivery IS 'Adiciona um item à fila de entrega';
COMMENT ON FUNCTION mark_delivery_failed IS 'Marca entrega como falha e agenda retry com backoff exponencial';