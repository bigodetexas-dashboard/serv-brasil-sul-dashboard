"""
Admin Routes - BigodeTexas Dashboard
Implementa a lógica do Painel Administrativo, incluindo:
- Texano AI (Assistente Tático com Contexto de Sistema)
- Gerenciamento de Usuários e Alts
- Controles de Servidor (Raid/Build)
- Logs e Diagnósticos de Segurança
"""

from flask import Blueprint, request, jsonify, session, current_app, render_template
from functools import wraps
import sqlite3
import os
import json
import asyncio
from datetime import datetime, timedelta

# Import integrations
from ai_integration import ask_gemini
from security_helpers import ip_blacklist, waf

# Define Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# --- DATABASE HELPER ---
def get_db_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
    )


def query_db(query, args=(), one=False):
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        conn.commit()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        print(f"[ADMIN DB ERROR] {e}")
        return [] if not one else None


# --- AUTH DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Dev Bypass
        if (
            os.getenv("FLASK_ENV") == "development"
            and session.get("discord_user_id") == "test_user_123"
        ):
            return f(*args, **kwargs)

        # 2. Check Session
        user_id = session.get("discord_user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # 3. Check Admin Role in DB (Simplified for now, assuming hardcoded admins or specific table)
        # TODO: Implement robust role check. For now, we allow access if in 'admins' table or specific IDs
        # admin = query_db("SELECT * FROM admins WHERE discord_id = ?", (user_id,), one=True)
        # if not admin:
        #     return jsonify({"error": "Access Denied"}), 403

        return f(*args, **kwargs)

    return decorated_function


# --- CSRF EXEMPT HELPER ---
def csrf_exempt(f):
    """Exempts the view from CSRF protection."""
    f._csrf_exempt = True
    return f


@admin_bp.route("/")
@admin_required
def admin_panel():
    """Main Admin Panel Interface"""
    return render_template("admin.html")


# ==================== TEXANO AI ENGINE ====================


def get_system_diagnostics():
    """
    Coleta sinais vitais do sistema para dar contexto ao Texano.
    Ele 'lê' o sistema antes de responder.
    """
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "status": "ONLINE",
        "alerts": [],
    }

    # 1. Check Database
    try:
        user_count = query_db("SELECT COUNT(*) FROM users", one=True)[0]
        diagnostics["db_users"] = user_count
        diagnostics["db_status"] = "HEALTHY"
    except:
        diagnostics["db_status"] = "CRITICAL_FAILURE"
        diagnostics["alerts"].append("Banco de dados inacessível!")

    # 2. Check recent WAF/Security Logs (Last 1 hour)
    try:
        waf_logs = query_db(
            "SELECT COUNT(*) FROM waf_logs WHERE timestamp > datetime('now', '-1 hour')",
            one=True,
        )[0]
        if waf_logs > 50:
            diagnostics["security_level"] = "HIGH"
            diagnostics["alerts"].append(
                f"Ataque em andamento? {waf_logs} violações WAF na última hora."
            )
        elif waf_logs > 10:
            diagnostics["security_level"] = "ELEVATED"
            diagnostics["alerts"].append(
                f"Atividade suspeita detectada: {waf_logs} tentativas de invasão."
            )
        else:
            diagnostics["security_level"] = "NORMAL"
    except:
        diagnostics["security_level"] = "UNKNOWN"

    # 3. Check Pending Deliveries (Shop)
    try:
        pending = query_db(
            "SELECT COUNT(*) FROM shop_orders WHERE delivered = 0", one=True
        )[0]
        diagnostics["pending_deliveries"] = pending
        if pending > 10:
            diagnostics["alerts"].append(
                f"Fila de entregas engarrafada: {pending} pedidos pendentes."
            )
    except:
        pass

    return diagnostics


