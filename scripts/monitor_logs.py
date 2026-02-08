# -*- coding: utf-8 -*-
"""
Robô de Logs Nitrado - BigodeTexas
Sincroniza Nitrado ID dos logs com as identidades do site.
"""

import os
import sys
import sqlite3
import time
import math
from datetime import datetime
from dotenv import load_dotenv

# Adicionar raiz do projeto ao sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.log_parser import DayZLogParser
from utils.ftp_helpers import connect_ftp
# from utils.heartbeat import send_heartbeat  # Opcional - comentado temporariamente
# from utils.sync_manager import SyncManager  # Opcional - comentado temporariamente

load_dotenv()

# Configurar encoding UTF-8 para o stdout (corrige exibição de caracteres especiais)
# NOTA: Desabilitado quando importado como módulo para evitar conflito com StdoutInterceptor
if sys.platform == "win32" and __name__ == "__main__":
    import codecs
    # Só aplicar se stdout ainda não foi interceptado
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    if hasattr(sys.stderr, 'detach'):
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Caminho do banco de dados unificado
DB_PATH = os.path.join(project_root, "bigode_unified.db")

# Rastreador de spam de construção
spam_tracker = {}  # {player_name: [timestamps]}
# Rastreador de logins (Anti-Dupe)
login_tracker = {}  # {player_name: [timestamps]}

# 🏙️ ZONAS URBANAS (SECURITY 3.0)
# Se estiver aqui, o teto é baixo (120m). Se fora, é alto (700m - Montanhas).
CITY_ZONES = {
    "Chernogorsk": {"center": (6600, 2600), "radius": 1500},
    "Elektrozavodsk": {"center": (10400, 2300), "radius": 1500},
    "Berezino": {"center": (12900, 9500), "radius": 2000},
    "Zelenogorsk": {"center": (2700, 5200), "radius": 1000},
    "Severograd": {"center": (8400, 12700), "radius": 1000},
    "Novodmitrovsk": {"center": (11500, 14500), "radius": 1500},
    "Vybor/NWAF": {"center": (4500, 10000), "radius": 2000},  # Base Militar
    "Svetloyarsk": {"center": (13900, 13400), "radius": 1000},
}


# ==================== FUNÇÕES DE PROTEÇÃO ====================


def is_raid_time():
    """Verifica se está no horário de RAID (Sexta 18h - Domingo 23h59)."""
    now = datetime.now()
    weekday = now.weekday()  # 0=Segunda, 4=Sexta, 6=Domingo
    hour = now.hour

    # Sexta após 18h
    if weekday == 4 and hour >= 18:
        return True
    # Sábado (dia inteiro)
    if weekday == 5:
        return True
    # Domingo até 23h59
    if weekday == 6:
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


def check_duplication(player_name):
    """Verifica se o jogador está relogando rapido demais (Duplication)."""
    now = time.time()
    if player_name not in login_tracker:
        login_tracker[player_name] = []

    # Limpa timestamps antigos (150 segundos = 2.5 min)
    login_tracker[player_name] = [
        t for t in login_tracker[player_name] if now - t < 150
    ]

    # Adiciona atual
    login_tracker[player_name].append(now)

    # Limite: 4 logins em 2.5 minutos
    if len(login_tracker[player_name]) >= 4:
        return True
    return False


def check_height_limit(x, z, y):
    """
    Verifica altura com contexto (Cidade vs Floresta).
    Retorna (Allowed: bool, Reason: str)
    """
    # 1. Hard Cap Global (Anti-Avião/Heli Glitch)
    if y > 700:
        return False, f"Global Hard Cap ({y:.1f}m > 700m)"

    # 2. Contexto Urbano
    for city_name, data in CITY_ZONES.items():
        cx, cz = data["center"]
        radius = data["radius"]

        # Distância até o centro da cidade
        dist = math.sqrt((x - cx) ** 2 + (z - cz) ** 2)

        if dist <= radius:
            # Está na Cidade - Limite Estrito (120m)
            # Cobre Prédios (50m) e Guindastes (70m) com folga.
            if y > 120:
                return False, f"City Glitch em {city_name} ({y:.1f}m > 120m)"
            return True, "City Safe"

    # 3. Zona Rural/Montanha
    # Permitido até 700m (Global Cap)
    return True, "Wilderness OK"


