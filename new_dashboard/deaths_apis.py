# -*- coding: utf-8 -*-
"""
APIs para Deaths (Kill Feed) - BigodeTexas
Refatorado para Blueprint e compatibilidade SQLite.
"""

from flask import Blueprint, request, jsonify, current_app
import sqlite3
import os
from datetime import datetime, timezone
import math

deaths_bp = Blueprint("deaths", __name__)


# --- DATABASE HELPER ---
def get_db_path():
    # Assume que o DB está na raiz do projeto (um nível acima deste arquivo se estiver em new_dashboard/)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
    )


def get_db_connection():
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[DEATHS API ERROR] Connection failed: {e}")
        return None


# ==================== DEATHS APIs ====================


@deaths_bp.route("/recent", methods=["GET"])
def api_deaths_recent():
    """Retorna mortes recentes com paginação"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    if not conn:
        return jsonify({"deaths": [], "error": "Database connection failed"}), 500

    cur = conn.cursor()

    # Total
    cur.execute("SELECT COUNT(*) FROM deaths_log")
    total = cur.fetchone()[0]

    # Mortes recentes
    cur.execute(
        """
        SELECT
            id, killer_gamertag, victim_gamertag, death_type, death_cause,
            weapon, distance, is_headshot,
            coord_x, coord_z, location_name, occurred_at
        FROM deaths_log
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """,
        (per_page, offset),
    )

    deaths = []
    for row in cur.fetchall():
        # SQLite doesn't have native datetime objects like PG, so we parse if needed
        # But occurred_at is stored as TIMESTAMP which usually returns as string or int depending on adapter
        dt_str = row["occurred_at"]
        try:
            # Try to convert to ISO for JS if it's already a string
            dt = (
                datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                if dt_str
                else None
            )
        except:
            dt = None

        death = {
            "id": row["id"],
            "killer": row["killer_gamertag"],
            "victim": row["victim_gamertag"],
            "death_type": row["death_type"],
            "death_cause": row["death_cause"],
            "weapon": row["weapon"],
            "distance": row["distance"],
            "is_headshot": bool(row["is_headshot"]),
            "coords": [row["coord_x"], row["coord_z"]],
            "location": row["location_name"],
            "timestamp": dt_str,
            "time_ago": get_time_ago(dt) if dt else "Recentemente",
        }
        deaths.append(death)

    cur.close()
    conn.close()

    return jsonify(
        {"deaths": deaths, "total": total, "page": page, "per_page": per_page}
    )


@deaths_bp.route("/stats", methods=["GET"])
def api_deaths_stats():
    """Retorna estatísticas de mortes (últimas 24h)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()

    # Stats básicas (SQLite compatível)
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN death_type = 'pvp' THEN 1 ELSE 0 END) as pvp,
            SUM(CASE WHEN death_type = 'animal' THEN 1 ELSE 0 END) as animal,
            SUM(CASE WHEN is_headshot = 1 THEN 1 ELSE 0 END) as headshots
        FROM deaths_log
        WHERE occurred_at >= datetime('now', '-24 hours')
    """)

    row = cur.fetchone()
    stats = dict(row) if row else {"total": 0, "pvp": 0, "animal": 0, "headshots": 0}

    # Arma mais usada
    cur.execute("""
        SELECT weapon, COUNT(*) as count
        FROM deaths_log
        WHERE death_type = 'pvp' AND occurred_at >= datetime('now', '-24 hours')
        GROUP BY weapon
        ORDER BY count DESC
        LIMIT 1
    """)
    most_weapon_row = cur.fetchone()
    most_weapon = most_weapon_row["weapon"] if most_weapon_row else "N/A"

    # Local mais mortal
    cur.execute("""
        SELECT location_name, COUNT(*) as count
        FROM deaths_log
        WHERE occurred_at >= datetime('now', '-24 hours')
        GROUP BY location_name
        ORDER BY count DESC
        LIMIT 1
    """)
    most_location_row = cur.fetchone()
    most_location = most_location_row["location_name"] if most_location_row else "N/A"

    cur.close()
    conn.close()

    total_deaths = stats.get("total") or 0
    return jsonify(
        {
            "total_deaths": total_deaths,
            "pvp": stats.get("pvp") or 0,
            "animal": stats.get("animal") or 0,
            "headshots": stats.get("headshots") or 0,
            "deaths_per_hour": round(total_deaths / 24, 1),
            "most_used_weapon": most_weapon,
            "most_deadly_location": most_location,
        }
    )


def get_time_ago(dt):
    """Converte datetime para 'há X minutos/horas'"""
    if not dt:
        return "Desconhecido"

    now = datetime.now(timezone.utc)
    # Ensure dt is timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 0:
        return "agora"
    if seconds < 60:
        return "há poucos segundos"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"há {minutes} min"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"há {hours}h"
    else:
        days = int(seconds / 86400)
        return f"há {days}d"
