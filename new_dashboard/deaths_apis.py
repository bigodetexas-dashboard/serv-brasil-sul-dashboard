# -*- coding: utf-8 -*-
"""
APIs para Deaths (Kill Feed)
Adicionar ao new_dashboard/app.py
"""

# ==================== DEATHS APIs ====================

from datetime import datetime, timezone
from utils.deaths_helper import get_location_name


@app.route("/api/deaths/recent", methods=["GET"])
def api_deaths_recent():
    """Retorna mortes recentes com paginaÃ§Ã£o"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    # Total
    cur.execute("SELECT COUNT(*) FROM deaths_log")
    total = cur.fetchone()[0] if cur.fetchone() else 0

    # Mortes recentes
    cur.execute(
        """
        SELECT
            id, killer_gamertag, victim_gamertag, death_type, death_cause,
            weapon, distance, is_headshot,
            coord_x, coord_z, location_name, occurred_at
        FROM deaths_log
        ORDER BY occurred_at DESC
        LIMIT %s OFFSET %s
    """,
        (per_page, offset),
    )

    deaths = []
    for row in cur.fetchall():
        death = {
            "id": row[0],
            "killer": row[1],
            "victim": row[2],
            "death_type": row[3],
            "death_cause": row[4],
            "weapon": row[5],
            "distance": row[6],
            "is_headshot": row[7],
            "coords": [row[8], row[9]],
            "location": row[10],
            "timestamp": row[11].isoformat() if row[11] else None,
            "time_ago": get_time_ago(row[11]) if row[11] else "Desconhecido",
        }
        deaths.append(death)

    cur.close()
    conn.close()

    return jsonify(
        {"deaths": deaths, "total": total, "page": page, "per_page": per_page}
    )


@app.route("/api/deaths/stats", methods=["GET"])
def api_deaths_stats():
    """Retorna estatÃ­sticas de mortes (Ãºltimas 24h)"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Stats bÃ¡sicas
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE death_type = 'pvp') as pvp,
            COUNT(*) FILTER (WHERE death_type = 'animal') as animal,
            COUNT(*) FILTER (WHERE is_headshot = TRUE) as headshots
        FROM deaths_log
        WHERE occurred_at >= NOW() - INTERVAL '24 hours'
    """)

    stats = cur.fetchone()

    # Arma mais usada
    cur.execute("""
        SELECT weapon, COUNT(*) as count
        FROM deaths_log
        WHERE death_type = 'pvp' AND occurred_at >= NOW() - INTERVAL '24 hours'
        GROUP BY weapon
        ORDER BY count DESC
        LIMIT 1
    """)
    most_weapon = cur.fetchone()

    # Local mais mortal
    cur.execute("""
        SELECT location_name, COUNT(*) as count
        FROM deaths_log
        WHERE occurred_at >= NOW() - INTERVAL '24 hours'
        GROUP BY location_name
        ORDER BY count DESC
        LIMIT 1
    """)
    most_location = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(
        {
            "total_deaths": stats[0] if stats else 0,
            "pvp": stats[1] if stats else 0,
            "animal": stats[2] if stats else 0,
            "headshots": stats[3] if stats else 0,
            "deaths_per_hour": round((stats[0] if stats else 0) / 24, 1),
            "most_used_weapon": most_weapon[0] if most_weapon else "N/A",
            "most_deadly_location": most_location[0] if most_location else "N/A",
        }
    )


def get_time_ago(timestamp):
    """Converte timestamp para 'hÃ¡ X minutos/horas'"""
    if not timestamp:
        return "Desconhecido"

    now = datetime.now(timezone.utc)
    diff = now - timestamp.replace(tzinfo=timezone.utc)
    seconds = diff.total_seconds()

    if seconds < 60:
        return "hÃ¡ poucos segundos"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"hÃ¡ {minutes} min"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"hÃ¡ {hours}h"
    else:
        days = int(seconds / 86400)
        return f"hÃ¡ {days}d"