def check_construction(x, z, y, player_name, item_name, conn):
    """
    Verifica se a construção é permitida.
    Retorna (allowed: bool, reason: str)
    """
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
    cur = conn.cursor()

    # Busca bases ativas do PostgreSQL
    try:
        cur.execute("""
            SELECT b.id, b.owner_discord_id, b.clan_id, b.name, b.coord_x, b.coord_z, b.radius,
                   c.name as clan_name
            FROM bases_v2 b
            LEFT JOIN clans c ON b.clan_id = c.id
        """)
        active_bases = cur.fetchall()
    except Exception:
        # Se não tiver PostgreSQL, tenta SQLite local
        try:
            cur.execute(
                "SELECT id, owner_id, name, x, z, radius, clan_id FROM bases_v2"
            )
            active_bases = cur.fetchall()
        except Exception:
            # Sem bases registradas
            return True, "OK"

    for base in active_bases:
        # Adapta para diferentes estruturas de banco
        if isinstance(base, dict):
            base_x = base.get("coord_x") or base.get("x")
            base_z = base.get("coord_z") or base.get("z")
            base_radius = base.get("radius", 100)
            base_owner = base.get("owner_discord_id") or base.get("owner_id")
            base_name = base.get("name", "Base")
            base_id = base.get("id")
            base_clan_id = base.get("clan_id")
        else:
            # Tupla do SQLite
            try:
                (
                    base_id,
                    base_owner,
                    base_clan_id,
                    base_name,
                    base_x,
                    base_z,
                    base_radius,
                ) = base[:7]
            except:
                continue

        if not base_x or not base_z:
            continue

        # Calcula distância
        dist = math.sqrt((x - base_x) ** 2 + (z - base_z) ** 2)

        if dist <= base_radius:
            # --- REGRAS ESPECÍFICAS DE BASE ---

            # A. PNEUS (Glitch) -> BANIMENTO IMEDIATO
            if "wheel" in item_lower or "tire" in item_lower:
                return False, f"BannedItemBase:{item_name}"

            # B. SHELTER (Glitch de Visão) -> BANIMENTO IMEDIATO
            if "improvisedshelter" in item_lower:
                return False, f"BannedItemBase:{item_name}"

            # C. FOGUEIRA/CONSTRUÇÃO -> APENAS AUTORIZADOS

            # Busca Discord ID do jogador
            cur.execute(
                "SELECT discord_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?)",
                (player_name,),
            )
            row = cur.fetchone()

            if not row:
                # Se não tem conta vinculada, é considerado INIMIGO na área protegida
                return False, f"UnauthorizedBase:{base_name}"

            builder_id = row[0] if isinstance(row, tuple) else row.get("discord_id")

            # 1. É o Dono?
            if str(base_owner) == str(builder_id):
                return True, "Owner"

            # 2. Tem permissão explícita?
            try:
                cur.execute(
                    "SELECT level FROM base_permissions WHERE base_id = ? AND discord_id = ?",
                    (base_id, str(builder_id)),
                )
                perm_row = cur.fetchone()
                if perm_row:
                    return True, "PermittedUser"
            except Exception:
                pass

            # 3. É do Clã da Base?
            if base_clan_id:
                try:
                    cur.execute(
                        "SELECT clan_id FROM clan_members_v2 WHERE discord_id = ?",
                        (str(builder_id),),
                    )
                    member_row = cur.fetchone()
                    if member_row:
                        member_clan_id = (
                            member_row[0]
                            if isinstance(member_row, tuple)
                            else member_row.get("clan_id")
                        )
                        if member_clan_id == base_clan_id:
                            return True, "ClanBaseMember"
                except Exception:
                    pass

            return False, f"UnauthorizedBase:{base_name}"

    return True, "OK"