@admin_bp.route("/texano/vitals", methods=["GET"])
@csrf_exempt
@admin_required
def texano_vitals():
    """Retorna os sinais vitais para a UI (pulso)"""
    diag = get_system_diagnostics()

    # Check suspicious alts for the pulse
    suspicious = []
    try:
        # Simple check for users with same Last IP in last 24h
        suspicious = query_db("""
            SELECT last_ip, COUNT(DISTINCT discord_id) as c
            FROM player_identities
            WHERE last_seen > datetime('now', '-24 hours')
            GROUP BY last_ip
            HAVING c > 1
        """)
    except:
        pass

    return jsonify(
        {
            "success": True,
            "db_status": diag.get("db_status"),
            "pending_deliveries": diag.get("pending_deliveries", 0),
            "security_level": diag.get("security_level"),
            "total_identities": diag.get("db_users", 0),
            "suspicious_alts": [dict(row) for row in suspicious] if suspicious else [],
        }
    )


@admin_bp.route("/texano/ask", methods=["POST"])
@csrf_exempt
@admin_required
def texano_ask():
    """Endpoint de chat com o Texano (com injeção de contexto)"""
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt vazio"}), 400

    # 1. Coletar Contexto do Sistema (O "Cérebro" do J.A.R.V.I.S.)
    diagnostics = get_system_diagnostics()

    context_str = f"""
    [SYSTEM TELEMETRY]
    - Status DB: {diagnostics.get("db_status")}
    - Usuários Registrados: {diagnostics.get("db_users")}
    - Nível de Segurança: {diagnostics.get("security_level")}
    - Entregas Pendentes: {diagnostics.get("pending_deliveries", 0)}
    - Alertas Ativos: {", ".join(diagnostics.get("alerts", []))}
    """

    # 2. Enviar para IA
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Usamos uma função específica para o Texano se quisermos um prompt de sistema diferente,
        # mas por hora vamos usar ask_gemini injetando o contexto.
        # Mas como o usuário quer que ele seja um "Programador Avançado", vamos instruir isso no prompt.

        full_prompt = f"""
        [CONTEXTO TÉCNICO AVANÇADO]
        {context_str}

        [SUA PERSONA: TEXANO]
        Você é o Texano, uma IA de Elite e Engenheiro de Software Sênior do BigodeTexas.
        Você monitora o servidor DayZ e o código Python/Flask.
        - Se ver alertas de segurança, sugira bloqueio de IP.
        - Se ver entregas pendentes, sugira verificar o `delivery_processor.py`.
        - Fale de forma técnica, mas direta ("Xerife").
        - Você NÃO executa comandos, apenas diagnóstica e sugere.

        [PERGUNTA DO ADMIN]
        {prompt}
        """

        response = loop.run_until_complete(ask_gemini(full_prompt))
        loop.close()

        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== USER MANAGEMENT ====================


@admin_bp.route("/check_alts", methods=["POST"])
@csrf_exempt
@admin_required
def check_alts():
    """Verifica contas secundárias (Mesmo IP ou Hardware ID)"""
    data = request.get_json()
    gamertag = data.get("gamertag")

    if not gamertag:
        return jsonify({"error": "Gamertag required"}), 400

    # Buscar dados do alvo
    target = query_db(
        "SELECT * FROM player_identities WHERE gamertag = ? COLLATE NOCASE",
        (gamertag,),
        one=True,
    )

    if not target:
        return jsonify(
            {
                "success": False,
                "error": "Jogador não encontrado na base de identidades.",
            }
        )

    target_ip = target["last_ip"]
    target_xbox_id = target["xbox_id"]

    # Buscar coincidências
    # 1. Por IP
    ip_matches = []
    if target_ip:
        ip_matches = query_db(
            "SELECT gamertag, discord_id FROM player_identities WHERE last_ip = ? AND gamertag != ? COLLATE NOCASE",
            (target_ip, gamertag),
        )

    # 2. Por Xbox ID (Hardware/Conta) caso tenhamos esse dado
    xbox_matches = []
    if target_xbox_id:
        xbox_matches = query_db(
            "SELECT gamertag, discord_id FROM player_identities WHERE xbox_id = ? AND gamertag != ? COLLATE NOCASE",
            (target_xbox_id, gamertag),
        )

    # Consolidar
    alts = set()
    for m in ip_matches or []:
        alts.add(f"{m['gamertag']} (IP)")
    for m in xbox_matches or []:
        alts.add(f"{m['gamertag']} (ID)")

    return jsonify(
        {
            "success": True,
            "identity": {
                "gamertag": target["gamertag"],
                "last_ip": target_ip,  # TODO: Mask in prod? Admin needs to see it.
                "xbox_id": target_xbox_id,
            },
            "alts_count": len(alts),
            "alts": list(alts),
        }
    )


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """Lista usuários para gerenciamento"""
    users = query_db(
        "SELECT discord_id, discord_username, gamertag, banned FROM users LIMIT 100"
    )  # Pagination TODO
    if not users:
        return jsonify({"users": []})

    return jsonify({"users": [dict(u) for u in users]})


