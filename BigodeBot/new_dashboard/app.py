"""
BigodeTexas Dashboard - Versão 2.1 (SQLite Edition)
Sistema completo de dashboard para servidor DayZ (Unificado)
"""

import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from dotenv import load_dotenv
import sqlite3
import sys
import json
import math

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.achievements import ACHIEVEMENTS_DEF

# Configurar caminho correto para o .env (na raiz do projeto)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


@app.before_request
def before_request():
    """Inject test session in debug mode if missing"""
    # Security check: Only allow this in explicit development environment
    is_development = os.getenv("FLASK_ENV") == "development" or os.getenv("FLASK_DEBUG") == "1"

    if app.debug and is_development and "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
        session["discord_avatar"] = None


# Configuração do banco de dados (SQLite Unificado)
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def get_db():
    """Conexão com banco de dados SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro ao conectar SQLite: {e}")
        return None


# ==================== ROTAS PRINCIPAIS ====================


@app.route("/")
def index():
    """Homepage"""
    return render_template("index.html")


@app.route("/heatmap")
def heatmap():
    return render_template("heatmap.html")


@app.route("/login")
def login():
    """Redireciona para OAuth Discord"""
    from discord_auth import get_oauth_url

    return redirect(get_oauth_url())


@app.route("/callback")
def callback():
    """Callback OAuth Discord"""
    from discord_auth import exchange_code, get_user_info

    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))

    try:
        # Trocar código por token
        token_data = exchange_code(code)
        access_token = token_data.get("access_token")

        if not access_token:
            return redirect(url_for("index"))

        # Buscar informações do usuário
        user_info = get_user_info(access_token)
        discord_id = user_info["id"]

        # Buscar conexões (Xbox)
        from discord_auth import get_user_connections

        connections = get_user_connections(access_token)

        xbox_gamertag = None
        for conn in connections:
            if conn.get("type") == "xbox":
                xbox_gamertag = conn.get("name")
                break

        # Salvar na sessão
        session["discord_user_id"] = discord_id
        session["discord_username"] = user_info["username"]
        session["discord_avatar"] = user_info.get("avatar")
        session["discord_email"] = user_info.get("email")
        session["xbox_gamertag"] = xbox_gamertag

        # --- AUTO-LINK & VERIFICATION LOGIC (Via Discord Connection) ---
        if xbox_gamertag:
            from repositories.player_repository import PlayerRepository

            repo = PlayerRepository()

            # Check existing linking
            stats = repo.get_player_stats_by_discord_id(discord_id)
            current_gt = stats.get("nitrado_gamertag") if stats else None

            if not current_gt:
                print(
                    f"[AUTO-LINK] Automatically linking {discord_id} to Xbox Gamertag: {xbox_gamertag}"
                )
                repo.set_gamertag(discord_id, xbox_gamertag, verified=True)
            elif current_gt.lower() == xbox_gamertag.lower():
                # Already matched, ensure verified flag is set
                repo.set_verified(discord_id, True)
        # -----------------------------------------------------------

        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Erro no OAuth: {e}")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Limpa a sessão e desloga o usuário"""
    session.clear()
    return redirect(url_for("index"))


# ==================== XBOX VERIFICATION (MICROSOFT OAUTH) ====================


@app.route("/login/xbox")
def login_xbox():
    """Redireciona para o login da Microsoft para verificar Xbox"""
    if "discord_user_id" not in session:
        return redirect(url_for("login"))

    from xbox_auth import get_xbox_login_url

    return redirect(get_xbox_login_url())


@app.route("/callback/xbox")
def callback_xbox():
    """Callback do login da Microsoft"""
    if "discord_user_id" not in session:
        return redirect(url_for("index"))

    code = request.args.get("code")
    if not code:
        return redirect(url_for("dashboard"))

    try:
        from xbox_auth import authenticate_with_xbox

        result = authenticate_with_xbox(code)

        if result.get("success") and result.get("gamertag"):
            discord_id = session["discord_user_id"]
            xbox_gamertag = result["gamertag"]

            # Salvar no DB e marcar como verificado
            from repositories.player_repository import PlayerRepository

            repo = PlayerRepository()

            # Vincula a Gamertag provada via Microsoft OAuth e marca como verificado
            repo.set_gamertag(discord_id, xbox_gamertag, verified=True)

            session["xbox_gamertag"] = xbox_gamertag
            print(f"[XBOX-VERIFIED] User {discord_id} verified via MS OAuth as {xbox_gamertag}")

            return render_template("dashboard.html", verification_success=True)
        else:
            print(f"Erro na verificação Xbox: {result.get('error')}")
            return redirect(url_for("dashboard", error="xbox_auth_failed"))

    except Exception as e:
        print(f"Erro no Callback Xbox: {e}")
        return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """Dashboard do usuário"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("dashboard.html")


@app.route("/shop")
def shop():
    """Loja de itens"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("shop.html")


@app.route("/leaderboard")
def leaderboard():
    """Rankings"""
    return render_template("leaderboard.html")


@app.route("/checkout")
def checkout():
    """Página de checkout com mapa"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("checkout.html")


@app.route("/order-confirmation")
def order_confirmation():
    """Confirmação de pedido"""
    return render_template("order_confirmation.html")


@app.route("/agradecimentos")
def agradecimentos():
    """Página de agradecimentos aos amigos"""
    return render_template("agradecimentos.html")


@app.route("/debug/oauth")
def debug_oauth():
    """Página de debug para OAuth"""
    from discord_auth import get_oauth_url

    return jsonify(
        {
            "oauth_url": get_oauth_url(),
            "client_id": os.getenv("DISCORD_CLIENT_ID"),
            "redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
            "client_secret_configured": bool(os.getenv("DISCORD_CLIENT_SECRET")),
        }
    )


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": str(datetime.now()), "version": "2.1-sqlite"})


@app.route("/base")
def base():
    """Página de registro de base"""
    return render_template("base.html")


@app.route("/clan")
def clan():
    """Página de gerenciamento de clã"""
    return render_template("clan.html")


@app.route("/banco")
def banco():
    """Página do Banco Sul"""
    return render_template("banco.html")


@app.route("/achievements")
def achievements():
    """Página de conquistas"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("achievements.html")