def ban_player(gamertag, reason="Banido pelo Bot", conn=None):
    """
    Adiciona o jogador ao arquivo ban.txt no servidor via FTP usando XUID se disponível.
    """
    xuid = None
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT xbox_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?)",
                (gamertag,),
            )
            row = cur.fetchone()
            if row:
                xuid = row[0] if isinstance(row, tuple) else row.get("xbox_id")
        except Exception as e:
            print(f"[ERRO] Falha ao buscar XUID para banimento: {e}")

    try:
        ftp = connect_ftp()
        if not ftp:
            print(f"[ERRO] Não foi possível conectar ao FTP para banir {gamertag}")
            return False

        # Caminho do arquivo de banimentos
        ban_file_path = "/dayzxb_config/ban.txt"

        # Baixa o arquivo atual
        ban_list = []
        try:
            from io import BytesIO

            bio = BytesIO()
            ftp.retrbinary(f"RETR {ban_file_path}", bio.write)
            bio.seek(0)
            ban_list = bio.read().decode("utf-8", errors="ignore").splitlines()
        except Exception:
            pass

        # Identificador para busca no ban.txt
        ban_id = xuid if xuid else gamertag

        # Verifica se já está banido
        is_banned = False
        for line in ban_list:
            if ban_id.lower() in line.lower():
                is_banned = True
                break

        if is_banned:
            print(f"[INFO] {gamertag} ({ban_id}) já está banido")
            ftp.quit()
            return True

        # Adiciona novo ban no formato solicitado: [XUID/GT] // [Gamertag] - [Motivo]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        if xuid:
            new_ban_line = f"{xuid}  // {gamertag} - {reason} - {timestamp}"
        else:
            new_ban_line = f"{gamertag}  // {reason} - {timestamp}"

        ban_list.append(new_ban_line)

        # Upload do arquivo atualizado
        from io import BytesIO

        bio = BytesIO("\n".join(ban_list).encode("utf-8"))
        bio.seek(0)
        ftp.storbinary(f"STOR {ban_file_path}", bio)

        ftp.quit()
        print(f"✅ [BANIMENTO] {gamertag} ({ban_id}) foi banido: {reason}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao banir {gamertag}: {e}")
        return False


# ==================== FIM DAS FUNÇÕES DE PROTEÇÃO ====================


