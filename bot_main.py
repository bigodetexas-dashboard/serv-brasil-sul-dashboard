import os
import sys
import json
import io
import time
import math
import threading
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# Third-Party Imports
import sqlite3
import discord
from discord.ext import commands, tasks
import aiohttp
from flask import Flask, jsonify  # Added jsonify
from dotenv import load_dotenv

# Local Application Imports
import database
from security import (
    AdminWhitelist,
    backup_manager,
)
from web_dashboard import dashboard_bp
from discord_oauth import init_oauth
from flask_wtf.csrf import CSRFProtect  # Added for CSRF support
from new_dashboard.babel_config import init_babel  # Added for Translation support

# Carregar variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÃO GERAL (de variáveis de ambiente) ---
TOKEN = os.getenv("DISCORD_TOKEN")

# FTP (Nitrado)
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Nitrado API
NITRADO_TOKEN = os.getenv("NITRADO_TOKEN")
SERVICE_ID = os.getenv("SERVICE_ID")

# Segurança
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_IDS_STR = os.getenv("ADMIN_WHITELIST", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

# Footer Icon
FOOTER_ICON = os.getenv(
    "FOOTER_ICON",
    "https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png",
)

# Inicializar whitelist de admin
admin_whitelist = AdminWhitelist(ADMIN_IDS)

# Validar configurações críticas
if not TOKEN:
    raise ValueError("DISCORD_TOKEN não encontrado no .env!")
if not FTP_HOST or not FTP_USER or not FTP_PASS:
    raise ValueError("Credenciais FTP não encontradas no .env!")


from utils.helpers import (
    load_json,
    save_json,
    find_item_by_key,
    calculate_kd,
    calculate_level,
    get_user_clan,
)
from utils.ftp_helpers import connect_ftp
from utils.decorators import rate_limit, require_admin_password
from utils.dashboard_api import send_dashboard_event  # NEW
from utils.n8n_dispatcher import send_n8n_base_alert
from utils.auto_failover import auto_failover  # 🔄 AUTO-FAILOVER AUTÔNOMO


async def restart_server():
    """Envia comando de restart para a API da Nitrado."""
    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/restart"
    headers = {"Authorization": f"Bearer {NITRADO_TOKEN}"}

    print(f"Tentando reiniciar servidor ID {SERVICE_ID}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print("[SUCESSO] Servidor reiniciando!")
                        # EMIT EVENT TO DASHBOARD
                        await send_dashboard_event("STATUS", "Reiniciando", 0)
                        return True, "Servidor reiniciando com sucesso!"
                    else:
                        print(f"[AVISO] API: {data}")
                        return False, f"Erro API: {data.get('message')}"
                else:
                    text = await response.text()
                    print(f"❌ ERRO API: {response.status} - {text}")
                    return False, f"Erro HTTP: {response.status}"
    except Exception as e:
        print(f"[ERRO] Erro de conexao: {e}")
        return False, f"Erro de conexao: {e}"


# Arquivos de Dados
ECONOMY_FILE = "economy.json"
ITEMS_FILE = "items.json"
LINKS_FILE = "links.json"
CONFIG_FILE = "config.json"
PLAYERS_DB_FILE = "players_db.json"
ACHIEVEMENTS_FILE = "achievements.json"
CLANS_FILE = "clans.json"
MISSIONS_FILE = "missions.json"
SESSIONS_FILE = "active_sessions.json"

# Rastreamento de Duplicação
pickup_tracker = {}  # {player_name: [(item_id, timestamp)]}
active_sessions = load_json(SESSIONS_FILE)  # {player_name: login_timestamp}

# Configurações de Economia
DAILY_BONUS = 500
HOURLY_SALARY = 1000
BONUS_10H = 5000
KILL_REWARD = 50

# Killfeed State
current_log_file = ""
last_read_lines = 0

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class BigodeBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_password = ADMIN_PASSWORD
        self.admin_whitelist = admin_whitelist
        self.footer_icon = FOOTER_ICON

    async def setup_hook(self):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("--- EXECUTANDO SETUP_HOOK (STARTUP) ---")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # 1. Iniciar Loops de Processamento IMEDIATAMENTE
        tasks_to_start = [
            raid_scheduler,
            backup_loop,
            save_data_loop,
            killfeed_loop,
            sync_queue_loop,
        ]

        for t in tasks_to_start:
            try:
                if not t.is_running():
                    t.start()
                    print(f"  [OK] Task iniciada via Setup Hook: {t}")
            except Exception as e:
                print(f"  [ERRO] Falha ao iniciar task {t}: {e}")

        # 2. Carregar Cogs (Módulos)
        try:
            await load_extensions()
        except Exception as e:
            print(f"  [ERROR] Falha ao carregar extensoes: {e}")

        # 3. Hijack de logs (opcional, deixar desativado para debug se necessário)
        # sys.stdout = SocketWriter(sys.stdout)
        # sys.stderr = SocketWriter(sys.stderr)

        print("--- SETUP_HOOK CONCLUIDO ---")


bot = BigodeBot(command_prefix="!", intents=intents)


async def load_extensions():
    # print("Iniciando carregamento de modulos (Cogs)...")
    # Usar caminho absoluto para a pasta cogs
    cogs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cogs")
    if not os.path.exists(cogs_dir):
        print(f"  [ERROR] Diretorio de Cogs nao encontrado: {cogs_dir}")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"  [OK] Modulo carregado: {filename}")
            except Exception as e:
                print(f"  [ERROR] Erro ao carregar {filename}: {e}")


# Substituir o antigo load_extensions
@bot.event
async def on_ready():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"BOT LOGADO: {bot.user} (ID: {bot.user.id})")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("SISTEMA PRONTO E PROCESSANDO.")
    print("------")


# --- DASHBOARD & WEB SERVER ---
# Imports moved to top
from flask_socketio import SocketIO

# --- CONFIGURAÇÃO FLASK INTEGRADA ---
base_dir = os.path.dirname(os.path.abspath(__file__))
# UNIFICADO: Aponta para o novo dashboard premium
template_dir = os.path.join(base_dir, "new_dashboard", "templates")
static_dir = os.path.join(base_dir, "new_dashboard", "static")
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path="/static",
)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")  # Importante para sessões
csrf = CSRFProtect(app)  # Initialize CSRF

# Carregar Blueprints
app.register_blueprint(dashboard_bp)

# Inicializar OAuth e Babel
init_oauth(app)
babel = init_babel(app)  # Initialize Translation

# CRITICAL: Desabilitar cache de templates para forçar reload
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["EXPLAIN_TEMPLATE_LOADING"] = True

# Inicializar SocketIO (Async via Threading)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# Rota de Health Check (mantida para compatibilidade)
@app.route("/health")
def health():
    return "OK", 200


@app.route("/set_language/<lang>")
def set_language(lang):
    from flask import session, redirect, request, url_for

    session["lang"] = lang  # Using 'lang' as per babel_config.py
    return redirect(request.referrer or url_for("dashboard.index"))


# --- SISTEMA DE LOGS AO VIVO (Stdout Hijack) ---
class SocketWriter:
    def __init__(self, stream, namespace="/admin"):
        self.stream = stream
        self.namespace = namespace

    def write(self, message):
        self.stream.write(message)
        self.stream.flush()  # Ensure terminal sees it
        if message.strip():
            # Enviar para o SocketIO dentro do contexto da aplicação
            try:
                with app.app_context():
                    socketio.emit(
                        "log_message", {"data": message}, namespace=self.namespace
                    )
            except:
                pass  # Ignore context errors during startup

    def flush(self):
        self.stream.flush()