@app.route("/history")
def history():
    """Página de histórico de atividades"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("history.html")


@app.route("/settings")
def settings():
    """Página de configurações"""
    if "discord_user_id" not in session:
        session["discord_user_id"] = "test_user_123"
        session["discord_username"] = "Jogador de Teste"
    return render_template("settings.html")


# ==================== API ENDPOINTS ====================


@app.route("/api/stats")
def api_stats():
    """Estatísticas gerais do servidor"""
    try:
        conn = get_db()
        if not conn:
            raise Exception("No DB connection")
        cur = conn.cursor()

        # Total de jogadores
        cur.execute("SELECT COUNT(*) as total FROM users")
        row = cur.fetchone()
        total_players = row["total"] if row else 0

        # Total de kills (se tivermos essa info)
        # cur.execute("SELECT SUM(kills) as total FROM players_db")
        # total_kills = cur.fetchone()["total"] or 0
        total_kills = 0  # Placeholder until we have kills in DB

        # Total de moedas em circulação
        cur.execute("SELECT SUM(balance) as total FROM users")
        row = cur.fetchone()
        total_coins = row["total"] if row and row["total"] else 0

        cur.close()
        conn.close()

        return jsonify(
            {
                "total_players": total_players,
                "total_kills": total_kills,
                "total_coins": total_coins,
                "server_name": "BigodeTexas",
            }
        )
    except Exception as e:
        print(f"Erro em /api/stats: {e}")
        return jsonify(
            {
                "total_players": 0,
                "total_kills": 0,
                "total_coins": 0,
                "server_name": "BigodeTexas",
                "error": "Database temporarily unavailable",
            }
        )


@app.route("/api/user/profile")
def api_user_profile():
    """Perfil do usuário logado"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db()
    if not conn:
        return jsonify({"error": "DB Error"}), 500
    cur = conn.cursor()

    # Buscar dados de economia/user
    cur.execute("SELECT * FROM users WHERE discord_id = ?", (str(user_id),))
    user = cur.fetchone()

    conn.close()

    balance = user["balance"] if user else 0
    gamertag = user["nitrado_gamertag"] if user else None
    is_verified = False
    if user and user["nitrado_verified"]:
        is_verified = True
    elif session.get("xbox_gamertag"):
        is_verified = True

    return jsonify(
        {
            "username": session.get("discord_username", "Jogador"),
            "gamertag": gamertag,
            "balance": balance,
            "avatar": session.get("discord_avatar"),
            "xbox_connected_to_discord": is_verified,
        }
    )


@app.route("/api/user/balance")
def api_user_balance():
    """Saldo do usuário"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE discord_id = ?", (str(user_id),))
    result = cur.fetchone()
    conn.close()

    return jsonify({"balance": result["balance"] if result else 0, "user_id": user_id})


@app.route("/api/shop/items")
def api_shop_items():
    """Lista de itens da loja vindos do SQLite"""
    conn = get_db()
    if not conn:
        return jsonify([])

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT item_key as code, name, price, category, description FROM shop_items WHERE is_active = 1"
        )
        items = [dict(row) for row in cur.fetchall()]
        return jsonify(items)
    except Exception as e:
        print(f"Erro ao carregar itens do DB: {e}")
        return jsonify([])
    finally:
        conn.close()


@app.route("/api/user/stats")
def api_user_stats():
    """Estatísticas do usuário reais do SQLite"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db()
    if not conn:
        return jsonify({"error": "DB Error"}), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT kills, deaths, best_killstreak, total_playtime FROM users WHERE discord_id = ?",
            (str(user_id),),
        )
        row = cur.fetchone()

        if not row:
            return jsonify(
                {
                    "kills": 0,
                    "deaths": 0,
                    "kd": 0,
                    "streak": 0,
                    "playtime": 0,
                    "has_base": False,
                }
            )

        kills = row["kills"] or 0
        deaths = row["deaths"] or 0
        kd = kills / deaths if deaths > 0 else kills

        # Check if user has a base
        cur.execute("SELECT id FROM bases WHERE owner_id = ?", (str(user_id),))
        has_base = cur.fetchone() is not None

        return jsonify(
            {
                "kills": kills,
                "deaths": deaths,
                "kd": round(kd, 2),
                "streak": row["best_killstreak"],
                "total_playtime": row["total_playtime"],
                "has_base": has_base,
            }
        )
    finally:
        conn.close()


@app.route("/api/clan/my")
def api_clan_my():
    """Informações do clã do usuário logado"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db()
    cur = conn.cursor()

    try:
        # Find user clan
        cur.execute(
            """
            SELECT c.*, cm.role
            FROM clan_members cm
            JOIN clans c ON cm.clan_id = c.id
            WHERE cm.discord_id = ?
        """,
            (str(user_id),),
        )
        clan = cur.fetchone()

        if not clan:
            return jsonify({"has_clan": False})

        # Get members
        cur.execute(
            "SELECT discord_id, role, joined_at FROM clan_members WHERE clan_id = ?",
            (clan["id"],),
        )
        members = [dict(row) for row in cur.fetchall()]

        # Get active war if any
        cur.execute(
            """
            SELECT * FROM clan_wars
            WHERE (clan1_id = ? OR clan2_id = ?) AND status = 'active'
            AND (expires_at IS NULL OR expires_at > datetime('now'))
        """,
            (clan["id"], clan["id"]),
        )
        war = cur.fetchone()
        war_data = None
        if war:
            # Get enemy name
            enemy_id = war["clan1_id"] if war["clan2_id"] == clan["id"] else war["clan2_id"]
            cur.execute("SELECT name FROM clans WHERE id = ?", (enemy_id,))
            enemy = cur.fetchone()
            war_data = dict(war)
            war_data["enemy_name"] = enemy["name"] if enemy else "Desconhecido"

        return jsonify(
            {
                "has_clan": True,
                "info": dict(clan),
                "members": members,
                "war": war_data,
            }
        )
    finally:
        conn.close()


@app.route("/api/clan/create", methods=["POST"])
def api_clan_create():
    """Criar um novo clã"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Nome obrigatório"}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        # Check if user already in clan
        cur.execute("SELECT id FROM clan_members WHERE discord_id = ?", (str(user_id),))
        if cur.fetchone():
            return jsonify({"error": "Você já pertence a um clã"}), 400

        color1 = data.get("color1", "#8B0000")
        color2 = data.get("color2", "#000000")

        # Insert clan
        cur.execute(
            "INSERT INTO clans (name, leader_discord_id, symbol_color1, symbol_color2) VALUES (?, ?, ?, ?)",
            (name, str(user_id), color1, color2),
        )
        clan_id = cur.lastrowid

        # Add leader
        cur.execute(
            "INSERT INTO clan_members (clan_id, discord_id, role) VALUES (?, ?, 'leader')",
            (clan_id, str(user_id)),
        )

        conn.commit()
        return jsonify({"success": True, "clan_id": clan_id})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Nome de clã já existe"}), 400
    except Exception as e:
        print(f"Erro ao criar clã: {e}")
        return jsonify({"error": "Erro interno"}), 500
    finally:
        conn.close()


