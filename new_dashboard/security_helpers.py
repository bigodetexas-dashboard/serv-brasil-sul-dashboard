import sqlite3
import os
import re

# Unified DB Path
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def log_attack_to_db(ip, attack_type, payload):
    """Logs WAF violation to SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO waf_logs (ip, attack_type, payload, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (ip, attack_type, payload),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WAF LOG_ERROR] Failed to log attack: {e}")


class IPMiddleware:
    def __init__(self):
        self.cached_blacklist = set()
        self.load_blacklist()

    def load_blacklist(self):
        """Loads active bans from DB."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT identifier FROM security_bans WHERE is_active = 1 AND type = 'ip'")
            rows = cur.fetchall()
            self.cached_blacklist = {row[0] for row in rows}
            conn.close()
            print(f"[SECURITY] Loaded {len(self.cached_blacklist)} banned IPs from DB.")
        except Exception as e:
            print(f"[SECURITY ERROR] Failed to load blacklist: {e}")

    def is_blacklisted(self, ip):
        return ip in self.cached_blacklist

    def record_violation(self, ip, attack_type="Generic Violation"):
        """Records violation and checks if auto-ban is needed."""
        print(f"Violation recorded for {ip}: {attack_type}")
        log_attack_to_db(ip, attack_type, "Automated Detection")

        # Check if we should auto-ban (e.g., > 10 violations)
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM waf_logs WHERE ip = ?", (ip,))
            count = cur.fetchone()[0]
            if count >= 10:
                self.add(ip, reason=f"Auto-ban: {count} WAF violations recorded.")
            conn.close()
        except Exception as e:
            print(f"[SECURITY ERROR] Auto-ban check failed: {e}")

    def add(self, ip, reason="Manual Block"):
        """Adds IP to blacklist persistently."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO security_bans (identifier, type, reason) VALUES (?, 'ip', ?)",
                (ip, reason),
            )
            conn.commit()
            conn.close()
            self.cached_blacklist.add(ip)
            print(f"[SECURITY] IP {ip} blacklisted persistently: {reason}")
        except Exception as e:
            print(f"[SECURITY ERROR] Failed to blacklist IP: {e}")


class WAF:
    def detect_attack(self, value):
        # Professional-grade Regex patterns for detection
        dangerous_patterns = [
            # SQL Injection (Improved)
            (
                r"(?i)(union|select|insert|update|delete|drop|alter|truncate|exec)\s+",
                "SQL Injection Attempt",
            ),
            (r"(?i)OR\s+.+?=.+", "SQLi Condition Bypass"),
            (r"--", "SQL Comment Probe"),
            # XSS (Improved)
            (r"(?i)<script.*?>", "Cross-Site Scripting (XSS)"),
            (r"(?i)javascript:", "JS Protocol Injection"),
            (r"(?i)onerror\s*=", "XSS Event Handler"),
            (r"(?i)alert\(", "XSS Execution Probe"),
            # Path Traversal & File Access
            (r"\.\./", "Path Traversal Attempt"),
            (r"(?i)/etc/passwd", "System File Access Probe"),
            (r"(?i)C:\\Windows", "Windows System Access Probe"),
            # Shell/Command Injection
            (r"(?i)(cmd\.exe|powershell|/bin/sh|/bin/bash)", "Command Injection Attempt"),
            (r"\|\s*(nc|bash|sh|php|python|perl)", "Reverse Shell Attempt"),
        ]

        for pattern, attack_type in dangerous_patterns:
            if re.search(pattern, value):
                return True, attack_type

        return False, None


ip_blacklist = IPMiddleware()
waf = WAF()
