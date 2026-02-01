-- Security Bans Table
CREATE TABLE IF NOT EXISTS security_bans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL,
    -- IP or Discord ID
    type TEXT NOT NULL,
    -- 'ip' or 'discord'
    reason TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- WAF Logs Table
CREATE TABLE IF NOT EXISTS waf_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    attack_type TEXT,
    payload TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- Index for performance
CREATE INDEX IF NOT EXISTS idx_security_bans_identifier ON security_bans(identifier);
CREATE INDEX IF NOT EXISTS idx_waf_logs_ip ON waf_logs(ip);