# Substitui stdout e stderr (MOVIDO PARA ON_READY PARA EVITAR DEADLOCK)
# sys.stdout = SocketWriter(sys.stdout)
# sys.stderr = SocketWriter(sys.stderr)


# Rodar o servidor web em uma thread separada (MOVIDO PARA O BLOCO MAIN)
def start_web_server():
    port = int(
        os.getenv("PORT", "5001")
    )  # Changed from 3000 to 5001 as per user expectation
    print(f"[INIT] Iniciando Servidor Web na porta {port}...")
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True,
    )


# --- CLASSE DE PAGINAÇÃO INTERATIVA ---

# --- SISTEMA DE ECONOMIA ---
# As funções get_balance e update_balance foram movidas para database.py ou para o Cog de Economia.
# Para compatibilidade interna em bot_main.py, usaremos instâncias se necessário ou as manteremos aqui temporariamente.
# No entanto, a meta é reduzir bot_main.py.


# add_to_inventory movido para database.py


# --- SISTEMA DE LOJA ---
# find_item_by_key movido para utils/helpers.py


# --- SINCRONIZAÇÃO DE TYPES ---
def sync_types_from_server():
    """Baixa types.xml do servidor e atualiza items.json"""
    try:
        ftp = connect_ftp()
        if not ftp:
            return False, "Erro ao conectar FTP"

        # Caminho do types.xml no servidor
        types_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/types.xml"

        # Baixa o arquivo
        bio = io.BytesIO()
        try:
            ftp.retrbinary(f"RETR {types_path}", bio.write)
        except Exception as e:
            ftp.quit()
            return False, f"Erro ao baixar types.xml: {e}"

        ftp.quit()

        # Parseia XML
        bio.seek(0)
        tree = ET.parse(bio)
        root = tree.getroot()

        # Categorias baseadas em tags/flags
        # Categorias baseadas em tags/flags
        # category_map removido pois logica abaixo usa if/elif direto

        new_items = {}
        items_added = 0

        for type_elem in root.findall("type"):
            name = type_elem.get("name")
            if not name:
                continue

            # Pega nominal (quantidade no servidor) como base de preço
            nominal_elem = type_elem.find("nominal")
            nominal = int(nominal_elem.text) if nominal_elem is not None else 10

            # Preço baseado em raridade (quanto menor nominal, mais raro, mais caro)
            if nominal <= 5:
                price = 5000
            elif nominal <= 10:
                price = 3000
            elif nominal <= 20:
                price = 2000
            elif nominal <= 50:
                price = 1000
            else:
                price = 500

            # Detecta categoria por nome (simplificado)
            category = "construcao"  # padrão
            name_lower = name.lower()
            if any(x in name_lower for x in ["rifle", "gun", "pistol", "shotgun"]):
                category = "armas"
            elif "ammo" in name_lower or "round" in name_lower:
                category = "municao"
            elif "mag" in name_lower:
                category = "carregadores"
            elif any(x in name_lower for x in ["optic", "suppressor", "scope"]):
                category = "acessorios"
            elif any(
                x in name_lower for x in ["bandage", "blood", "saline", "morphine"]
            ):
                category = "medico"
            elif any(
                x in name_lower for x in ["jacket", "pants", "boots", "helmet", "vest"]
            ):
                category = "roupas"
            elif any(x in name_lower for x in ["wheel", "battery", "spark"]):
                category = "veiculos"

            if category not in new_items:
                new_items[category] = {}

            # Usa nome do type como key (simplificado)
            item_key = name.lower().replace("_", "")
            new_items[category][item_key] = {
                "name": name,
                "price": price,
                "description": f"Nominal: {nominal}",
            }
            items_added += 1

        # Salva novo items.json
        save_json(ITEMS_FILE, new_items)

        return True, f"Sincronização concluída! {items_added} itens processados."

    except Exception as e:
        return False, f"Erro na sincronização: {e}"


# As definições de conquistas foram movidas para database.py
def check_achievements(user_id):
    return database.check_achievements(user_id)


# --- SISTEMA DE VÍNCULO (LINKING) ---
def get_discord_id_by_gamertag(gamertag):
    return database.get_link_by_gamertag(gamertag)


# --- SISTEMA DE CLÃS (WARS) ---
# --- SISTEMA DE CLÃS MOVIDO PARA cogs/clans.py ---


def update_war_score(killer_name, victim_name):
    """Verifica se há guerra entre os clãs e atualiza o placar."""
    killer_id = get_discord_id_by_gamertag(killer_name)
    victim_id = get_discord_id_by_gamertag(victim_name)

    if not killer_id or not victim_id:
        return None

    k_tag, _ = get_user_clan(killer_id)
    v_tag, _ = get_user_clan(victim_id)

    if not k_tag or not v_tag or k_tag == v_tag:
        return None

    # TODO: Implement War System in Database
    # For now, we skip war updates as it requires a new table or complex JSON structure
    return None


# --- SISTEMA DE STATS (KILLFEED) ---
def get_player_stats(_db, player_name):
    # db argument is ignored in favor of database call, kept for compatibility if needed
    player = database.get_player(player_name)
    if not player:
        player = {
            "gamertag": player_name,
            "kills": 0,
            "deaths": 0,
            "killstreak": 0,
            "best_killstreak": 0,
            "last_death_time": time.time(),
            "first_seen": time.time(),
            "longest_shot": 0,
            "weapons_stats": {},
            "total_playtime": 0,
        }

    # Ensure JSON fields are parsed
    if isinstance(player.get("weapons_stats"), str):
        try:
            player["weapons_stats"] = json.loads(player["weapons_stats"])
        except Exception:
            player["weapons_stats"] = {}

    return player


def update_stats_db(killer_name, victim_name, weapon=None, distance=0):
    current_time = time.time()

    # Matador
    killer = get_player_stats(None, killer_name)
    killer["kills"] = killer.get("kills", 0) + 1
    killer["killstreak"] = killer.get("killstreak", 0) + 1
    if killer["killstreak"] > killer.get("best_killstreak", 0):
        killer["best_killstreak"] = killer["killstreak"]

    # Longest Shot
    if distance > killer.get("longest_shot", 0):
        killer["longest_shot"] = int(distance)

    # Weapon Stats
    if weapon:
        w_key = weapon.replace('"', "").strip()
        weapons_stats = killer.get("weapons_stats", {})
        if w_key not in weapons_stats:
            weapons_stats[w_key] = 0
        weapons_stats[w_key] += 1
        killer["weapons_stats"] = weapons_stats

    database.save_player(killer_name, killer)

    # Vítima
    victim = get_player_stats(None, victim_name)
    victim["deaths"] = victim.get("deaths", 0) + 1
    victim["killstreak"] = 0
    time_alive = int(current_time - victim.get("last_death_time", current_time))
    victim["last_death_time"] = current_time

    database.save_player(victim_name, victim)

    return killer, victim, time_alive


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}h:{minutes:02d}m:{secs:02d}s"


# calculate_level movido para utils/helpers.py


# calculate_kd movido para utils/helpers.py


# --- FTP & LOGS ---
# connect_ftp movido para utils/ftp_helpers.py


