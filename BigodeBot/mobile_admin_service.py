"""
Mobile admin service for BigodeBot.
Provides REST API endpoints for mobile admin panel.
"""

import os
import json
from functools import wraps
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Mobile Admin Console - Independent Service
app = Flask(__name__)
# SECURITY: Enable ProxyFix for Cloudflare/Nginx proxy support
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = secrets.token_hex(24)

# Configuration Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "server_config.json")
LOGIN_TOKEN = "elite_admin_2026"  # Security Token


def require_api_key(f):
    """Decorator to require valid API key for endpoint access."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_authed"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


@app.route("/api/admin/status")
@require_api_key
def admin_status():
    """Get admin panel status."""
    config = load_config()
    return render_template("mobile_admin.html", config=config)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        token = request.form.get("token")
        if token == LOGIN_TOKEN:
            session["admin_authed"] = True
            return redirect(url_for("admin_status"))
    return """
        <style>
            body { background: #050505; color: #d4af37; font-family: "Impact"; text-align: center; padding-top: 100px; }
            input { background: #111; border: 1px solid #d4af37; color: white; padding: 10px; border-radius: 5px; }
            button { background: #d4af37; color: black; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; }
        </style>
        <h2>TACTICAL LOGIN</h2>
        <form method="post">
            <input type="password" name="token" placeholder="ADMIN TOKEN" autofocus>
            <button type="submit">ACCESS</button>
        </form>
    """


@app.route("/api/control", methods=["POST"])
@require_api_key
def control():
    data = request.json
    action = data.get("action")
    config = load_config()

    if action == "toggle_raid":
        config["raid_active"] = not config.get("raid_active", False)
        save_config(config)
        return jsonify({"status": "ok", "raid_active": config["raid_active"]})

    return jsonify({"status": "unknown"})


@app.route("/logout")
def logout():
    session.pop("admin_authed", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Running on a separate port for total isolation
    # SECURITY: Debug mode disabled in production
    # Set FLASK_DEBUG=1 environment variable for development debugging
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    # nosec B104 - Binding to 0.0.0.0 is intentional for remote access, secured with LOGIN_TOKEN
    app.run(host="0.0.0.0", port=5555, debug=debug_mode)  # nosec B104