@app.route("/api/clan/add_member", methods=["POST"])
def api_clan_add():
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    identifier = data.get("identifier")
    if not identifier:
        return jsonify({"error": "ID ou Gamertag obrigatório"}), 400

    from repositories.clan_repository import ClanRepository
    from repositories.player_repository import PlayerRepository

    clan_repo = ClanRepository()
    player_repo = PlayerRepository()

    clan = clan_repo.get_user_clan(user_id)
    if not clan:
        return jsonify({"error": "Você não tem clã"}), 400
    if clan["role"] not in ["leader", "moderator"]:
        return jsonify({"error": "Permissão negada"}), 403

    # Resolve identifier
    target_id = identifier
    if not identifier.isdigit():
        target_id = player_repo.get_discord_id_by_gamertag(identifier)
        if not target_id:
            return jsonify({"error": "Gamertag não encontrado"}), 404

    # Check if already in a clan
    existing_clan = clan_repo.get_user_clan(target_id)
    if existing_clan:
        return jsonify({"error": f"Jogador já está no clã {existing_clan['name']}"}), 400

    # Create INVITE instead of direct add
    if clan_repo.create_invite(clan["id"], target_id):
        return jsonify({"success": True, "message": "Convite enviado com sucesso!"})
    else:
        return jsonify({"error": "Erro ao enviar convite (possível duplicata)"}), 400


@app.route("/api/user/invites")
def api_user_invites():
    """Listar convites pendentes"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify([])

    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()
    invites = repo.get_user_invites(user_id)
    return jsonify(invites)


@app.route("/api/clan/invite/respond", methods=["POST"])
def api_clan_invite_respond():
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    invite_id = data.get("invite_id")
    accept = data.get("accept", False)

    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()

    if repo.respond_invite(invite_id, accept):
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Erro ao responder convite"}), 400


@app.route("/api/clan/remove_member", methods=["POST"])
def api_clan_remove():
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    target_id = data.get("discord_id")

    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()

    clan = repo.get_user_clan(user_id)
    if not clan:
        return jsonify({"error": "Clã não encontrado"}), 404

    # Check permissions (Only Leader can remove?)
    if clan["role"] != "leader":
        return jsonify({"error": "Apenas líder pode remover membros"}), 403

    if target_id == user_id:
        return jsonify({"error": "Você não pode se remover aqui"}), 400

    if repo.remove_member(clan["id"], target_id):
        return jsonify({"success": True})
    return jsonify({"error": "Erro ao remover"}), 400


@app.route("/api/clan/leave", methods=["POST"])
def api_clan_leave():
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    from repositories.clan_repository import ClanRepository

    repo = ClanRepository()

    clan = repo.get_user_clan(user_id)
    if not clan:
        return jsonify({"error": "Clã não encontrado"}), 404

    if clan["role"] == "leader":
        return jsonify(
            {"error": "Líder não pode sair. Transfira a liderança ou delete o clã."}
        ), 400

    if repo.remove_member(clan["id"], user_id):
        return jsonify({"success": True})
    return jsonify({"error": "Erro ao sair"}), 400


@app.route("/api/user/purchases")
def api_user_purchases():
    """Histórico de compras"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db()
    cur = conn.cursor()

    # transactions table has type 'purchase'
    cur.execute(
        """
        SELECT * FROM transactions
        WHERE discord_id = ? AND type = 'purchase'
        ORDER BY created_at DESC
    """,
        (str(user_id),),
    )

    purchases = cur.fetchall()
    conn.close()

    # Formatar dados
    result = []
    for p in purchases:
        # Description might store JSON or text, assuming JSON based on recent edits to player_repository
        # actually transactions table has 'description' as text.
        # But wait, app.py logic was inserting JSON into 'items' column in purchases table.
        # We unified into 'transactions'. Let's see how we handle it.
        # Simpler: just return description

        result.append(
            {
                "id": p["id"],
                "date": p["created_at"],  # SQLite returns string usually
                "total": p["amount"],
                "status": "completed",  # Transactions are immediate usually
                "items_count": 1,
                "items": [{"name": p["description"], "quantity": 1}],  # Placeholder
            }
        )

    return jsonify(result)