def sync_logs():
    """Executa uma rodada de sincronização com tratamento de erros."""
    print(f"[{datetime.now()}] Iniciando ciclo autônomo de logs...")

    try:
        # 🔄 FAILOVER: Envia heartbeat para indicar que está vivo
        # send_heartbeat("primary")  # Comentado temporariamente

        # 🔄 FAILOVER: Verifica se há eventos do backup para sincronizar
        # sync_mgr = SyncManager()  # Comentado temporariamente
        # if sync_mgr.has_pending_sync():
        #     print("[SYNC] Eventos pendentes detectados! Sincronizando...")
        #     sync_mgr.process_backup_events()

        parser = DayZLogParser()
        local_log = "monitor_server_logs.txt"

        # 1. Baixar Logs (.ADM ou .RPT)
        if not parser.fetch_logs(local_log):
            return False

        # 2. Parsear Eventos
        events = parser.parse_log_events(local_log)
        if not events:
            print("[INFO] Nenhum evento novo detectado.")
            if os.path.exists(local_log):
                os.remove(local_log)
            return True

        print(f"[INFO] Processando {len(events)} eventos encontrados...")

        # 3. Conectar ao Banco
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        stats = {"conn": 0, "pvp": 0, "coins": 0}

        for event in events:
            e_type = event.get("type")

            # A. PROCESSAMENTO DE CONEXÃO (Identidades e IPs)
            if e_type == "connection":
                gt, pid, ip = event["gamertag"], event["player_id"], event["ip"]
                cur.execute(
                    "SELECT discord_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?)",
                    (gt,),
                )
                row = cur.fetchone()

                if row:
                    cur.execute(
                        "UPDATE player_identities SET nitrado_id = ?, xbox_id = ?, last_ip = ?, last_seen = datetime('now') WHERE LOWER(gamertag) = LOWER(?)",
                        (pid, pid, ip, gt),
                    )
                else:
                    cur.execute(
                        "INSERT OR IGNORE INTO player_identities (gamertag, nitrado_id, xbox_id, last_ip, last_seen) VALUES (?, ?, ?, ?, datetime('now'))",
                        (gt, pid, pid, ip),
                    )

                # 🛡️ PROTEÇÃO ATIVA: Anti-Dupe
                if check_duplication(gt):
                    print(
                        f"🚫 [ANTI-DUPE] {gt} relogou rápido demais (Possível Duplicação)!"
                    )
                    ban_player(gt, "Tentativa de Duplicação (Fast Relog)", conn)

                stats["conn"] += 1

            # B. PROCESSAMENTO DE PVP (Kills e Recompensas)
            elif e_type == "pvp_kill":
                killer, victim, weapon = (
                    event["killer"],
                    event["victim"],
                    event["weapon"],
                )
                dist, pos = event["distance"], event["pos"]

                # 🛡️ PROTEÇÃO ATIVA: Anti-SkyWalk (Inteligente)
                # pos é (x, y, z) agora
                if len(pos) >= 3:
                    x, y, z = pos[0], pos[1], pos[2]
                    allowed, reason = check_height_limit(x, z, y)

                    if not allowed:
                        print(f"🚫 [SKY-KILL] {killer} detectado: {reason}")
                        ban_player(killer, reason, conn)

                # 1. Registrar na tabela 'events' para o Heatmap
                cur.execute(
                    """
                    INSERT INTO events (event_type, killer_name, victim_name, weapon, distance, game_x, game_z, timestamp)
                """,
                    (killer, victim, weapon, dist, pos[0], pos[2], event["timestamp"]),
                )

                # 1.1 Registrar na tabela 'deaths_log' (Visualizada no Dashboard)
                try:
                    cur.execute(
                        """
                        INSERT INTO deaths_log
                        (killer_gamertag, victim_gamertag, death_type, death_cause, weapon, distance, coord_x, coord_z, occurred_at)
                        VALUES (?, ?, 'pvp', 'weapon', ?, ?, ?, ?, ?)
                        """,
                        (
                            killer,
                            victim,
                            weapon,
                            dist,
                            pos[0],
                            pos[2],
                            event["timestamp"],
                        ),
                    )
                except Exception as e:
                    print(f"⚠️ [AVISO] Falha ao gravar no deaths_log: {e}")

                stats["pvp"] += 1

                # 2. CREDITAR RECOMPENSA (150 DZCoins)
                # Tenta achar o Discord ID pelo Gamertag
                cur.execute(
                    "SELECT discord_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?) AND discord_id IS NOT NULL",
                    (killer,),
                )
                row = cur.fetchone()

                if row:
                    d_id = row["discord_id"]
                    reward = 150
                    print(
                        f"💰 [ECONOMIA] Creditando {reward} coins para {killer} (ID: {d_id}) por kill em {victim}"
                    )

                    # Atualiza balance na tabela users
                    cur.execute(
                        "UPDATE users SET balance = balance + ? WHERE discord_id = ?",
                        (reward, d_id),
                    )

                    # Tenta registrar histórico se a tabela existir
                    try:
                        cur.execute(
                            "INSERT INTO dashboard_events (event_type, discord_id, content, timestamp) VALUES ('reward', ?, ?, datetime('now'))",
                            (d_id, f"Recebeu {reward} DZCoins por eliminar {victim}"),
                        )
                    except Exception:
                        pass
                    stats["coins"] += 1
                else:
                    print(
                        f"⚠️ [AVISO] {killer} fez uma kill mas não tem Discord vinculado para receber coins."
                    )

            # C. PROCESSAMENTO DE CONSTRUÇÃO (Build e Placement)
            elif e_type in ["build_action", "placement"]:
                player = event.get("player")
                item = event.get("item")
                pos = event.get("pos")
                action = event.get("action", "placed")
                tool = event.get("tool", "none")

                # Extrai coordenadas (x, y, z) do parser atualizado (x, y, z)
                x, y, z = (
                    pos[0],
                    pos[1] if len(pos) > 2 else 0,
                    pos[2] if len(pos) > 2 else 0,
                )

                # 🛡️ PROTEÇÃO ATIVA: Verifica SPAM
                if check_spam(player, item):
                    print(f"🚫 [SPAM DETECTADO] {player} está spamando {item}!")
                    ban_player(player, "Spam de Construção/Lag Machine", conn)
                    stats["conn"] += 1  # Conta como evento processado
                    continue

                # 🛡️ PROTEÇÃO ATIVA: Verifica Regras de Construção
                allowed, reason = check_construction(x, z, y, player, item, conn)

                if not allowed:
                    # BANIMENTO AUTOMÁTICO
                    if reason == "GardenPlot":
                        print(f"🚫 [BANIMENTO] {player} tentou plantar GardenPlot!")
                        ban_player(player, "GardenPlot Proibido", conn)

                    elif reason == "SkyBase":
                        print(
                            f"🚫 [BANIMENTO] {player} tentou construir Sky Base (y={y}m)!"
                        )
                        # Sky Base é construção. Sky Walk seria movimento, mas se construir lá em cima também pega.
                        ban_player(player, f"Sky Base Detectada (Altura: {y}m)", conn)

                    elif reason == "UndergroundBase":
                        print(
                            f"🚫 [BANIMENTO] {player} tentou construir Underground Base (y={y}m)!"
                        )
                        ban_player(
                            player, f"Underground Base Detectada (Altura: {y}m)", conn
                        )

                    elif reason.startswith("BannedItemBase"):
                        banned_item = reason.split(":")[1]
                        print(
                            f"🚫 [BANIMENTO] {player} usou item proibido em base: {banned_item}!"
                        )
                        ban_player(player, f"Glitch Item em Base: {banned_item}", conn)

                    elif reason.startswith("UnauthorizedBase"):
                        base_name = reason.split(":")[1]
                        print(
                            f"🚫 [BANIMENTO] {player} construiu ilegalmente na base {base_name}!"
                        )
                        ban_player(
                            player, f"Construção Ilegal em Base: {base_name}", conn
                        )

                    stats["conn"] += 1  # Conta como evento processado
                    continue

                # ✅ CONSTRUÇÃO PERMITIDA - Registra no banco
                print(f"✅ [CONSTRUÇÃO OK] {player} colocou {item} ({reason})")

                # Registrar como evento para o Heatmap/Logs
                cur.execute(
                    """
                    INSERT INTO events (event_type, killer_name, victim_name, weapon, game_x, game_z, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        e_type,
                        player,
                        item,
                        tool if tool != "none" else action,
                        pos[0],
                        pos[2],  # Z agora é indice 2
                        event["timestamp"],
                    ),
                )
        conn.commit()
        conn.close()

        print(
            f"[OK] Fim do ciclo. Conexões: {stats['conn']}, Kills: {stats['pvp']}, Recompensas: {stats['coins']}"
        )

        if os.path.exists(local_log):
            os.remove(local_log)
        return True

    except Exception as e:
        print(f"[CRÍTICO] Erro no monitor de logs: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_forever():
    """Mantém o robô rodando eternamente com auto-recuperação."""
    print("========================================")
    print("   BIGODETEXAS - ROBÔ DE LOGS ATIVO     ")
    print("        Status: MODO AUTÔNOMO           ")
    print("========================================")

    consecutive_failures = 0

    while True:
        success = sync_logs()

        if success:
            consecutive_failures = 0
            # Espera 5 minutos para a próxima rodada
            time.sleep(300)
        else:
            consecutive_failures += 1
            wait_time = min(
                60 * consecutive_failures, 3600
            )  # Backoff progressivo até 1h
            print(f"[AUTO-RECOVERY] Falha detectada. Reiniciando em {wait_time}s...")
            time.sleep(wait_time)


if __name__ == "__main__":
    run_forever()