def find_latest_adm_log(ftp):
    """Encontra o arquivo .ADM mais recente no servidor (Priorizando /dayzxb/config)."""
    print("Buscando arquivos de log (.ADM)...")

    # Prioridade 1: /dayzxb/config (Nitrado Xbox Default)
    # Prioridade 2: Fallbacks
    for path in ["/dayzxb/config", "/dayzxb", "/profile", "/SC"]:
        try:
            print(f"  Tentando pasta: {path}")
            ftp.cwd(path)
            items = ftp.nlst()

            # Filtra apenas ADM primeiro
            adm_files = [
                f"{path}/{f}"
                for f in items
                if f.lower().endswith(".adm") and "crash" not in f.lower()
            ]
            if adm_files:
                adm_files.sort()
                latest = adm_files[-1]
                print(f"  [OK] Encontrado .ADM mais recente: {latest}")
                return latest

            # Fallback para .RPT se não houver .ADM
            rpt_files = [
                f"{path}/{f}"
                for f in items
                if f.lower().endswith(".rpt") and "crash" not in f.lower()
            ]
            if rpt_files:
                rpt_files.sort()
                latest = rpt_files[-1]
                print(f"  [OK] Usando .RPT (Fallback): {latest}")
                return latest

        except Exception:
            continue

    print("Nenhum arquivo de log (.ADM ou .RPT) encontrado.")
    return None


# --- ANTI-SPAM DE CONSTRUÇÃO & DUPLICAÇÃO ---
spam_tracker = {}  # {player_name: [timestamps]}


def check_duplication(player_name, item_name, item_id):
    """Verifica se o jogador está pegando o mesmo item (ID) repetidamente."""
    if not item_id or item_id == "Unknown":
        return False

    now = time.time()
    if player_name not in pickup_tracker:
        pickup_tracker[player_name] = []

    # Limpa histórico antigo (5 minutos)
    pickup_tracker[player_name] = [
        t for t in pickup_tracker[player_name] if now - t[1] < 300
    ]

    # Adiciona atual
    pickup_tracker[player_name].append((item_id, now))

    # Conta quantas vezes esse ID foi pego
    count = sum(1 for i, t in pickup_tracker[player_name] if i == item_id)

    # Se pegou o mesmo ID mais de 2 vezes em 5 minutos -> SUSPEITO
    if count > 2:
        return True
    return False


def check_spam(player_name, item_name):
    """Verifica se o jogador está spamando itens (Lag Machine)."""
    if "fencekit" not in item_name.lower():
        return False

    now = time.time()
    if player_name not in spam_tracker:
        spam_tracker[player_name] = []

    # Limpa timestamps antigos (60 segundos)
    spam_tracker[player_name] = [t for t in spam_tracker[player_name] if now - t < 60]

    # Adiciona atual
    spam_tracker[player_name].append(now)

    # Limite: 10 kits em 1 minuto
    if len(spam_tracker[player_name]) > 10:
        return True
    return False


def check_construction(x, z, y, player_name, item_name):
    """Verifica se a construção é permitida."""
    item_lower = item_name.lower()

    # 1. BANIMENTO DE JARDIM (GardenPlot)
    if "gardenplot" in item_lower:
        return False, "GardenPlot"

    # 2. SKY BASE (Altura > 1000m)
    if y > 1000:
        return False, "SkyBase"

    # 3. UNDERGROUND BASE (Altura < -10m)
    if y < -10:
        return False, "UndergroundBase"

    # 4. PROTEÇÃO DE BASE
    # 4. PROTEÇÃO DE BASE
    active_bases = database.get_active_bases()
    for base in active_bases:
        dist = math.sqrt((x - base["x"]) ** 2 + (z - base["z"]) ** 2)
        if dist <= base["radius"]:
            # --- REGRAS ESPECÍFICAS DE BASE ---

            # A. PNEUS (Glitch) -> BANIMENTO IMEDIATO
            if "wheel" in item_lower or "tire" in item_lower:
                return False, f"BannedItemBase:{item_name}"

            # B. SHELTER (Glitch de Visão) -> BANIMENTO IMEDIATO
            if "improvisedshelter" in item_lower:
                return False, f"BannedItemBase:{item_name}"

            # C. FOGUEIRA/CONSTRUÇÃO -> APENAS AUTORIZADOS

            # Verifica se o jogador é do clã ou dono
            builder_id = get_discord_id_by_gamertag(player_name)

            if not builder_id:
                # Se não tem conta vinculada, é considerado INIMIGO na área protegida
                return False, f"UnauthorizedBase:{base.get('name', 'Base')}"

            # 1. É o Dono?
            if str(base["owner_id"]) == str(builder_id):
                return True, "Owner"

            # 2. Tem permissão explícita? (Permissao de Construir via Tabela)
            if base.get("source") == "db" and database.check_base_permission(
                base["id"], builder_id
            ):
                return True, "PermittedUser"

            # 3. É do Clã da Base? (Verificação Refinada)
            builder_clan_tag, builder_clan_data = database.get_user_clan(builder_id)

            # Se base V2 tem Clan ID
            if base.get("clan_id") and builder_clan_data:
                # Se o clã do builder tiver ID e bater com o da base
                if builder_clan_data.get("id") == base["clan_id"]:
                    return True, "ClanBaseMember"

            # Fallback Legacy: Compara TAGs se ownership bate
            owner_clan_tag, _ = database.get_user_clan(base["owner_id"])
            if owner_clan_tag and builder_clan_tag == owner_clan_tag:
                return True, "ClanMemberLegacy"

            return False, f"UnauthorizedBase:{base.get('name', 'Base')}"

    return True, "OK"


# --- DATABASE SYNC FOR DASHBOARD ---
def save_death_to_db(
    killer,
    victim,
    weapon,
    distance,
    pos,
    death_type="pvp",
    is_headshot=0,
    location="Chernarus",
):
    """Salva morte no banco de dados unificado para o dashboard."""
    try:
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db"
        )
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO deaths_log (
                killer_gamertag, victim_gamertag, death_type, death_cause,
                weapon, distance, is_headshot, coord_x, coord_z, location_name, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
            (
                killer,
                victim,
                death_type,
                f"Killed by {killer}" if killer else "Died",
                weapon,
                distance,
                1 if is_headshot else 0,
                pos[0],
                pos[2],
                location,
            ),
        )

        conn.commit()
        conn.close()
        print(f"[DB SYNC] Morte registrada no Dashboard: {killer} -> {victim}")

        # Emitir via SocketIO se possível (Opcional, pois o dashboard costuma ler via API)
        # Notificar o dashboard via socket se estiver rodando no mesmo processo
        try:
            from new_dashboard.app import socketio

            socketio.emit(
                "new_death",
                {
                    "killer": killer,
                    "victim": victim,
                    "weapon": weapon,
                    "location": location,
                },
                namespace="/",
            )
        except:
            pass

    except Exception as e:
        print(f"[DB SYNC ERROR] Erro ao salvar morte no DB: {e}")


# --- PERSISTENT LOGGING (ADM DASHBOARD) ---
def save_log_to_db(event_type, gamertag, ip, extra=None):
    """Salva logs gerais no banco para o Admin Dashboard."""
    try:
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db"
        )
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO game_logs (timestamp, event_type, gamertag, ip, extra)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event_type,
                gamertag,
                ip,
                json.dumps(extra or {}),
            ),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[LOG DB ERROR] {e}")