@app.route("/api/user/achievements")
def api_user_achievements():
    """Conquistas do usuário (IDs desbloqueados)"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({})

    conn = get_db()
    if not conn:
        return jsonify({})

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT achievement_id FROM user_achievements WHERE discord_id = ?",
            (str(user_id),),
        )
        unlocked = [row["achievement_id"] for row in cur.fetchall()]

        # Return as a dict of boolean flags for legacy compatibility if needed
        # or just the list. The current template uses /api/achievements/all
        result = {aid: (aid in unlocked) for aid in ACHIEVEMENTS_DEF.keys()}
        return jsonify(result)
    finally:
        conn.close()


@app.route("/api/achievements/all")
def api_achievements_all():
    """Lista completa de conquistas com progresso e status para o usuário logado"""
    user_id = session.get("discord_user_id")
    if not user_id:
        # Fallback to all locked if not logged in
        unlocked_ids = []
        user_stats = {}
        user_balance = 0
        user_transactions = []
    else:
        conn = get_db()
        try:
            cur = conn.cursor()
            # Get unlocked IDs
            cur.execute(
                "SELECT achievement_id, unlocked_at FROM user_achievements WHERE discord_id = ?",
                (str(user_id),),
            )
            unlocked_data = {row["achievement_id"]: row["unlocked_at"] for row in cur.fetchall()}
            unlocked_ids = list(unlocked_data.keys())

            # Get user stats for progress mapping
            cur.execute(
                "SELECT kills, deaths, total_playtime, balance FROM users WHERE discord_id = ?",
                (str(user_id),),
            )
            row = cur.fetchone()
            user_stats = dict(row) if row else {"kills": 0, "deaths": 0, "total_playtime": 0}
            user_balance = user_stats.get("balance", 0)

            # Get transactions for shopper progress
            cur.execute("SELECT type FROM transactions WHERE discord_id = ?", (str(user_id),))
            user_transactions = [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    result = []

    for ach_id, ach in ACHIEVEMENTS_DEF.items():
        # Mapping real stats to achievement progress
        progress = 0
        if ach_id == "first_kill":
            progress = min(1, user_stats.get("kills", 0))
        elif ach_id == "assassin":
            progress = min(10, user_stats.get("kills", 0))
        elif ach_id == "serial_killer":
            progress = min(50, user_stats.get("kills", 0))
        elif ach_id == "rich":
            progress = min(10000, user_balance)
        elif ach_id == "millionaire":
            progress = min(100000, user_balance)
        elif ach_id == "shopper":
            progress = min(10, sum(1 for t in user_transactions if t.get("type") == "purchase"))
        elif ach_id == "veteran":
            progress = min(50, int(user_stats.get("total_playtime", 0) / 3600))
        elif ach_id == "bounty_hunter":
            progress = min(5, user_stats.get("bounties_completed", 0))

        is_unlocked = ach_id in unlocked_ids

        result.append(
            {
                "id": ach_id,
                "title": ach["title"],
                "description": ach["description"],
                "icon": ach["icon"] if is_unlocked else "🔒",
                "category": ach["category"],
                "rarity": ach["rarity"],
                "tier": ach["tier"],
                "points": ach["points"],
                "reward": ach["reward"],
                "unlocked": is_unlocked,
                "unlockedDate": unlocked_data.get(ach_id) if is_unlocked else None,
                "progress": progress,
                "maxProgress": ach["maxProgress"],
            }
        )

    return jsonify(result)


@app.route("/api/achievements/stats")
def api_achievements_stats():
    """Estatísticas globais de conquistas do usuário"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify(
            {
                "total_unlocked": 0,
                "total_achievements": len(ACHIEVEMENTS_DEF),
                "total_points": 0,
                "rare_count": 0,
                "completion_rate": 0,
            }
        )

    conn = get_db()
    if not conn:
        return jsonify({})

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT achievement_id FROM user_achievements WHERE discord_id = ?",
            (str(user_id),),
        )
        unlocked_ids = [row["achievement_id"] for row in cur.fetchall()]

        total_points = 0
        rare_count = 0

        for ach_id in unlocked_ids:
            if ach_id in ACHIEVEMENTS_DEF:
                ach = ACHIEVEMENTS_DEF[ach_id]
                total_points += ach["points"]
                if ach["rarity"] in ["epic", "legendary", "mythic"]:
                    rare_count += 1

        total_achs = len(ACHIEVEMENTS_DEF)
        completion_rate = round((len(unlocked_ids) / total_achs * 100), 1) if total_achs > 0 else 0

        return jsonify(
            {
                "total_unlocked": len(unlocked_ids),
                "total_achievements": total_achs,
                "total_points": total_points,
                "rare_count": rare_count,
                "completion_rate": completion_rate,
            }
        )
    finally:
        conn.close()


