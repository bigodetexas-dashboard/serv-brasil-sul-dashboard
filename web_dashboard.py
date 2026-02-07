from flask import (
    Blueprint,
    jsonify,
    render_template,
    send_from_directory,
    request,
    url_for,
)
import sqlite3
import json
import os
import sys
from datetime import datetime

# Adicionar raiz do projeto ao sys.path para encontrar o core
# Adicionar raiz do projeto ao sys.path para encontrar o core
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from discord_oauth import login_required
import database

# Blueprint definition
# Blueprint definition
# ATENÇÃO: Redirecionando para as pastas do NOVO DASHBOARD
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
# POINTING TO NEW DASHBOARD (Gold Elite)
template_dir = os.path.join(base_dir, "new_dashboard", "templates")
static_dir = os.path.join(base_dir, "new_dashboard", "static")
DB_PATH = os.path.join(base_dir, "bigode_unified.db")

dashboard_bp = Blueprint("dashboard", __name__)


# ==================== ROTAS DE COMPATIBILIDADE (NOVO DESIGN) ====================
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/agradecimentos")
def agradecimentos():
    return render_template("agradecimentos.html")


def load_json(filename):
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
    )
    full_path = os.path.join(data_dir, filename)
    if not os.path.exists(full_path):
        # Cria arquivo vazio se não existir
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
        except:
            pass
        return {}
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# --- API ENDPOINTS ---
@dashboard_bp.route("/api/stats")
def api_stats():
    players_db = database.get_all_players()
    economy = database.get_economy(
        "all"
    )  # Passando "all" ou ajustando database.py para retornar tudo se user_id for None
    total_kills = sum(p.get("kills", 0) for p in players_db.values())
    total_deaths = sum(p.get("deaths", 0) for p in players_db.values())
    total_players = len(players_db)
    total_coins = sum(u.get("balance", 0) for u in economy.values())
    return jsonify(
        {
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "total_players": total_players,
            "total_coins": total_coins,
            "server_name": "BigodeTexas",
        }
    )


@dashboard_bp.route("/api/players")
def api_players():
    players_db = database.get_all_players()
    players_list = []
    for name, stats in players_db.items():
        kd = (
            stats["kills"]
            if stats.get("deaths", 0) == 0
            else round(stats["kills"] / stats["deaths"], 2)
        )
        players_list.append(
            {
                "name": name,
                "kills": stats.get("kills", 0),
                "deaths": stats.get("deaths", 0),
                "kd": kd,
                "killstreak": stats.get("best_killstreak", 0),
                "longest_shot": stats.get("longest_shot", 0),
            }
        )
    return jsonify(players_list)