@admin_bp.route("/toggle_ban", methods=["POST"])
@csrf_exempt
@admin_required
def toggle_ban():
    """Banir/Desbanir usuário"""
    data = request.get_json()
    discord_id = data.get("discord_id")

    user = query_db(
        "SELECT banned FROM users WHERE discord_id = ?", (discord_id,), one=True
    )
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_status = not user["banned"]

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET banned = ? WHERE discord_id = ?", (new_status, discord_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "new_status": new_status})


# ==================== SERVER CONTROLS ====================


@admin_bp.route("/logs", methods=["GET"])
@admin_required
def get_logs():
    """Retorna logs do sistema (Simulado/Real)"""
    # Aqui deveríamos ler logs reais do Nitrado ou DB
    # Por enquanto, vamos mockar algo para teste se não tiver DB de logs

    # Tentar ler logs reais do DB se existirem
    logs = query_db("SELECT * FROM game_logs ORDER BY timestamp DESC LIMIT 50")

    if not logs:
        # Mock data for demonstration until log robot populates DB
        return jsonify(
            [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event_type": "connection",
                    "gamertag": "RooKafer",
                    "ip": "1.2.3.4",
                    "extra": {},
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=5)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "event_type": "zombie_kill",
                    "gamertag": "Texano",
                    "ip": "1.2.3.4",
                    "extra": {"zombie_type": "Soldier"},
                },
            ]
        )

    return jsonify([dict(l) for l in logs])


@admin_bp.route("/update_settings", methods=["POST"])
@csrf_exempt
@admin_required
def update_settings():
    """Atualiza configurações de Raid/Build"""
    data = request.get_json()

    # Salvar em arquivo JSON ou DB
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "server_config.json"
    )

    try:
        current_config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                current_config = json.load(f)

        # Merge updates
        current_config.update(data)

        with open(config_path, "w") as f:
            json.dump(current_config, f, indent=4)

        return jsonify({"success": True, "config": current_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/dashboard_stats", methods=["GET"])
@admin_required
def dashboard_stats():
    """Estatísticas gerais para o Admin Dashboard"""

    # Ler config
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "server_config.json"
    )
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

    # Ler dados DB
    # Ler dados DB
    try:
        total_bases_res = query_db("SELECT COUNT(*) FROM bases", one=True)
        total_bases = total_bases_res[0] if total_bases_res else 0
    except:
        total_bases = 0
    # online_count (would come from Nitrado API cache)

    return jsonify(
        {
            "total_bases": total_bases,
            "online_count": 5,  # Mock, precisa integrar com NitradoService
            "raid_active": config.get("raid_active", False),
            "build_mode": config.get("build_mode", "restricted"),
            "raid_days": config.get("raid_days", []),
            "raid_start": config.get("raid_start", 20),
            "raid_end": config.get("raid_end", 22),
        }
    )


@admin_bp.route("/check_raid_zone", methods=["POST"])
@csrf_exempt
@admin_required
def check_raid_zone():
    data = request.get_json()
    x = float(data.get("x", 0))
    z = float(data.get("z", 0))

    # Lógica de verificação de raio de base (Mock para exemplo)
    # Na real, faria query no DB de bases calculando distância

    bases = query_db("SELECT * FROM bases")
    triggered = []

    for b in bases or []:
        # Distância Euclidiana simples (ignora Y)
        dist = ((x - b["x"]) ** 2 + (z - b["z"]) ** 2) ** 0.5
        if dist < 100:  # 100m raio
            triggered.append(f"Base de {b['owner_gamertag']} ({int(dist)}m)")

    return jsonify(
        {"success": True, "is_violation": len(triggered) > 0, "triggered": triggered}
    )