@app.route("/api/user/update-gamertag", methods=["POST"])
def api_user_update_gamertag():
    """Atualizar gamertag do usuário"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    gamertag = data.get("gamertag", "").strip()

    if not gamertag:
        return jsonify({"error": "Gamertag inválido"}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        # Tabela users tem nitrado_gamertag
        cur.execute(
            "INSERT OR IGNORE INTO users (discord_id, created_at) VALUES (?, datetime('now'))",
            (str(user_id),),
        )
        cur.execute(
            "UPDATE users SET nitrado_gamertag = ?, updated_at = datetime('now') WHERE discord_id = ?",
            (gamertag, str(user_id)),
        )

        conn.commit()

        return jsonify({"success": True, "gamertag": gamertag})

    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar gamertag: {e}")
        return jsonify({"error": "Erro ao salvar gamertag"}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/leaderboard")
def api_leaderboard():
    """Dados de todos os rankings reais do SQL"""
    conn = get_db()
    if not conn:
        return jsonify({})

    try:
        cur = conn.cursor()

        # Mais Ricos
        cur.execute(
            "SELECT nitrado_gamertag as name, balance as value, nitrado_verified as verified FROM users WHERE nitrado_gamertag IS NOT NULL ORDER BY balance DESC LIMIT 10"
        )
        richest = [dict(row) for row in cur.fetchall()]

        # Mais Kills
        cur.execute(
            "SELECT nitrado_gamertag as name, kills as value, nitrado_verified as verified FROM users WHERE nitrado_gamertag IS NOT NULL ORDER BY kills DESC LIMIT 10"
        )
        kills = [dict(row) for row in cur.fetchall()]

        # Melhor K/D (mínimo 5 kills)
        cur.execute("""
            SELECT nitrado_gamertag as name,
            CASE WHEN deaths = 0 THEN kills ELSE CAST(kills AS FLOAT) / deaths END as value,
            nitrado_verified as verified
            FROM users WHERE kills >= 5 AND nitrado_gamertag IS NOT NULL
            ORDER BY value DESC LIMIT 10
        """)
        kd = [dict(row) for row in cur.fetchall()]

        return jsonify(
            {
                "richest": richest,
                "kills": kills,
                "kd": kd,
                "zombies": [],
                "distance": [],
                "vehicle": [],
            }
        )
    finally:
        conn.close()


@app.route("/api/shop/purchase", methods=["POST"])
def api_shop_purchase():
    """Processar compra"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    total_cost = data.get("total")
    items = data.get("items")
    coordinates = data.get("coordinates")

    if not total_cost or not items:
        return jsonify({"error": "Dados inválidos"}), 400

    conn = get_db()
    cur = conn.cursor()

    from repositories.player_repository import PlayerRepository

    repo = PlayerRepository()

    try:
        # Verificar o status de verificação via PlayerRepository
        if not repo.is_verified(user_id):
            return (
                jsonify(
                    {
                        "error": "Acesso negado: Sua conta Xbox não está verificada.",
                        "need_verification": True,
                    }
                ),
                403,
            )

        # Verificar saldo
        balance = repo.get_balance(user_id)
        if balance < total_cost:
            return jsonify({"error": "Saldo insuficiente"}), 400

        # Deduzir saldo e registrar transação
        items_desc = ", ".join([f"{i.get('quantity')}x {i.get('name')}" for i in items])
        new_balance = repo.update_balance(
            user_id, -total_cost, reason=f"Shop Purchase: {items_desc} at {coordinates}"
        )

        # Adicionar ao inventário
        first_item_name = ""
        for item in items:
            item_key = item.get("code") or item.get("name")  # Usar code se disponível
            item_name = item.get("name")
            if not first_item_name:
                first_item_name = item_name
            qty = item.get("quantity", 1)
            if item_key:
                repo.add_to_inventory(user_id, item_key, item_name, quantity=qty)

        # 🏆 Check Achievements
        repo.check_and_unlock_achievements(str(user_id))

        # 🚁 Tentar realizar a entrega via FTP (Spawn)
        # Import local para evitar circular imports se houver
        from utils.ftp_helpers import upload_spawn_request

        spawn_success = False
        # Se for múltiplos itens, o ideal seria iterar ou o upload_spawn_request suportar lista
        # Por enquanto o ftp_helpers.py suporta 1 item por vez no JSON structure atual de lá
        # Vamos tentar entregar o primeiro item como "prova de conceito" ou chamar multiple times
        # A função upload_spawn_request atualmente aceita (item_name, coords)

        # Melhoria: Vamos chamar para cada item comprado
        delivery_status = []
        for item in items:
            i_name = item.get("name")
            if upload_spawn_request(i_name, coordinates):
                delivery_status.append(f"{i_name}: Entregue")
                spawn_success = True
            else:
                delivery_status.append(f"{i_name}: Erro no Drone")

        msg_delivery = (
            " Itens despachados!" if spawn_success else " Erro no drone (itens no inventário)."
        )

        return jsonify(
            {
                "success": True,
                "deliveryTime": f"Instantâneo.{msg_delivery}",
                "coordinates": coordinates,
                "total": total_cost,
                "new_balance": new_balance,
            }
        )

    except Exception as e:
        conn.rollback()
        print(f"Erro na compra: {e}")
        return jsonify({"error": "Erro ao processar compra"}), 500
    finally:
        cur.close()
        conn.close()


@app.route("/api/bounties")
def api_bounties():
    """Lista de bumbas ativas"""
    conn = get_db()
    if not conn:
        return jsonify([])

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bounties ORDER BY amount DESC")
        bounties = [dict(row) for row in cur.fetchall()]
        return jsonify(bounties)
    except Exception as e:
        print(f"Erro ao carregar bounties: {e}")
        return jsonify([])
    finally:
        conn.close()


@app.route("/api/heatmap")
def api_heatmap():
    """API de Heatmap - Dados reais da tabela pvp_kills com filtros"""
    time_range = request.args.get("range", "24h")
    weapon_filter = request.args.get("weapon", "all")  # ✅ NOVO: Filtro de arma
    grid_size = int(request.args.get("grid", 100))  # ✅ NOVO: Clustering por grid (metros)

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "points": [], "total_events": 0})

    try:
        cur = conn.cursor()

        # ✅ OTIMIZADO: Query com clustering e filtro de arma
        query = f"""
            SELECT
                CAST(game_x/{grid_size} AS INTEGER)*{grid_size} + {grid_size}/2 as x,
                CAST(game_z/{grid_size} AS INTEGER)*{grid_size} + {grid_size}/2 as z,
                COUNT(*) as count
            FROM pvp_kills
            WHERE 1=1
        """
        params = []

        # Time Filter
        if time_range == "24h":
            query += " AND timestamp >= datetime('now', '-24 hours')"
        elif time_range == "7d":
            query += " AND timestamp >= datetime('now', '-7 days')"
        elif time_range == "30d":
            query += " AND timestamp >= datetime('now', '-30 days')"

        # ✅ NOVO: Weapon Filter
        if weapon_filter != "all":
            query += " AND weapon = ?"
            params.append(weapon_filter)

        # ✅ NOVO: Group by grid
        query += (
            f" GROUP BY CAST(game_x/{grid_size} AS INTEGER), CAST(game_z/{grid_size} AS INTEGER)"
        )

        cur.execute(query, params)
        rows = cur.fetchall()

        points = [{"x": row["x"], "z": row["z"], "count": row["count"]} for row in rows]
        total_events = sum(p["count"] for p in points)

        return jsonify({"success": True, "points": points, "total_events": total_events})
    finally:
        conn.close()