@dashboard_bp.route("/api/leaderboard")
def api_leaderboard():
    players_db = database.get_all_players()
    # Top Kills
    top_kills = sorted(
        [(name, stats.get("kills", 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    # Top K/D
    top_kd = []
    for name, stats in players_db.items():
        if stats.get("deaths", 0) > 0:
            kd = round(stats["kills"] / stats["deaths"], 2)
            top_kd.append((name, kd))
    top_kd = sorted(top_kd, key=lambda x: x[1], reverse=True)[:10]
    # Top Killstreak
    top_streak = sorted(
        [(name, stats.get("best_killstreak", 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    # Top Longest Shot
    top_shot = sorted(
        [(name, stats.get("longest_shot", 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    return jsonify(
        {
            "kills": [{"name": n, "value": v} for n, v in top_kills],
            "kd": [{"name": n, "value": v} for n, v in top_kd],
            "killstreak": [{"name": n, "value": v} for n, v in top_streak],
            "longest_shot": [{"name": n, "value": v} for n, v in top_shot],
        }
    )


@dashboard_bp.route("/api/shop")
def api_shop():
    from repositories.item_repository import ItemRepository

    repo = ItemRepository()
    items = repo.get_all_shop_items()

    # Adaptar formato se necessário para o frontend
    shop_items = []
    for item in items:
        shop_items.append(
            {
                "code": item.get("item_key"),
                "name": item.get("name"),
                "price": item.get("price"),
                "category": item.get("category"),
                "description": item.get("description"),
                "image": item.get(
                    "image_url", "/static/img/items/default.png"
                ),  # Fallback image
            }
        )

    return jsonify(shop_items)


@dashboard_bp.route("/api/user/balance")
@login_required
def api_user_balance():
    from flask import session

    user_id = session.get("discord_user_id")

    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    economy = database.get_economy("all")
    user_data = economy.get(str(user_id), {})
    balance = user_data.get("balance", 0)

    return jsonify({"balance": balance, "user_id": user_id})


@dashboard_bp.route("/api/shop/purchase", methods=["POST"])
@login_required
def api_shop_purchase():
    from flask import session, request
    import asyncio
    from datetime import datetime, timedelta

    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    print(f"DEBUG PURCHASE: Recebido: {data}")  # DEBUG
    items = data.get("items", [])
    coordinates = data.get("coordinates", {})
    total = data.get("total", 0)

    if not items or not coordinates:
        print(
            f"DEBUG PURCHASE: Dados inválidos! Items: {items}, Coords: {coordinates}"
        )  # DEBUG
        return jsonify({"error": "Dados inválidos"}), 400

    # Verificar saldo
    economy = database.get_economy("all")
    user_data = economy.get(str(user_id), {})
    balance = user_data.get("balance", 0)

    if total > balance:
        return jsonify({"error": "Saldo insuficiente"}), 400

    # Deduzir saldo
    new_balance = balance - total
    database.update_economy(str(user_id), {"balance": new_balance})

    # Criar pedido de entrega (será processado em 5 minutos)
    delivery_time = datetime.now() + timedelta(minutes=5)

    # Salvar pedido pendente
    pending_deliveries = load_json("pending_deliveries.json")
    delivery_id = f"delivery_{user_id}_{int(datetime.now().timestamp())}"

    pending_deliveries[delivery_id] = {
        "user_id": str(user_id),
        "items": items,
        "coordinates": coordinates,
        "total": total,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "delivery_at": delivery_time.isoformat(),
    }

    # Salvar arquivo
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
    )
    full_path = os.path.join(data_dir, "pending_deliveries.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(pending_deliveries, f, indent=2, ensure_ascii=False)

    return jsonify(
        {
            "success": True,
            "coordinates": coordinates,
            "total": total,
            "newBalance": new_balance,
            "deliveryTime": "5 minutos",
            "deliveryId": delivery_id,
        }
    )


@dashboard_bp.route("/api/wars")
def api_wars():
    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()
    wars = repo.get_active_wars()

    # Formata para o frontend
    wars_list = []
    for war in wars:
        wars_list.append(
            {
                "id": war.get("id"),
                "clan1": {
                    "name": war.get("clan1_name"),
                    "points": war.get("clan1_points", 0),
                },
                "clan2": {
                    "name": war.get("clan2_name"),
                    "points": war.get("clan2_points", 0),
                },
                "expires_at": war.get("expires_at"),
            }
        )

    return jsonify(wars_list)


@dashboard_bp.route("/api/clans/list")
def api_clans_list():
    """Retorna lista simples de clãs para seleção"""
    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()
    clans = repo.get_all_clans()
    return jsonify([{"id": c["id"], "name": c["name"]} for c in clans])


@dashboard_bp.route("/api/clan/war/declare", methods=["POST"])
@login_required
def api_clan_declare_war():
    from flask import session, request
    from repositories.clan_repository import ClanRepository

    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    target_clan_id = data.get("target_clan_id")

    if not target_clan_id:
        return jsonify({"error": "Target clan required"}), 400

    repo = ClanRepository()

    # 1. Verificar se sou líder
    my_clan = repo.get_user_clan(user_id)
    if not my_clan or my_clan.get("role") != "leader":
        return jsonify({"error": "Apenas líderes podem declarar guerra!"}), 403

    # 2. Verificar se não é contra mim mesmo
    if int(my_clan["id"]) == int(target_clan_id):
        return jsonify({"error": "Você não pode declarar guerra contra si mesmo!"}), 400

    # 3. Declarar Guerra
    war_id = repo.declare_war(my_clan["id"], target_clan_id)

    if war_id:
        return jsonify({"success": True, "message": "Guerra declarada com sucesso!"})
    else:
        return jsonify({"error": "Falha ao declarar guerra"}), 500


@dashboard_bp.route("/api/heatmap")
def api_heatmap():
    points = database.get_heatmap_points()
    return jsonify(points)


@dashboard_bp.route("/api/player/<name>")
@login_required
def api_player(name):
    stats = database.get_player(name)
    if not stats:
        return jsonify({"error": "Player not found"}), 404

    economy = database.get_economy("all")  # Otimizar depois para buscar só um

    kd = (
        stats["kills"]
        if stats.get("deaths", 0) == 0
        else round(stats["kills"] / stats["deaths"], 2)
    )

    # Buscar Discord ID pelo link
    discord_id = database.get_link_by_gamertag(name)

    balance = 0
    achievements = []
    if discord_id:
        eco_data = database.get_economy(discord_id)
        if eco_data:
            balance = eco_data.get("balance", 0)
            achievements = eco_data.get("achievements", {})

    return jsonify(
        {
            "name": name,
            "kills": stats.get("kills", 0),
            "deaths": stats.get("deaths", 0),
            "kd": kd,
            "killstreak": stats.get("best_killstreak", 0),
            "longest_shot": stats.get("longest_shot", 0),
            "weapons_stats": stats.get("weapons_stats", {}),
            "balance": balance,
            "achievements": achievements,
            "first_seen": stats.get("first_seen", 0),
        }
    )


# --- PAGES ---
@dashboard_bp.route("/")
def index():
    return render_template("index.html")


@dashboard_bp.route("/mural")
def mural():
    return render_template("mural.html")


@dashboard_bp.route("/deaths")
@dashboard_bp.route("/tiro-na-lata")
def deaths_feed():
    return render_template("deaths.html")


@dashboard_bp.route("/status")
def status():
    return jsonify({"status": "online", "server": "DayZ Xbox"})


@dashboard_bp.route("/api/deaths/recent")
def api_deaths_recent():
    try:
        limit = request.args.get("per_page", 50, type=int)

        # Connect to DB (using bigode_unified.db which has deaths_log)
        conn = sqlite3.connect(DB_PATH)  # Using global DB_PATH
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # In bigode_unified.db, table is deaths_log and timestamp is occurred_at
        cursor.execute(
            "SELECT * FROM deaths_log ORDER BY occurred_at DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        deaths = []
        for row in rows:
            deaths.append(
                {
                    "id": row["id"],
                    "killer": row["killer_gamertag"],
                    "victim": row["victim_gamertag"],
                    "weapon": row["weapon"],
                    "distance": row["distance"],
                    "location": row["location_name"]
                    or f"{row['coord_x']:.0f}, {row['coord_z']:.0f}",
                    "timestamp": row["occurred_at"],
                    "death_type": row["death_type"],
                    "is_headshot": bool(row["is_headshot"]),
                    "death_cause": row["death_cause"],
                }
            )

        return jsonify({"deaths": deaths})
    except Exception as e:
        print(f"Error fetching deaths: {e}")
        return jsonify({"deaths": []}), 500


@dashboard_bp.route("/api/deaths/stats")
def api_deaths_stats():
    try:
        conn = sqlite3.connect(DB_PATH)  # Using global DB_PATH
        cursor = conn.cursor()

        # Simple stats in deaths_log
        cursor.execute("SELECT COUNT(*) FROM deaths_log")
        total_deaths = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM deaths_log WHERE death_type = 'pvp'")
        pvp_deaths = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM deaths_log WHERE is_headshot = 1")
        headshots = cursor.fetchone()[0]

        conn.close()

        return jsonify(
            {
                "total_deaths": total_deaths,
                "pvp": pvp_deaths,
                "animal": 0,  # Add animal count if needed
                "headshots": headshots,
            }
        )
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({}), 500


@login_required
def admin_panel():
    from flask import session, abort

    # Verify Admin (Simple ID check for now, can be improved)
    # user_id = session.get("discord_user_id")
    # ADMIN_IDS = ["YOUR_ADMIN_ID_HERE"]
    # if user_id not in ADMIN_IDS: abort(403)
    return render_template("admin.html")


# --- ADMIN API ENDPOINTS ---
@dashboard_bp.route("/api/admin/dashboard_stats")
@login_required
def api_admin_stats():
    players = database.get_all_players()
    bases = database.get_active_bases()
    # Mock online count for now
    return jsonify(
        {
            "total_bases": len(bases),
            "online_count": 0,
            "total_users": len(players),
            "raid_active": False,
            "build_mode": "restricted",
        }
    )


@dashboard_bp.route("/api/admin/users")
@login_required
def api_admin_users():
    from repositories.mural_repository import MuralRepository

    mural_repo = MuralRepository()
    banned_ids = [str(b["discord_id"]) for b in mural_repo.get_active_bans()]

    players = database.get_all_players()
    links = database.get_all_links()  # gamertag -> discord_id logic needed here

    users_list = []
    # Combine data (Simplified for speed)
    for gamertag, p_data in players.items():
        discord_id = database.get_link_by_gamertag(gamertag)
        users_list.append(
            {
                "username": gamertag,
                "gamertag": gamertag,
                "discord_id": discord_id or "N/A",
                "banned": str(discord_id) in banned_ids if discord_id else False,
            }
        )
    return jsonify({"users": users_list})


@dashboard_bp.route("/api/admin/toggle_ban", methods=["POST"])
@login_required
def api_admin_toggle_ban():
    from flask import request
    from repositories.mural_repository import MuralRepository

    data = request.get_json()
    discord_id = data.get("discord_id")

    repo = MuralRepository()
    # Check if banned
    is_banned = False
    for b in repo.get_active_bans():
        if str(b["discord_id"]) == str(discord_id):
            is_banned = True
            break

    if is_banned:
        repo.unban_player(discord_id)
        return jsonify({"success": True, "new_status": False})
    else:
        repo.ban_player(discord_id, "Banido pelo Painel Admin")
        return jsonify({"success": True, "new_status": True})


@dashboard_bp.route("/api/admin/check_raid_zone", methods=["POST"])
@login_required
def api_admin_check_raid():
    from flask import request
    import math

    data = request.get_json()
    try:
        x = float(data.get("x"))
        z = float(data.get("z"))
    except:
        return jsonify({"error": "Invalid coordinates"}), 400

    bases = database.get_active_bases()
    triggered = []
    is_violation = False

    for base in bases:
        bx = float(base["x"])
        bz = float(base["z"])
        distance = math.sqrt((x - bx) ** 2 + (z - bz) ** 2)

        if distance < 300:  # Warning Zone
            violation = distance < 100  # Ban Zone
            if violation:
                is_violation = True
            triggered.append(
                {
                    "base_name": base["name"],
                    "distance": int(distance),
                    "violation": violation,
                }
            )

    return jsonify(
        {"success": True, "is_violation": is_violation, "triggered": triggered}
    )


@dashboard_bp.route("/api/admin/check_alts", methods=["POST"])
@login_required
def api_admin_check_alts():
    from flask import request
    from utils.ip_intelligence import ip_intel  # Using global instance

    data = request.get_json()
    gamertag = data.get("gamertag")

    if not gamertag:
        return jsonify({"error": "Gamertag required"}), 400

    # Check for alts
    alts = ip_intel.get_alts(gamertag)

    # Get identity info for context
    conn = ip_intel._get_conn()
    identity_info = {}
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT xbox_id, last_ip, last_seen FROM player_identities WHERE gamertag = ?",
            (gamertag,),
        )
        row = cur.fetchone()
        if row:
            identity_info = {"xbox_id": row[0], "last_ip": row[1], "last_seen": row[2]}
        conn.close()
    except:
        pass

    return jsonify(
        {
            "success": True,
            "gamertag": gamertag,
            "alts": alts,
            "alts_count": len(alts),
            "identity": identity_info,
        }
    )


@dashboard_bp.route("/api/admin/logs")
@login_required
def api_admin_logs():
    """Returns parsed game logs"""
    from utils.log_parser import DayZLogParser
    import os

    parser = DayZLogParser()

    # Try to fetch real logs if configured, else use local sample
    # For this environment, we prioritize the local sample we just made
    local_log = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "server_logs.txt"
    )

    if not os.path.exists(local_log):
        # Try to fetch if not exists
        parser.fetch_logs(local_log)

    connections = parser.parse_connections(local_log)

    # Reverse to show newest first
    return jsonify(list(reversed(connections)))


@dashboard_bp.route("/api/admin/nitrado/restart", methods=["POST"])
@login_required
def api_admin_restart():
    from utils.nitrado import restart_server
    import asyncio

    # Run async function in sync context
    success, msg = asyncio.run(restart_server())

    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "error": msg}), 500


@dashboard_bp.route("/api/admin/nitrado/stop", methods=["POST"])
@login_required
def api_admin_stop():
    from utils.nitrado import stop_server
    import asyncio

    success, msg = asyncio.run(stop_server())

    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "error": msg}), 500


# --- ECONOMY ENDPOINTS ---
@dashboard_bp.route("/api/economy/daily", methods=["POST"])
@login_required
def api_economy_daily():
    from flask import session
    import random
    from datetime import datetime, timedelta

    user_id = session.get("discord_user_id")
    economy = database.get_economy(user_id)

    # Check Cooldown
    last_daily = economy.get("last_daily")
    if last_daily:
        last_date = datetime.fromisoformat(last_daily)
        if datetime.now() - last_date < timedelta(hours=24):
            remaining = timedelta(hours=24) - (datetime.now() - last_date)
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return jsonify(
                {
                    "success": False,
                    "error": f"Volte em {hours}h {minutes}m",
                    "cooldown": True,
                }
            )

    # Grant Reward
    reward = random.randint(100, 500)
    database.update_balance(user_id, reward, "daily", "Bônus Diário Web")

    # Update Timestamp
    updated_eco = database.get_economy(user_id)
    updated_eco["last_daily"] = datetime.now().isoformat()
    database.save_economy(user_id, updated_eco)

    return jsonify(
        {
            "success": True,
            "reward": reward,
            "new_balance": updated_eco.get("balance", 0),
        }
    )


@dashboard_bp.route("/api/economy/transfer", methods=["POST"])
@login_required
def api_economy_transfer():
    from flask import session, request

    sender_id = session.get("discord_user_id")
    data = request.get_json()

    # Validate Inputs
    try:
        amount = int(data.get("amount", 0))
        target_info = data.get("target")  # Can be gamertag or discord_id logic
    except:
        return jsonify({"success": False, "error": "Dados inválidos"}), 400

    if amount <= 0:
        return jsonify({"success": False, "error": "Valor deve ser positivo"}), 400

    # Find Target
    # Try to find by gamertag first (simplest UX)
    discord_link = database.get_link_by_gamertag(target_info)
    target_id = discord_link if discord_link else target_info

    # If still no target_id or logic to verify target exists...
    # ideally we verify if target_id has an economy account or check links again
    # For now, let's assume if strict ID wasn't provided, we fail if link lookup failed
    if not target_id:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    if str(target_id) == str(sender_id):
        return jsonify(
            {"success": False, "error": "Não pode transferir para si mesmo"}
        ), 400

    # Check Balance
    sender_eco = database.get_economy(sender_id)
    if sender_eco.get("balance", 0) < amount:
        return jsonify({"success": False, "error": "Saldo insuficiente"}), 400

    # Execute Transfer
    database.update_balance(
        sender_id, -amount, "transfer", f"Enviado para {target_info}"
    )
    database.update_balance(
        target_id, amount, "transfer", f"Recebido de {sender_id}"
    )  # Ideally resolve sender name

    return jsonify(
        {
            "success": True,
            "message": f"Transferido {amount} para {target_info}",
            "new_balance": sender_eco.get("balance", 0) - amount,
        }
    )


@dashboard_bp.route("/api/mural/banned")
def api_mural_banned():
    from repositories.mural_repository import MuralRepository

    repo = MuralRepository()
    bans = repo.get_active_bans()

    # Formata para o frontend
    # DB retorna: discord_id, discord_username, nitrado_gamertag, ban_reason, banned_at, banned_by
    formatted_bans = []
    for ban in bans:
        formatted_bans.append(
            {
                "gamertag": ban.get("nitrado_gamertag") or "Desconhecido",
                "discord_name": ban.get("discord_username"),
                "reason": ban.get("ban_reason") or "Violação de Regras",
                "banned_by": ban.get("banned_by") or "Sistema",
                "date": ban.get("banned_at"),
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png",  # Fallback
            }
        )

    return jsonify(formatted_bans)


@dashboard_bp.route("/stats")
@login_required
def stats():
    return render_template("stats.html")


@dashboard_bp.route("/shop")
def shop():
    return render_template("shop.html")


@dashboard_bp.route("/shop-ecommerce")
def shop_ecommerce():
    return render_template("shop_ecommerce.html")


@dashboard_bp.route("/checkout")
def checkout():
    return render_template("checkout.html")


@dashboard_bp.route("/order-confirmation")
# @login_required  # Temporariamente desabilitado para teste
def order_confirmation():
    return render_template("order_confirmation.html")


@dashboard_bp.route("/loja")
@login_required
def loja():
    return render_template("marketplace.html")


@dashboard_bp.route("/leaderboard")
@login_required
def leaderboard():
    return render_template("leaderboard.html")


@dashboard_bp.route("/heatmap")
@login_required
def heatmap():
    return render_template("heatmap.html")


@dashboard_bp.route("/profile/<name>")
@login_required
def profile(name):
    return render_template("profile.html", player_name=name)


# --- EXPORT ENDPOINTS ---
@dashboard_bp.route("/api/export/players")
def export_players():
    players_db = database.get_all_players()
    players_list = []
    for name, stats in players_db.items():
        kd = (
            stats["kills"]
            if stats.get("deaths", 0) == 0
            else round(stats["kills"] / stats["deaths"], 2)
        )
        players_list.append(
            {
                "name": name,
                "kills": stats.get("kills", 0),
                "deaths": stats.get("deaths", 0),
                "kd": kd,
                "killstreak": stats.get("best_killstreak", 0),
                "longest_shot": stats.get("longest_shot", 0),
            }
        )
    return jsonify(players_list)


@dashboard_bp.route("/api/export/report")
def export_report():
    players_db = database.get_all_players()
    economy = database.get_economy("all")
    total_kills = sum(p.get("kills", 0) for p in players_db.values())
    total_deaths = sum(p.get("deaths", 0) for p in players_db.values())
    total_players = len(players_db)
    total_coins = sum(u.get("balance", 0) for u in economy.values())
    return jsonify(
        {
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "total_kills": total_kills,
                "total_deaths": total_deaths,
                "total_players": total_players,
                "total_coins": total_coins,
            },
        }
    )


# Static routes are handled automatically by the Blueprint
