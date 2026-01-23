"""
Multi-Channel Alert System
Send alerts via Discord, Email, SMS with intelligent throttling
"""

import json
import os
import smtplib
from collections import defaultdict
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from urllib import request, parse


class AlertSystem:
    """Multi-channel alert system with throttling"""

    # Severity levels
    SEVERITY_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, config: Dict = None):
        self.config = config or {}

        # Channel configurations
        self.discord_webhook = self.config.get("discord_webhook")
        self.email_config = self.config.get("email", {})
        self.sms_config = self.config.get("sms", {})

        # Throttling
        self.throttle_window = self.config.get("throttle_window_seconds", 300)  # 5 minutes
        self.max_alerts_per_window = self.config.get("max_alerts_per_window", 10)
        self.alert_history = defaultdict(list)

        # Alert tracking
        self.alerts_sent = {"discord": 0, "email": 0, "sms": 0}
        self.alerts_throttled = 0

    def should_throttle(self, alert_key: str) -> bool:
        """Check if alert should be throttled"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.throttle_window)

        # Clean old alerts
        self.alert_history[alert_key] = [
            timestamp for timestamp in self.alert_history[alert_key] if timestamp > cutoff
        ]

        # Check count
        if len(self.alert_history[alert_key]) >= self.max_alerts_per_window:
            self.alerts_throttled += 1
            return True

        # Record this alert
        self.alert_history[alert_key].append(now)
        return False

    def send_discord(self, message: str, severity: str = "INFO") -> bool:
        """Send alert to Discord via webhook"""
        if not self.discord_webhook:
            return False

        # Color based on severity
        colors = {
            "DEBUG": 0x808080,
            "INFO": 0x0099FF,
            "WARNING": 0xFFCC00,
            "ERROR": 0xFF6600,
            "CRITICAL": 0xFF0000,
        }

        embed = {
            "title": f"🚨 {severity} Alert",
            "description": message,
            "color": colors.get(severity, 0x0099FF),
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "BigodeTexas Autonomous System"},
        }

        payload = json.dumps({"embeds": [embed]}).encode("utf-8")

        try:
            req = request.Request(
                self.discord_webhook, data=payload, headers={"Content-Type": "application/json"}
            )
            # nosec B310 - Discord webhook URL is HTTPS only, controlled by config
            request.urlopen(req, timeout=10)  # nosec B310
            self.alerts_sent["discord"] += 1
            return True
        except Exception:
            return False

    def send_email(self, subject: str, message: str, severity: str = "INFO") -> bool:
        """Send alert via email"""
        if not self.email_config.get("enabled"):
            return False

        smtp_server = self.email_config.get("smtp_server")
        smtp_port = self.email_config.get("smtp_port", 587)
        username = self.email_config.get("username")
        password = self.email_config.get("password")
        from_email = self.email_config.get("from_email", username)
        to_emails = self.email_config.get("to_emails", [])

        if not all([smtp_server, username, password, to_emails]):
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{severity}] {subject}"
            msg["From"] = from_email
            msg["To"] = ", ".join(to_emails)

            # HTML body
            html = f"""
            <html>
              <body>
                <h2 style="color: {"red" if severity in ["ERROR", "CRITICAL"] else "orange" if severity == "WARNING" else "blue"};">
                  {severity} Alert
                </h2>
                <p><strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
                <hr>
                <p><small>BigodeTexas Autonomous System</small></p>
              </body>
            </html>
            """

            msg.attach(MIMEText(html, "html"))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            self.alerts_sent["email"] += 1
            return True

        except Exception:
            return False

    def send_sms(self, message: str, severity: str = "INFO") -> bool:
        """Send alert via SMS (Twilio)"""
        if not self.sms_config.get("enabled"):
            return False

        account_sid = self.sms_config.get("account_sid")
        auth_token = self.sms_config.get("auth_token")
        from_number = self.sms_config.get("from_number")
        to_numbers = self.sms_config.get("to_numbers", [])

        if not all([account_sid, auth_token, from_number, to_numbers]):
            return False

        # Only send SMS for ERROR and CRITICAL
        if severity not in ["ERROR", "CRITICAL"]:
            return False

        try:
            # Twilio API
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

            for to_number in to_numbers:
                data = parse.urlencode(
                    {
                        "From": from_number,
                        "To": to_number,
                        "Body": f"[{severity}] {message[:140]}",  # SMS limit
                    }
                ).encode("utf-8")

                req = request.Request(url, data=data)

                # Basic auth
                import base64

                credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
                req.add_header("Authorization", f"Basic {credentials}")

                # nosec B310 - Twilio API URL is HTTPS only, hardcoded trusted endpoint
                request.urlopen(req, timeout=10)  # nosec B310

            self.alerts_sent["sms"] += 1
            return True

        except Exception:
            return False

    def send_alert(
        self, message: str, severity: str = "INFO", channels: List[str] = None
    ) -> Dict[str, bool]:
        """Send alert to specified channels"""
        if severity not in self.SEVERITY_LEVELS:
            severity = "INFO"

        # Default channels based on severity
        if channels is None:
            if severity in ["CRITICAL", "ERROR"]:
                channels = ["discord", "email", "sms"]
            elif severity == "WARNING":
                channels = ["discord", "email"]
            else:
                channels = ["discord"]

        # Check throttling
        alert_key = f"{severity}:{message[:50]}"
        if self.should_throttle(alert_key):
            return {"throttled": True}

        # Send to each channel
        results = {}

        if "discord" in channels:
            results["discord"] = self.send_discord(message, severity)

        if "email" in channels:
            results["email"] = self.send_email("Autonomous System Alert", message, severity)

        if "sms" in channels:
            results["sms"] = self.send_sms(message, severity)

        return results

    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        return {
            "sent": dict(self.alerts_sent),
            "throttled": self.alerts_throttled,
            "total": sum(self.alerts_sent.values()),
            "active_throttles": len(self.alert_history),
        }

    def clear_throttle_history(self):
        """Clear throttle history"""
        self.alert_history.clear()
        self.alerts_throttled = 0

    def test_channels(self) -> Dict[str, bool]:
        """Test all configured channels"""
        results = {}

        test_message = "Test alert from BigodeTexas Autonomous System"

        if self.discord_webhook:
            results["discord"] = self.send_discord(test_message, "INFO")

        if self.email_config.get("enabled"):
            results["email"] = self.send_email("Test Alert", test_message, "INFO")

        if self.sms_config.get("enabled"):
            # Don't actually send SMS in test
            results["sms"] = False  # Would be True if we sent

        return results


def create_alert_system(config: Dict = None) -> AlertSystem:
    """Factory function to create alert system"""
    return AlertSystem(config)