@app.route("/api/heatmap/top_locations")
def api_heatmap_top():
    """Top Zonas de Conflito"""
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "locations": []})

    try:
        cur = conn.cursor()

        # Clustering logic is hard in SQL, so we'll just mock hotspots or use static zones
        # For a "WOW" effect, let's group by general regions if possible, or just return top random coords for demo
        # A simple approach: Group by truncated coords (approx 1km grid)
        cur.execute("""
            SELECT
                CAST(game_x/1000 AS INTEGER)*1000 + 500 as center_x,
                CAST(game_z/1000 AS INTEGER)*1000 + 500 as center_z,
                COUNT(*) as deaths
            FROM pvp_kills
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY CAST(game_x/1000 AS INTEGER), CAST(game_z/1000 AS INTEGER)
            ORDER BY deaths DESC
            LIMIT 5
        """)

        locations = []
        rows = cur.fetchall()

        # Helper to name locations
        import math

        CHERNARUS_CITIES = {
            # Cidades Principais
            "NWAF": (4600, 10000),
            "Berezino": (12000, 9000),
            "Cherno": (6500, 2500),
            "Elektro": (10500, 2300),
            "Tisy": (1700, 14000),
            # Cidades Médias
            "Vybor": (3800, 8900),
            "Stary Sobor": (6000, 7700),
            "Zeleno": (2700, 5300),
            "Novo": (11100, 12200),
            "Severograd": (7900, 12600),
            "Kamensk": (7900, 14400),
            "Krasnostav": (11200, 12000),
            # Vilas e Pequenas Cidades
            "Gorka": (9800, 8900),
            "Polana": (6900, 6400),
            "Mogilevka": (7500, 5000),
            "Guglovo": (8500, 6700),
            "Dubrovka": (10200, 9400),
            "Solnichniy": (13400, 6400),
            "Nizhnoye": (13000, 7900),
            "Staroye": (10100, 5400),
            "Dolina": (11100, 7000),
            "Orlovets": (11300, 8400),
            "Shakhovka": (9900, 2600),
            "Lopatino": (2700, 7100),
            "Pustoshka": (3600, 5900),
            "Grishino": (5900, 10200),
            "Vyshnoye": (6600, 6100),
            "Rogovo": (4800, 6800),
            "Kabanino": (5300, 8600),
            "Pogorevka": (4400, 6500),
            "Pulkovo": (5600, 3400),
            "Sosnovka": (2600, 6100),
        }

        for row in rows:
            cx, cz = row["center_x"], row["center_z"]
            name = "Ermo"
            min_dist = 20000
            for city, (bx, bz) in CHERNARUS_CITIES.items():
                dist = math.sqrt((cx - bx) ** 2 + (cz - bz) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    name = city

            if min_dist > 1000:  # ✅ MELHORADO: Reduzido de 1500 para 1000m
                name = f"Setor {int(cx / 1000)}x{int(cz / 1000)}"

            locations.append(
                {
                    "location_name": name,
                    "deaths": row["deaths"],
                    "center_x": cx,
                    "center_z": cz,
                }
            )

        return jsonify({"success": True, "locations": locations})
    finally:
        conn.close()


@app.route("/api/heatmap/timeline")
def api_heatmap_timeline():
    """Timeline de mortes"""
    time_range = request.args.get("range", "24h")
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "timeline": []})

    try:
        cur = conn.cursor()

        # Group by hour or day
        if time_range == "24h":
            fmt = "%Y-%m-%d %H:00:00"
        else:
            fmt = "%Y-%m-%d"

        # Parameterized query for timeline
        cur.execute(
            """
            SELECT strftime(?, timestamp) as period, COUNT(*) as pvp
            FROM pvp_kills
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY period
            ORDER BY period
        """,
            (fmt,),
        )

        timeline = []
        for row in cur.fetchall():
            timeline.append(
                {
                    "period": row["period"],
                    "pvp": row["pvp"],
                    "pve": 0,  # Placeholder until we track PvE
                }
            )

        return jsonify({"success": True, "timeline": timeline})
    finally:
        conn.close()


@app.route("/api/base/register", methods=["POST"])
def api_base_register():
    """Registrar nova base"""
    user_id = session.get("discord_user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    x = data.get("coord_x")
    # Frontend sends: coord_x, coord_y, coord_z, name
    # In DayZ map: X and Z are the horizontal plane. Y is height.
    # The frontend form labels are "Eixo X" and "Eixo Y" but map is usually X/Z.
    # Let's assume the user input "Y" is actually Z (North/South).
    # The frontend JS sends: coord_x, coord_y (from input), coord_z (0)

    # We should map frontend 'coord_y' to database 'z' for standard 2D coords
    game_z = data.get("coord_y")
    game_y = data.get("coord_z", 0)  # Height
    name = data.get("name", "Base Sem Nome")

    if x is None or game_z is None:
        return jsonify({"error": "Coordenadas inválidas"}), 400

    from repositories.player_repository import PlayerRepository

    repo = PlayerRepository()

    success, msg = repo.add_base(user_id, x, game_y, game_z, name)

    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"error": msg}), 400


@app.route("/api/heatmap/hourly")
def api_heatmap_hourly():
    """Atividade por hora do dia (0-23h)"""
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "hourly": [0] * 24})

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT CAST(strftime('%H', timestamp) as INTEGER) as hour, COUNT(*) as count
            FROM pvp_kills
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY hour
        """)

        hourly = [0] * 24
        for row in cur.fetchall():
            h = row["hour"]
            if 0 <= h < 24:
                hourly[h] = row["count"]

        return jsonify({"success": True, "hourly": hourly})
    finally:
        conn.close()


@app.route("/api/heatmap/weapons")
def api_heatmap_weapons():
    """Armas mais usadas"""
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "weapons": []})
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT weapon as name, COUNT(*) as count
            FROM pvp_kills
            WHERE weapon IS NOT NULL AND weapon != 'Desconhecida'
            GROUP BY weapon
            ORDER BY count DESC
            LIMIT 10
        """)
        weapons = [dict(row) for row in cur.fetchall()]
        return jsonify({"success": True, "weapons": weapons})
    finally:
        conn.close()