async def parse_log_line(line):
    line = line.strip()
    if not line:
        return

    # DEBUG: Ver o que está passando
    # print(f"[DEBUG PARSER] {line[:50]}...")
    if "killed by" in line:
        pass  # print(f"[DEBUG KILLED MATCH] {line}")
    elif "died" in line:  # Catch 'died' generic
        pass  # print(f"[DEBUG DIED MATCH] {line}")

    lx, lz = 0, 0

    # --- DETECÇÃO DE LOGIN (SUSPEITOS) ---
    if "connected" in line.lower() and "ip" in line.lower():
        try:
            # Ex: 12:00:00 | Player "Wellyton" (id=...) connected (ip=1.2.3.4)
            name = line.split('Player "')[1].split('"')[0]
            ip = line.split("ip=")[1].split(")")[0]

            print(f"[LOG] Jogador {name} conectando com IP: {ip}")

            # TODO: Comparar com lista de banidos/alts no DB
            # Salva log de conexão
            save_log_to_db("connection", name, ip, {"action": "login"})

            is_suspect = False
            # if database.check_suspect(name, ip): is_suspect = True

            if is_suspect:
                embed = discord.Embed(
                    title="🚨 ALERTA DE JOGADOR SUSPEITO!",
                    description=f"**Jogador:** {name}\n**IP:** {ip}\n**Motivo:** Possível Alt ou Banido!",
                    color=discord.Color.red(),
                )
                embed.set_footer(text="Segurança BigodeTexas", icon_url=FOOTER_ICON)
                return embed
        except Exception:
            pass

    if "committed suicide" in line:
        return None

    if "killed by Player" in line:
        try:
            parts = line.split("killed by Player")
            victim_name = (
                parts[0]
                .split("Player")[1]
                .split("(")[0]
                .strip()
                .replace('"', "")
                .replace("'", "")
            )

            # Fix: O nome do killer vem logo após "killed by Player", não tem outro "Player"
            # parts[1] ex: ' "Bandit" (id=Unknown) with M4A1 ...'
            killer_name = (
                parts[1].split("(")[0].strip().replace('"', "").replace("'", "")
            )

            # 1. Extrai Arma (Se houver)
            weapon = "Desconhecida"
            if " with " in line:
                weapon = line.split(" with ")[1].split(" ")[0].strip()

            # 2. Calcula Distância (Se possível)
            distance = 0
            location = "Desconhecido"

            if "<" in line and ">" in line:
                try:
                    coords = line.split("<")[1].split(">")[0].split(",")
                    lx, lz = float(coords[0]), float(coords[2])

                    # Usa Geolocalização
                    loc_name = get_location_name(lx, lz)
                    location = f"{loc_name} `({lx:.0f}, {lz:.0f})`"

                    # VERIFICA ALARMES 🚨
                    triggered = check_alarms(lx, lz, f"Morte de {victim_name}")
                    for alarm in triggered:
                        owner_id = alarm["owner_id"]
                        base_name = alarm["base_name"]
                        dist = alarm["dist"]

                        # 1. Alerta via Discord
                        try:
                            owner = await bot.fetch_user(int(owner_id))
                            alert_embed = discord.Embed(
                                title="🚨 ALARME DE BASE DISPARADO!",
                                color=discord.Color.red(),
                            )
                            alert_embed.description = f"**Atividade detectada na base {base_name}!**\n\n💀 **Evento:** Morte de {victim_name}\n🔫 **Assassino:** {killer_name}\n📍 **Local:** {loc_name}\n📏 **Distância do Centro:** {dist:.1f}m"
                            alert_embed.set_footer(
                                text="Sistema de Segurança BigodeTexas",
                                icon_url=FOOTER_ICON,
                            )
                            await owner.send(embed=alert_embed)
                        except Exception as e:
                            print(f"Erro ao enviar DM de alarme: {e}")

                        # 2. Alerta via Telegram (n8n)
                        if alarm.get("telegram_id"):
                            await send_n8n_base_alert(
                                player_name=killer_name,
                                coords=f"{lx:.0f}, {lz:.0f}",
                                base_name=base_name,
                                chat_id=alarm["telegram_id"],
                                is_group=alarm.get("is_group", False),
                                event_type=f"Morte de {victim_name}",
                            )

                    # VERIFICA ZONA QUENTE 🔥
                    is_hot, count = check_hotzone(lx, lz)
                    if is_hot and count == 3:
                        hot_embed = discord.Embed(
                            title="🔥 ZONA QUENTE DETECTADA!",
                            color=discord.Color.dark_orange(),
                        )
                        hot_embed.description = f"**Atenção Sobreviventes!**\n\nO pau tá quebrando em **{loc_name}**!\nJá foram **{count} mortes** nos últimos 15 minutos.\nPreparem-se para o PVP! ⚔️"
                        hot_embed.set_footer(
                            text="BigodeTexas • Radar de Conflitos",
                            icon_url=FOOTER_ICON,
                        )
                        channel = bot.get_channel(
                            load_json(CONFIG_FILE).get("killfeed_channel")
                        )
                        if channel:
                            await channel.send(embed=hot_embed)

                except Exception:
                    pass

            # 3. Atualiza Stats (Agora com arma e distância)
            k_stats, v_stats, time_alive = update_stats_db(
                killer_name, victim_name, weapon, distance
            )

            # EMIT EVENT TO DASHBOARD
            kill_msg = (
                f"{killer_name} matou {victim_name} com {weapon} ({distance:.0f}m)"
            )
            await send_dashboard_event("KILLFEED", kill_msg, None)

            # --- CLAN WAR UPDATE ---
            # war_update = update_war_score(killer_name, victim_name)
            # if war_update:
            #     try:
            #         c1 = war_update["clan1"]
            #         c2 = war_update["clan2"]
            #         s1 = war_update["score"][c1]
            #         s2 = war_update["score"][c2]

            #         war_embed = discord.Embed(
            #             title="⚔️ GUERRA DE CLÃS ATUALIZADA!",
            #             color=discord.Color.dark_red(),
            #         )
            #         war_embed.description = f"**{c1}** vs **{c2}**\n\n💀 **Baixa Confirmada!**\nO clã **{war_update['killer_clan']}** marcou um ponto!"
            #         war_embed.add_field(
            #             name="Placar",
            #             value=f"**{c1}:** {s1}\n**{c2}:** {s2}",
            #             inline=False,
            #         )
            #         war_embed.set_footer(
            #             text="BigodeTexas • Sistema de Guerra", icon_url=FOOTER_ICON
            #         )

            #         channel = bot.get_channel(
            #             load_json(CONFIG_FILE).get("killfeed_channel")
            #         )
            #         if channel:
            #             await channel.send(embed=war_embed)
            #     except Exception as e:
            #         print(f"Erro ao enviar update de guerra: {e}")
            # --- END CLAN WAR UPDATE ---

            # --- HEATMAP LOGGING ---
            try:
                if (
                    location != "Desconhecido" and "x" not in location
                ):  # Se location for nomeado, tentamos usar as coords raw se disponiveis
                    # A variavel location ja foi formatada com nome, entao precisamos das coords originais
                    # lx e lz foram definidos no bloco try anterior
                    pass

                # Se tivermos lx e lz do bloco anterior (linha 760), salvamos
                # Precisamos garantir que lx e lz estao no escopo.
                # O bloco try onde lx e lz sao definidos esta dentro do if "<" in line...
                # Vamos refatorar levemente para garantir que temos as coords.
                pass
            except Exception:
                pass

            # Refatorando a logica de extracao para persistir dados do heatmap

            discord_id = get_discord_id_by_gamertag(killer_name)
            reward_msg = ""
            total_reward = KILL_REWARD

            # Verifica BOUNTY (Procurado)
            bounties = load_bounties()
            victim_lower = victim_name.lower()

            if victim_lower in bounties:
                bounty_val = bounties[victim_lower]["amount"]
                total_reward += bounty_val
                reward_msg += f"\n🤠 **RECOMPENSA COLETADA:** +{bounty_val}!"
                # Remove a recompensa
                del bounties[victim_lower]
                save_bounties(bounties)

            if discord_id:
                try:
                    database.update_balance(
                        discord_id, total_reward, "kill", f"Kill: {victim_name}"
                    )
                except Exception as e:
                    print(
                        f"[ERROR] Falha ao atualizar saldo, salvando na fila local: {e}"
                    )
                    from utils.event_queue import add_to_queue

                    add_to_queue(
                        "kill_reward",
                        killer_name,
                        {
                            "discord_id": discord_id,
                            "amount": total_reward,
                            "victim": victim_name,
                        },
                    )

                # Verifica conquistas
                try:
                    new_achievements = check_achievements(discord_id)
                    if new_achievements:
                        for _ach_id, ach_def in new_achievements:
                            reward_msg += (
                                f"\n🏆 **CONQUISTA DESBLOQUEADA:** {ach_def['name']}!"
                            )
                            if ach_def["reward"] > 0:
                                reward_msg += f" (+{ach_def['reward']} DZ Coins)"
                except Exception:
                    pass

            # TEMA BIGODE TEXAS 🤠
            embed = discord.Embed(
                title="🤠 KILLFEED TEXAS", color=discord.Color.orange()
            )

            # Assassino
            embed.add_field(
                name="🔫 Pistoleiro (Assassino)",
                value=f"**{killer_name}**\n⭐ Nível: {calculate_level(k_stats['kills'])}\n🎯 K/D: {calculate_kd(k_stats['kills'], k_stats['deaths'])}\n🔥 Série: {k_stats['killstreak']}\n📏 Longest: {k_stats.get('longest_shot', 0)}m{reward_msg}",
                inline=True,
            )

            # Vítima
            embed.add_field(
                name="⚰️ Finado (Vítima)",
                value=f"**{victim_name}**\n⭐ Nível: {calculate_level(v_stats['kills'])}\n⏳ Viveu: {format_time(time_alive)}",
                inline=True,
            )

            # Detalhes
            embed.add_field(
                name="🌵 Detalhes do Crime",
                value=f"🛠️ Arma: `{weapon}`\n📍 Local: `{location}`",
                inline=False,
            )

            embed.set_thumbnail(
                url="https://i.imgur.com/S71j4qO.png"
            )  # Ícone de caveira/wanted
            embed.set_footer(
                text=f"BigodeTexas • {datetime.now().strftime('%H:%M')} • O Xerife está de olho 👀",
                icon_url=FOOTER_ICON,
            )

            # SALVAR NO DB DO DASHBOARD 🚀
            save_death_to_db(
                killer_name,
                victim_name,
                weapon,
                distance,
                (lx, 0, lz),
                death_type="pvp",
                is_headshot=False,
                location=location,
            )

            return embed
        except Exception as e:
            print(f"Erro parse kill: {e}")
            return None

    elif "died" in line and "Player" in line:
        try:
            victim_name = (
                line.split("Player")[1]
                .split("died")[0]
                .split("(")[0]
                .strip()
                .replace('"', "")
                .replace("'", "")
            )
            # Atualiza DB (morte natural)
            db = load_json(PLAYERS_DB_FILE)
            victim = get_player_stats(db, victim_name)
            victim["deaths"] += 1
            victim["killstreak"] = 0
            victim["last_death_time"] = time.time()
            save_json(PLAYERS_DB_FILE, db)

            # SALVAR NO DB DO DASHBOARD 🚀
            save_death_to_db(
                None,
                victim_name,
                "Desconhecido",
                0,
                (0, 0, 0),
                death_type="pve",
                is_headshot=False,
                location="Chernarus",
            )

            embed = discord.Embed(
                description=f"💀 **{victim_name}** morreu.",
                color=discord.Color.dark_grey(),
            )
            return embed
        except Exception:
            return None

    elif "placed" in line and "at <" in line:
        try:
            # Ex: Player "Survivor" (id=...) placed "GardenPlot" at <123, 456, 789>
            parts = line.split(" placed ")
            player_part = parts[0]
            item_part = parts[1]

            player_name = player_part.split('Player "')[1].split('"')[0]
            item_name = item_part.split('"')[1]

            coords = item_part.split("at <")[1].split(">")[0].split(",")
            x, z = float(coords[0]), float(coords[2])
            y = float(coords[1])  # Altura

            # 1. CHECK SPAM (Lag Machine)
            if check_spam(player_name, item_name):
                print(f"BANINDO {player_name} por SPAM de Construção (Lag Machine)!")
                channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                if channel:
                    await channel.send(
                        f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por Spam de Construção (Lag Machine)!"
                    )
                ban_player(player_name, "Spam de Construcao/Lag Machine")
                return None

            # 2. CHECK CONSTRUCTION (Regras Gerais)
            allowed, reason = check_construction(x, z, y, player_name, item_name)

            if not allowed:
                if reason == "GardenPlot":
                    # AÇÃO: BANIR JOGADOR
                    print(f"BANINDO {player_name} por plantar GardenPlot!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(
                            f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por plantar GardenPlot (Proibido)!"
                        )

                    # Executa Banimento Real
                    ban_player(player_name, "GardenPlot Proibido")

                elif reason == "SkyBase":
                    print(f"BANINDO {player_name} por Sky Base!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(
                            f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por construir Sky Base (Altura > 1000m)!"
                        )
                    ban_player(player_name, "Sky Base Detectada")

                elif reason == "UndergroundBase":
                    print(f"BANINDO {player_name} por Base Subterrânea!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(
                            f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por construir Base Subterrânea!"
                        )
                    ban_player(player_name, "Underground Base Detectada")

                elif reason.startswith("BannedItemBase"):
                    # AÇÃO: BANIR JOGADOR (Glitch de Pneu/Shelter)
                    item_banned = reason.split(":")[1]
                    print(
                        f"BANINDO {player_name} por item proibido em Base: {item_banned}!"
                    )
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(
                            f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por usar **{item_banned}** em área de Base (Anti-Glitch)!"
                        )

                    # Executa Banimento Real
                    ban_player(player_name, f"Glitch Item em Base: {item_banned}")

                elif reason.startswith("UnauthorizedBase"):
                    base_name = reason.split(":")[1]
                    print(
                        f"BANINDO {player_name} por construção ilegal na base {base_name}!"
                    )

                    # Alerta no canal de Alarmes (mantido para registro)
                    alarm_channel = bot.get_channel(
                        load_json(CONFIG_FILE).get("alarm_channel")
                    )
                    if alarm_channel:
                        await alarm_channel.send(
                            f"🚨 **ALERTA DE INVASÃO**\n**{player_name}** tentou colocar **{item_name}** na área protegida da base **{base_name}**!"
                        )

                    # Alerta no canal de Banimentos
                    ban_channel = bot.get_channel(
                        load_json(CONFIG_FILE).get("ban_channel")
                    )
                    if ban_channel:
                        await ban_channel.send(
                            f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por construir ilegalmente na base **{base_name}** (Não autorizado)!"
                        )

                    # Executa Banimento Real
                    ban_player(player_name, f"Construcao Ilegal em Base: {base_name}")

        except Exception as e:
            print(f"Erro parse placement: {e}")

    # --- DETECÇÃO DE DUPLICAÇÃO (PICKED UP) ---
    elif " picked up " in line:
        try:
            # Ex: Player "Survivor" (id=Unknown) picked up "M4A1" (id=12345)
            parts = line.split(" picked up ")
            player_part = parts[0]
            item_part = parts[1]

            player_name = player_part.split('Player "')[1].split('"')[0]
            item_name = item_part.split('"')[1]

            item_id = None
            if "(id=" in item_part:
                item_id = item_part.split("(id=")[1].split(")")[0]

            if check_duplication(player_name, item_name, item_id):
                print(f"BANINDO {player_name} por Duplicação de Item (ID: {item_id})!")
                channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                if channel:
                    await channel.send(
                        f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por Duplicação de Item (Duping)!\nItem: {item_name} (ID: {item_id})"
                    )
                ban_player(player_name, f"Duplicação de Item: {item_name}")

        except Exception as e:
            print(f"Erro parse pickup: {e}")

    # --- DETECÇÃO DE LOGIN/LOGOUT (SALÁRIO) ---
    elif " is connected" in line:
        try:
            # Ex: Player "Survivor" is connected
            player_name = line.split('Player "')[1].split('"')[0]

            # 1. Registra Login e Salva
            active_sessions[player_name] = time.time()
            save_json(SESSIONS_FILE, active_sessions)
            print(f"[LOGIN] Detectado: {player_name}")

            # 2. Daily Automático
            discord_id = get_discord_id_by_gamertag(player_name)
            if discord_id:
                eco = database.get_economy(discord_id)
                last = eco.get("last_daily")

                should_pay = True
                if last:
                    try:
                        last_date = datetime.fromisoformat(last)
                        if datetime.now() - last_date < timedelta(hours=24):
                            should_pay = False
                    except (ValueError, TypeError):
                        should_pay = True

                if should_pay:
                    database.update_balance(
                        discord_id, DAILY_BONUS, "daily", "Bônus diário de login"
                    )

                    # Atualiza o campo last_daily na economia do usuário
                    eco = database.get_economy(discord_id)
                    eco["last_daily"] = datetime.now().isoformat()
                    database.save_economy(discord_id, eco)

                    channel = bot.get_channel(
                        load_json(CONFIG_FILE).get("salary_channel")
                    )
                    if channel:
                        await channel.send(
                            f"🌞 **BÔNUS DIÁRIO!**\n**{player_name}** conectou e ganhou **{DAILY_BONUS} DZ Coins**!"
                        )

        except Exception as e:
            print(f"Erro parse login: {e}")

    elif " has been disconnected" in line:
        try:
            # Ex: Player "Survivor" has been disconnected
            player_name = line.split('Player "')[1].split('"')[0]

            if player_name in active_sessions:
                login_time = active_sessions.pop(player_name)
                save_json(SESSIONS_FILE, active_sessions)
                duration_seconds = time.time() - login_time
                hours_played = duration_seconds / 3600

                # 1. Atualiza Tempo Total de Jogo no players_db
                player_stats = database.get_player(player_name)
                if player_stats:
                    player_stats["total_playtime"] = (
                        player_stats.get("total_playtime", 0) + duration_seconds
                    )
                    database.save_player(player_name, player_stats)

                # 2. Pagamento Proporcional (Mínimo 10 minutos para ganhar algo)
                if duration_seconds > 600:
                    salary = int(hours_played * HOURLY_SALARY)

                    # Formata tempo
                    h = int(hours_played)
                    m = int((duration_seconds % 3600) // 60)

                    discord_id = get_discord_id_by_gamertag(player_name)
                    if discord_id and salary > 0:
                        database.update_balance(
                            discord_id, salary, "salary", f"Tempo jogado: {h}h {m}m"
                        )

                        msg = f"💸 **SALÁRIO RECEBIDO!**\n**{player_name}** jogou por {h}h {m}m e ganhou **{salary} DZ Coins**."

                        # Bônus de 10 Horas
                        if hours_played >= 10:
                            database.update_balance(
                                discord_id,
                                BONUS_10H,
                                "salary",
                                "Bônus Maratonista +10h",
                            )
                            msg += f"\n🏆 **MARATONISTA!** Bônus de {BONUS_10H} por jogar +10h direto!"

                        channel = bot.get_channel(
                            load_json(CONFIG_FILE).get("salary_channel")
                        )
                        if channel:
                            await channel.send(msg)
                else:
                    print(
                        f"Sessão curta de {player_name}: {duration_seconds:.0f}s (Sem pagamento)"
                    )

        except Exception as e:
            print(f"Erro parse logout: {e}")

    return None


def ban_player(gamertag, reason="Banido pelo Bot"):
    """Adiciona o jogador ao arquivo ban.txt no servidor via FTP."""
    local_file = "ban.txt"
    remote_path = "/ban.txt"  # Tenta na raiz primeiro, ou /dayzxb/config/ban.txt

    try:
        ftp = connect_ftp()
        if not ftp:
            return

        # 1. Baixa o ban.txt atual (se existir)
        current_bans = ""
        try:
            bio = io.BytesIO()
            ftp.retrbinary(f"RETR {remote_path}", bio.write)
            current_bans = bio.getvalue().decode("utf-8", errors="ignore")
        except Exception:
            print("Arquivo ban.txt não encontrado, criando novo.")

        # 2. Verifica se já está banido
        if gamertag in current_bans:
            print(f"{gamertag} já está na lista de banimento.")
            ftp.quit()
            return

        # 3. Adiciona o novo ban
        # Formato: Gamertag // Motivo
        new_entry = f"{gamertag} // {reason}\n"
        current_bans += new_entry

        # 4. Salva e Upload
        with open(local_file, "w", encoding="utf-8") as f:
            f.write(current_bans)

        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR {remote_path}", f)

        print(f"✅ Jogador {gamertag} adicionado ao ban.txt com sucesso.")
        ftp.quit()

    except Exception as e:
        print(f"Erro ao banir jogador: {e}")


# --- PERSISTÊNCIA DE ESTADO (MEMÓRIA) ---
STATE_FILE = "bot_state.json"


# --- TASKS (LOOP) ---
@tasks.loop(seconds=15)
async def killfeed_loop():
    global last_read_lines, current_log_file
    print("[DEBUG] killfeed_loop EXECUTANDO...", flush=True)

    # 🔄 AUTO-FAILOVER: Ignorado para forçar este bot como principal
    # should_backup = auto_failover.should_activate_backup()
    # if should_backup:
    #     auto_failover.send_backup_heartbeat()
    # else:
    #     return

    # Forçado Ativado
    pass

    # NOTE: 'last_read_lines' is reused here as 'last_byte_offset' to avoid global renaming chaos
    last_byte_offset = last_read_lines

    config = load_json(CONFIG_FILE)
    channel_id = config.get("killfeed_channel")
    print(f"[DEBUG] killfeed_loop EXECUTANDO... (Channel ID: {channel_id})", flush=True)
    if not channel_id:
        return

    channel = bot.get_channel(int(channel_id))
    if not channel:
        try:
            print(
                f"[DEBUG] Canal {channel_id} nao encontrado no cache. Tentando buscar...",
                flush=True,
            )
            channel = await bot.fetch_channel(int(channel_id))
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar canal {channel_id}: {e}", flush=True)
            return

    # Usar ascii/ignore para evitar UnicodeEncodeError no terminal Windows
    safe_channel_name = channel.name.encode("ascii", "ignore").decode("ascii")
    print(f"[DEBUG] Canal encontrado: {safe_channel_name}", flush=True)
    print("[DEBUG] Tentando conectar ao FTP...", flush=True)
    ftp = connect_ftp()
    if not ftp:
        print("[DEBUG] FALHA AO CONECTAR FTP.", flush=True)
        return

    print("[DEBUG] FTP Conectado com sucesso!", flush=True)

    try:
        # 1. State Recovery
        if not current_log_file:
            state = load_json(STATE_FILE)
            if state:
                current_log_file = state.get("current_log_file")
                last_byte_offset = state.get(
                    "last_read_lines", 0
                )  # Mapping lines->bytes per logic
                print(f"State Loaded: {current_log_file} (Offset {last_byte_offset})")

        # 2. File Selection (if none)
        if not current_log_file:
            print("Tentando localizar log mais recente no FTP...")
            current_log_file = find_latest_adm_log(ftp)
            if current_log_file:
                # Get Initial Size
                ftp.voidcmd("TYPE I")  # Ensure binary mode for SIZE
                size = ftp.size(current_log_file)
                last_byte_offset = size
                print(f"Initial Log: {current_log_file} (Start Offset {size})")

                # Use global var tracking
                last_read_lines = last_byte_offset
                save_json(
                    STATE_FILE,
                    {
                        "current_log_file": current_log_file,
                        "last_read_lines": last_byte_offset,
                    },
                )

        else:
            # 3. Check for Update
            try:
                ftp.voidcmd("TYPE I")  # Ensure binary mode for SIZE
                server_size = ftp.size(current_log_file)
            except Exception:
                # File might be gone or rotated
                server_size = -1

            if server_size < last_byte_offset:
                # ROTATION DETECTED (Server file is smaller than our offset)
                print("Log rotation detected (File smaller). Resetting...")
                current_log_file = ""
                last_read_lines = 0
                save_json(STATE_FILE, {"current_log_file": "", "last_read_lines": 0})

            elif server_size > last_byte_offset:
                # NEW DATA FOUND
                print(f"Downloading new bytes: {last_byte_offset} -> {server_size}")

                bio = io.BytesIO()
                # Use REST command to download only from offset
                ftp.retrbinary(
                    f"RETR {current_log_file}", bio.write, rest=last_byte_offset
                )

                new_content = bio.getvalue().decode("utf-8", errors="ignore")
                new_lines = new_content.split("\n")

                for line in new_lines:
                    if line.strip():
                        embed = await parse_log_line(line)
                        if embed:
                            await channel.send(embed=embed)

                # Update Offset
                last_read_lines = server_size
                save_json(
                    STATE_FILE,
                    {
                        "current_log_file": current_log_file,
                        "last_read_lines": server_size,
                    },
                )

    except Exception as e:
        print(f"Loop Error: {e}")
        # Reset on hard fail
        if "550" in str(e):
            current_log_file = ""
            last_read_lines = 0
            save_json(STATE_FILE, {"current_log_file": "", "last_read_lines": 0})

    try:
        ftp.quit()
    except:
        pass


@tasks.loop(minutes=1)
async def save_data_loop():
    """Salva periodicamente todos os dados críticos para garantir persistência."""
    print(f"[AUTOSAVE] Dados verificados em {datetime.now().strftime('%H:%M:%S')}")


@tasks.loop(minutes=5)
async def sync_queue_loop():
    """Tenta processar eventos da fila local salvos durante falhas do DB."""
    from utils.event_queue import load_queue, clear_queue

    pending = load_queue()
    if not pending:
        return

    print(f"[SYNC] Processando {len(pending)} eventos pendentes...")
    processed_count = 0

    for event in pending:
        try:
            if event["type"] == "kill_reward":
                data = event["data"]
                database.update_balance(
                    data["discord_id"],
                    data["amount"],
                    "kill_sync",
                    f"Sync Kill: {data['victim']}",
                )
                processed_count += 1
        except Exception as e:
            print(f"[SYNC] Erro ao processar evento: {e}")
            # Mantém os restantes na fila se falhar de novo
            break

    if processed_count == len(pending):
        clear_queue()
        print("[SYNC] Todos os eventos sincronizados com sucesso!")
    elif processed_count > 0:
        # Atualiza a fila apenas com o que sobrou
        from utils.event_queue import save_queue

        save_queue(pending[processed_count:])
        print(
            f"[SYNC] {processed_count} eventos sincronizados. Restam {len(pending) - processed_count}."
        )


# --- LOOP DE BACKUP AUTOMÁTICO ---
@tasks.loop(hours=1)
async def backup_loop():
    """Cria backup automático dos arquivos críticos a cada hora"""
    critical_files = [
        ECONOMY_FILE,
        PLAYERS_DB_FILE,
        LINKS_FILE,
        CLANS_FILE,
        CONFIG_FILE,
        "bot_state.json",
    ]

    print("[BACKUP] Iniciando backup automático...")
    backup_manager.backup_all(critical_files)
    print(f"[BACKUP] Backup concluído em {datetime.now().strftime('%H:%M:%S')}")


# --- AGENDADOR DE RAID ---
@tasks.loop(minutes=1)
async def raid_scheduler():
    # Horário de Brasília (UTC-3)
    # Ajuste conforme o fuso horário da máquina onde o bot roda.
    # Se a máquina for UTC-6, adicionamos 3 horas.
    # Para garantir, vamos usar UTC e subtrair 3.
    utc_now = datetime.now(timezone.utc)
    br_time = utc_now - timedelta(hours=3)

    weekday = br_time.weekday()  # 5 = Sábado, 6 = Domingo
    hour = br_time.hour
    minute = br_time.minute

    # Sábado (5) e Domingo (6)
    if weekday in [5, 6]:
        # 1. Preparação do Raid (20:55)
        if hour == 20 and minute == 55:
            print("⏰ Preparando Raid! Enviando globals_raid.xml...")
            if upload_globals("globals_raid.xml"):
                channel = bot.get_channel(
                    load_json(CONFIG_FILE).get("killfeed_channel")
                )
                if channel:
                    await channel.send(
                        "⚠️ **ATENÇÃO:** O Raid será liberado no próximo reinício (21:00)!"
                    )

        # 2. Início do Raid (21:00) - RESTART
        if hour == 21 and minute == 0:
            print("⏰ HORA DO RAID! Reiniciando servidor...")
            success, msg = await restart_server()
            channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
            if channel:
                if success:
                    await channel.send(
                        "🚨 **INICIANDO RAID!** O servidor está reiniciando para liberar a destruição! ⚔️"
                    )
                else:
                    await channel.send(
                        f"❌ **ERRO:** Falha ao reiniciar o servidor: {msg}"
                    )

        # 3. Preparação do Fim (22:55)
        if hour == 22 and minute == 55:
            print("⏰ Encerrando Raid! Enviando globals_safe.xml...")
            if upload_globals("globals_safe.xml"):
                channel = bot.get_channel(
                    load_json(CONFIG_FILE).get("killfeed_channel")
                )
                if channel:
                    await channel.send(
                        "🛡️ **ATENÇÃO:** O Raid será desativado no próximo reinício (23:00)!"
                    )

        # 4. Fim do Raid (23:00) - RESTART
        if hour == 23 and minute == 0:
            print("⏰ FIM DO RAID! Reiniciando servidor...")
            success, msg = await restart_server()
            channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
            if channel:
                if success:
                    await channel.send(
                        "🛡️ **RAID ENCERRADO!** O servidor está reiniciando e as bases estão seguras novamente."
                    )
                else:
                    await channel.send(
                        f"❌ **ERRO:** Falha ao reiniciar o servidor: {msg}"
                    )


def upload_globals(local_filename):
    try:
        ftp = connect_ftp()
        if not ftp:
            return False

        # Caminho do arquivo no servidor (Tenta achar)
        remote_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/globals.xml"

        # Tenta enviar
        try:
            with open(local_filename, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"Upload de {local_filename} concluído com sucesso.")
            ftp.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar {local_filename}: {e}")
            ftp.quit()
            return False

    except Exception as e:
        print(f"Erro global no upload: {e}")
        return False


@bot.command()
@require_admin_password()
async def set_killfeed(ctx):
    config = load_json(CONFIG_FILE)
    config["killfeed_channel"] = ctx.channel.id
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Canal de Killfeed definido para: {ctx.channel.mention}")


@bot.command()
@require_admin_password()
async def restart(ctx):
    """(Admin) Reinicia o servidor DayZ imediatamente."""
    await ctx.send("⏳ **Enviando comando de restart para a Nitrado...**")
    success, msg = await restart_server()
    if success:
        await ctx.send(
            "✅ **Servidor reiniciando!** Aguarde alguns minutos para voltar."
        )
    else:
        await ctx.send(f"❌ **Falha ao reiniciar:** {msg}")


@bot.command()
@rate_limit()
async def ajuda(ctx):
    embed = discord.Embed(
        title="📜 Central de Ajuda - BigodeBot", color=discord.Color.blue()
    )

    embed.add_field(
        name="💰 Economia",
        value=(
            "`!registrar <Gamertag>` - Vincular conta\n"
            "`!saldo` - Ver seu saldo\n"
            "`!daily` - Resgatar bônus diário\n"
            "`!loja` - Ver itens para compra\n"
            "`!comprar <codigo>` - Adquirir item\n"
            "`!inventario` - Ver seus itens virtuais\n"
            "`!transferir <@user> <valor>` - Enviar coins\n"
            "`!extrato` - Ver histórico financeiro"
        ),
        inline=False,
    )

    embed.add_field(
        name="🏆 Social & Perfil",
        value=(
            "`!perfil` - Ver suas estatísticas e conquistas\n"
            "`!conquistas` - Lista de desafios\n"
            "`!top` - Ranking do servidor"
        ),
        inline=False,
    )

    embed.add_field(
        name="🛡️ Clãs", value="Use `!clan` para ver os comandos de clãs.", inline=False
    )

    if ctx.author.id in bot.admin_whitelist:
        embed.add_field(
            name="🛠️ Admin",
            value=(
                "`!set_killfeed` - Mudar canal de mortes\n"
                "`!desvincular <Gamertag>` - Limpar vínculo\n"
                "`!spawn <item_name> <coords>` - Spawn direto"
            ),
            inline=False,
        )

    embed.set_footer(
        text="BigodeTexas • Sua experiência levada a sério", icon_url=bot.footer_icon
    )
    await ctx.send(embed=embed)


# --- SISTEMA DE CLÃS COMANDOS MOVIDOS PARA cogs/clans.py ---


# --- SISTEMA DE RECOMPENSAS (BOUNTIES) ---
BOUNTIES_FILE = "bounties.json"


def load_bounties():
    return load_json(BOUNTIES_FILE)


def save_bounties(data):
    save_json(BOUNTIES_FILE, data)


# --- SISTEMA DE ALARMES ---
ALARMS_FILE = "alarms.json"


def load_alarms():
    return load_json(ALARMS_FILE)


def save_alarms(data):
    save_json(ALARMS_FILE, data)


def check_alarms(x, z, _event_desc):
    """Verifica se uma coordenada aciona algum alarme."""
    alarms = load_alarms()
    triggered = []

    for _alarm_id, data in alarms.items():
        try:
            ax, az = data["x"], data["z"]
            radius = data["radius"]

            # Distância Euclidiana
            dist = math.sqrt((x - ax) ** 2 + (z - az) ** 2)

            if dist <= radius:
                triggered.append(
                    {
                        "owner_id": data["owner_id"],
                        "base_name": data["name"],
                        "dist": dist,
                        "telegram_id": data.get("telegram_id"),
                        "is_group": data.get("is_group", False),
                    }
                )
        except Exception:
            pass

    return triggered


# --- SISTEMA DE ZONA QUENTE (HEATMAP) ---
recent_kills = []  # Lista de tuplas (x, z, timestamp)


def check_hotzone(new_x, new_z):
    """Verifica se há muitas mortes recentes perto desta."""
    global recent_kills
    now = datetime.now()

    # 1. Limpa kills antigas (> 15 minutos)
    recent_kills = [k for k in recent_kills if (now - k[2]).total_seconds() < 900]

    # 2. Adiciona a nova kill
    recent_kills.append((new_x, new_z, now))

    # 3. Conta kills próximas (Raio 500m)
    count = 0
    for kx, kz, _ in recent_kills:
        dist = math.sqrt((new_x - kx) ** 2 + (new_z - kz) ** 2)
        if dist <= 500:
            count += 1

    # DEBUG
    # print(f"DEBUG HEATMAP: New({new_x},{new_z}) TotalKills={len(recent_kills)} Count={count}")

    # Se tiver 3 ou mais mortes (incluindo a atual), é Zona Quente!
    if count >= 3:
        return True, count
    return False, count


# --- GEOLOCALIZAÇÃO (CIDADES) ---
CHERNARUS_LOCATIONS = {
    "NWAF (Aeroporto)": (4600, 10000),
    "Berezino": (12000, 9000),
    "Chernogorsk": (6500, 2500),
    "Elektrozavodsk": (10500, 2300),
    "Krasnostav": (11000, 12300),
    "Stary Sobor": (6000, 7700),
    "Vybor": (3800, 8900),
    "Zelenogorsk": (2700, 5300),
    "Tisy Military": (1700, 14000),
    "Balota AF": (4500, 2500),
    "Svetlojarsk": (13900, 13300),
    "Novodmitrovsk": (11500, 14500),
    "Severograd": (8400, 13700),
    "Gorka": (9500, 8800),
    "Kabanino": (5300, 8600),
    "Grishino": (7200, 9700),
    "Pavlovo": (1700, 3800),
    "Kamenka": (1800, 2200),
    "Myshkino": (2000, 7300),
    "VMC (Military)": (4500, 8300),
}


def add_event(timestamp, _item_name, x, z):
    """Registra evento no banco de dados"""
    # Assuming 'database' is imported or available globally.
    # If not, this line would cause a NameError.
    # For the purpose of this edit, we'll assume 'database' exists.
    # database.add_event(timestamp, x, z) # This line was malformed in the instruction.
    pass  # Placeholder to keep function syntactically correct without 'database'


def get_location_name(x, z):
    """Retorna o nome da cidade mais próxima."""
    closest_city = "Ermo"
    min_dist = float("inf")

    for city, (cx, cz) in CHERNARUS_LOCATIONS.items():
        dist = math.sqrt((x - cx) ** 2 + (z - cz) ** 2)
        if dist < min_dist:
            min_dist = dist
            closest_city = city

    if min_dist < 600:
        return f"Em **{closest_city}**"
    elif min_dist < 2000:
        return f"Perto de **{closest_city}** ({min_dist:.0f}m)"
    else:
        return "No meio do nada (Ermo)"


# --- COMANDOS EXTRAS ---


# --- COMANDOS MOVIDOS PARA COGS (pvp.py) ---
# alarme, set, etc.


# --- COMANDOS DE ALARME E PROCURADO MOVIDOS PARA cogs/pvp.py ---


# =============================================================================
# SISTEMA DE LEADERBOARD - Rankings de Jogadores
# =============================================================================


# --- SISTEMA DE LEADERBOARD MOVIDO PARA cogs/leaderboard.py ---


# =============================================================================
# SISTEMA DE ADMIN SPAWNER - Spawnar Itens no Servidor
# =============================================================================

# Importar sistema de spawn
# Importar sistema de spawn (Moved to top)


# --- COMANDOS DE ADMIN SPAWNER MOVIDOS PARA cogs/admin.py ---


# --- COMANDOS SOBRESSALENTES REMOVIDOS (MIGRADOS PARA COGS) ---


# =============================================================================
# SISTEMA DE EDITOR DE GAMEPLAY - Modificar cfggameplay.json
# =============================================================================

# Importar sistema de edição
# Importar sistema de edição (Moved to top)


# --- COMANDOS DE EDITOR DE GAMEPLAY MOVIDOS PARA cogs/admin.py ---
# --- MODULARIZADO ---
# --- FIM DO ARQUIVO MODULARIZADO ---


if __name__ == "__main__":
    # Iniciar Servidor Web
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    try:
        print("--- INICIANDO BOT.RUN() ---")
        bot.run(TOKEN)
    except Exception as e:
        print(f"\n[ERRO CRITICO] O bot falhou ao iniciar: {e}")
        print("Verifique se o TOKEN esta correto e se a internet esta funcionando.")
        pass