@app.route("/api/heatmap/hero_stats")
def api_heatmap_hero_stats():
    """Estatísticas gerais para o Hero Stats Banner"""
    time_range = request.args.get("range", "24h")
    conn = get_db()
    if not conn:
        return jsonify({"success": False})

    try:
        cur = conn.cursor()

        # Time filter
        time_filter = ""
        if time_range == "24h":
            time_filter = "WHERE timestamp >= datetime('now', '-24 hours')"
        elif time_range == "7d":
            time_filter = "WHERE timestamp >= datetime('now', '-7 days')"
        elif time_range == "30d":
            time_filter = "WHERE timestamp >= datetime('now', '-30 days')"
        # else: all time (no filter)

        # 1. Total Kills
        cur.execute(f"SELECT COUNT(*) as total FROM pvp_kills {time_filter}")
        total_kills = cur.fetchone()["total"] or 0

        # 2. Kills Today (last 24h)
        cur.execute(
            "SELECT COUNT(*) as total FROM pvp_kills WHERE timestamp >= datetime('now', '-24 hours')"
        )
        kills_today = cur.fetchone()["total"] or 0

        # 3. Top Weapon
        cur.execute(f"""
            SELECT weapon, COUNT(*) as count
            FROM pvp_kills
            {time_filter}
            AND weapon IS NOT NULL AND weapon != 'Desconhecida'
            GROUP BY weapon
            ORDER BY count DESC
            LIMIT 1
        """)
        top_weapon_row = cur.fetchone()
        top_weapon = top_weapon_row["weapon"] if top_weapon_row else "-"

        # 4. Top Player (killer_name)
        cur.execute(f"""
            SELECT killer_name, COUNT(*) as count
            FROM pvp_kills
            {time_filter}
            AND killer_name IS NOT NULL
            GROUP BY killer_name
            ORDER BY count DESC
            LIMIT 1
        """)
        top_player_row = cur.fetchone()
        top_player = top_player_row["killer_name"] if top_player_row else "-"

        # 5. Peak Hour (horário com mais atividade)
        cur.execute(f"""
            SELECT CAST(strftime('%H', timestamp) as INTEGER) as hour, COUNT(*) as count
            FROM pvp_kills
            {time_filter}
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        """)
        peak_hour_row = cur.fetchone()
        if peak_hour_row:
            h = peak_hour_row["hour"]
            peak_hour = f"{h}h-{(h + 1) % 24}h"
        else:
            peak_hour = "-"

        # 6. Hottest Zone (usar lógica de top_locations)
        cur.execute(f"""
            SELECT
                CAST(game_x/1000 AS INTEGER)*1000 + 500 as center_x,
                CAST(game_z/1000 AS INTEGER)*1000 + 500 as center_z,
                COUNT(*) as deaths
            FROM pvp_kills
            {time_filter}
            GROUP BY CAST(game_x/1000 AS INTEGER), CAST(game_z/1000 AS INTEGER)
            ORDER BY deaths DESC
            LIMIT 1
        """)
        hottest_row = cur.fetchone()
        hottest_zone = "-"
        if hottest_row:
            cx, cz = hottest_row["center_x"], hottest_row["center_z"]
            # Usar mesmo dicionário de cidades
            CHERNARUS_CITIES = {
                "NWAF": (4600, 10000),
                "Berezino": (12000, 9000),
                "Cherno": (6500, 2500),
                "Elektro": (10500, 2300),
                "Tisy": (1700, 14000),
                "Vybor": (3800, 8900),
                "Stary Sobor": (6000, 7700),
                "Zeleno": (2700, 5300),
                "Novo": (11100, 12200),
                "Severograd": (7900, 12600),
                "Kamensk": (7900, 14400),
                "Krasnostav": (11200, 12000),
                "Gorka": (9800, 8900),
                "Polana": (6900, 6400),
                "Mogilevka": (7500, 5000),
                "Guglovo": (8500, 6700),
                "Dubrovka": (10200, 9400),
                "Solnichniy": (13400, 6400),
                "Nizhnoye": (13000, 7900),
                "Staroye": (10100, 5400),
                "Dolina": (11100, 7000),
                "Orlovets": (11300, 8400),
                "Shakhovka": (9900, 2600),
                "Lopatino": (2700, 7100),
                "Pustoshka": (3600, 5900),
                "Grishino": (5900, 10200),
                "Vyshnoye": (6600, 6100),
                "Rogovo": (4800, 6800),
                "Kabanino": (5300, 8600),
                "Pogorevka": (4400, 6500),
                "Pulkovo": (5600, 3400),
                "Sosnovka": (2600, 6100),
            }
            min_dist = 20000
            for city, (bx, bz) in CHERNARUS_CITIES.items():
                dist = math.sqrt((cx - bx) ** 2 + (cz - bz) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    hottest_zone = city
            if min_dist > 1000:
                hottest_zone = f"Setor {int(cx / 1000)}x{int(cz / 1000)}"

        return jsonify(
            {
                "success": True,
                "total_kills": total_kills,
                "kills_today": kills_today,
                "top_weapon": top_weapon,
                "top_player": top_player,
                "peak_hour": peak_hour,
                "hottest_zone": hottest_zone,
            }
        )
    finally:
        conn.close()


# ==================== ADMIN ROUTES ====================


# --- MIGRATION CHECK ---
def ensure_banned_column():
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            # Try to select the column to see if it exists
            try:
                cur.execute("SELECT is_banned FROM users LIMIT 1")
            except sqlite3.OperationalError:
                # Column missing, add it
                print("[MIGRATION] Adding 'is_banned' column to users table...")
                cur.execute("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0")
                conn.commit()
        except Exception as e:
            print(f"[MIGRATION ERROR] {e}")
        finally:
            conn.close()


# Run migration logic
ensure_banned_column()


def require_admin(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("discord_user_id")
        # Read from .env
        env_admin_ids = os.getenv("ADMIN_DISCORD_IDS", "")
        admin_list = [i.strip() for i in env_admin_ids.split(",") if i.strip()]

        # Fallback security if env is empty
        if not admin_list:
            admin_list = ["322846467389259776"]  # Keeping original dev ID as fallback

        if not user_id or str(user_id) not in admin_list:
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin")
@require_admin
def admin_panel():
    return render_template("admin.html")


@app.route("/api/admin/users")
@require_admin
def api_admin_users():
    conn = get_db()
    if not conn:
        return jsonify({"error": "DB Error"}), 500
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT discord_id, nitrado_gamertag as gamertag, balance, nitrado_verified, is_banned FROM users ORDER BY created_at DESC LIMIT 100"
        )
        users = []
        for row in cur.fetchall():
            users.append(
                {
                    "discord_id": row["discord_id"],
                    "gamertag": row["gamertag"],
                    "username": f"User {row['discord_id'][-4:]}",  # Placeholder name
                    "banned": bool(row["is_banned"]),
                }
            )
        return jsonify({"users": users})
    finally:
        conn.close()


@app.route("/api/admin/toggle_ban", methods=["POST"])
@require_admin
async def api_admin_toggle_ban():
    data = request.get_json()
    target_id = data.get("discord_id")

    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT is_banned, nitrado_gamertag FROM users WHERE discord_id = ?",
            (target_id,),
        )
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "User not found"}), 404

        current_status = bool(row["is_banned"])
        new_status = not current_status
        gamertag = row["nitrado_gamertag"]

        # Update DB
        cur.execute(
            "UPDATE users SET is_banned = ? WHERE discord_id = ?",
            (new_status, target_id),
        )
        conn.commit()

        # Call Nitrado API if banning and gamertag exists
        if new_status and gamertag:
            from utils.nitrado import ban_player

            await ban_player(gamertag)

        return jsonify({"success": True, "new_status": new_status})
    except Exception as e:
        print(f"Error toggle ban: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/admin/dashboard_stats")
@require_admin
async def api_admin_dashboard_stats():
    conn = get_db()
    stats = {
        "total_bases": 0,
        "online_players": [],
        "online_count": 0,
        "raid_active": False,  # Default
        "build_mode": "restricted",  # Default
    }

    if not conn:
        return jsonify({"error": "DB Error"}), 500

    try:
        cur = conn.cursor()
        # 1. Base Count
        cur.execute("SELECT COUNT(*) FROM bases")
        stats["total_bases"] = cur.fetchone()[0]

        # 2. Config (Simulated from DB or JSON)
        # Assuming we store config in a simple key-value table if it existed, or JSON
        # For now, let's load from config.json or a designated file for dynamic states
        # Let's check 'bot_state.json' if created, otherwise default to False/Restricted
        # To make it persistent, allow read/write to a JSON state file
        config_path = "server_config.json"  # New specific config
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                import json

                c = json.load(f)
                stats["raid_active"] = c.get("raid_active", False)
                stats["build_mode"] = c.get("build_mode", "restricted")
                stats["raid_days"] = c.get("raid_days", [5])  # Default Saturday
                stats["raid_start"] = c.get("raid_start", 20)  # Default 20h
                stats["raid_end"] = c.get("raid_end", 22)  # Default 22h
        else:
            stats["raid_days"] = [5]
            stats["raid_start"] = 20
            stats["raid_end"] = 22

        # 3. Online Players (Async Nitrado Call)
        from utils.nitrado import get_online_players

        online_list = await get_online_players()
        # Mock for dev/demo if empty or failed (optional, let's stick to empty list is safe)
        stats["online_players"] = online_list
        stats["online_count"] = len(online_list)

        return jsonify(stats)
    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/admin/update_settings", methods=["POST"])
@require_admin
def api_admin_update_settings():
    data = request.get_json()
    config_path = "server_config.json"

    current_config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            try:
                current_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

    if "raid_active" in data:
        current_config["raid_active"] = data["raid_active"]
        # Trigger any logic needed (e.g. upload globals.xml) - For now just state

    if "build_mode" in data:
        current_config["build_mode"] = data["build_mode"]

    if "raid_days" in data:
        current_config["raid_days"] = data["raid_days"]

    if "raid_start" in data:
        current_config["raid_start"] = int(data["raid_start"])

    if "raid_end" in data:
        current_config["raid_end"] = int(data["raid_end"])

    with open(config_path, "w") as f:
        json.dump(current_config, f)

    return jsonify({"success": True, "config": current_config})


@app.route("/api/admin/check_raid_zone", methods=["POST"])
@require_admin
def api_admin_check_raid():
    """Simulate Anti-Raid check for given coordinates"""
    data = request.get_json()
    try:
        x = float(data.get("x"))
        z = float(data.get("z"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coords"}), 400

    from repositories.player_repository import PlayerRepository

    repo = PlayerRepository()
    bases = repo.get_all_bases()
    triggered = []

    for b in bases:
        try:
            bx, bz = b["x"], b["z"]
            # radius = b["radius"]  # Unused variable removed

            # Distance check
            dist = math.sqrt((x - bx) ** 2 + (z - bz) ** 2)

            # Detection logic (Simulated 100m for build protection)
            if dist <= 100.0:
                triggered.append(
                    {
                        "base_name": b["name"],
                        "owner_id": b["owner_id"],
                        "distance": round(dist, 1),
                        "violation": True,
                    }
                )
            elif dist <= 300.0:
                triggered.append(
                    {
                        "base_name": b["name"],
                        "owner_id": b["owner_id"],
                        "distance": round(dist, 1),
                        "violation": False,
                        "msg": "Near base (Warning Zone)",
                    }
                )

        except Exception as e:
            print(f"Error checking base {b}: {e}")

    return jsonify(
        {
            "success": True,
            "x": x,
            "z": z,
            "triggered": triggered,
            "is_violation": any(t["violation"] for t in triggered),
        }
    )


if __name__ == "__main__":
    # Restricted to localhost for safety, use environment variable for external access (0.0.0.0)
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host=host, port=5000, debug=debug_mode)
