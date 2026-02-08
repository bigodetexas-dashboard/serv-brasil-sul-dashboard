# -*- coding: utf-8 -*-
"""
Sistema de Banimento Automático IMEDIATO - BigodeTexas
Detecta infrações e aplica ban instantâneo via XUID
"""
import sqlite3
import os
import sys
from datetime import datetime
from ftplib import FTP
from io import BytesIO
import requests
from dotenv import load_dotenv

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database

# Importar sistema de failover/sync
try:
    from utils.sync_manager import SyncManager
    SYNC_ENABLED = True
except ImportError:
    SYNC_ENABLED = False
    print("[AUTO-BAN] ⚠️ Sistema de sincronização não disponível")

load_dotenv()

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db")


# ==================== WHITELIST DE PROTEÇÃO ====================
# XUIDs protegidos - NUNCA serão banidos automaticamente
# Administradores e moderadores do servidor
PROTECTED_XUIDS = [
    "2535405695546273",  # Wellyton (Admin Principal)
    # Adicione outros admins aqui:
    # "1234567890123456",  # Nome do Admin
]


# ==================== TIPOS DE INFRAÇÕES ====================

class InfractionType:
    """Tipos de infrações detectáveis"""

    # CRÍTICAS (Ban Permanente Imediato)
    LAG_MACHINE = "lag_machine"              # Spam de construção (>10 itens/min)
    FLY_HACK = "fly_hack"                    # Construção em altura ilegal
    SKY_BASE = "sky_base"                    # Base acima de 1000m
    UNDERGROUND_BASE = "underground_base"    # Base abaixo de -10m
    BANNED_ITEM = "banned_item"              # Uso de item proibido (pneus, shelter)
    DUPLICATION = "item_duplication"         # Duplicação de itens (relog rápido)
    SPEED_HACK = "speed_hack"                # Velocidade anormal
    AIMBOT = "aimbot"                        # Headshot rate anormal
    WALLHACK = "wallhack"                    # Kills através de paredes

    # GRAVES (Ban Imediato - Revisável)
    ALT_ACCOUNT = "alt_account"              # Múltiplas contas mesmo IP
    GARDEN_EXPLOIT = "garden_exploit"        # Construção em jardim
    RAID_EXPLOIT = "raid_exploit"            # Raid fora do horário permitido
    GLITCH_ABUSE = "glitch_abuse"            # Abuso de bugs do jogo
    TERRITORY_INVASION = "territory_invasion"  # Construção em território alheio

    # CATEGORIAS
    CATEGORIES = {
        "CRÍTICA": [LAG_MACHINE, FLY_HACK, SKY_BASE, UNDERGROUND_BASE, BANNED_ITEM,
                    DUPLICATION, SPEED_HACK, AIMBOT, WALLHACK, TERRITORY_INVASION],
        "GRAVE": [ALT_ACCOUNT, GARDEN_EXPLOIT, RAID_EXPLOIT, GLITCH_ABUSE],
    }


def ensure_infractions_table():
    """Cria tabela de infrações se não existir"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS infractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gamertag TEXT NOT NULL,
                discord_id TEXT,
                xuid TEXT,
                ip_address TEXT,
                infraction_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                evidence TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                auto_banned BOOLEAN DEFAULT 1,
                ban_lifted BOOLEAN DEFAULT 0,
                admin_notes TEXT
            )
        """)

        # Índices para performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_gamertag ON infractions(gamertag)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_xuid ON infractions(xuid)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_type ON infractions(infraction_type)")

        conn.commit()
        return True
    except Exception as e:
        print(f"[AUTO-BAN] Erro ao criar tabela de infrações: {e}")
        return False
    finally:
        conn.close()


def record_infraction(gamertag, infraction_type, description, evidence=None,
                     xuid=None, ip_address=None, discord_id=None):
    """Registra uma infração no banco de dados"""

    # Determinar severidade
    severity = "CRÍTICA"
    for sev, types in InfractionType.CATEGORIES.items():
        if infraction_type in types:
            severity = sev
            break

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO infractions
            (gamertag, discord_id, xuid, ip_address, infraction_type, severity,
             description, evidence, auto_banned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (gamertag, discord_id, xuid, ip_address, infraction_type, severity,
              description, evidence))

        conn.commit()
        infraction_id = cur.lastrowid

        print(f"[AUTO-BAN] Infração registrada: {gamertag} - {infraction_type} (ID: {infraction_id})")
        return infraction_id

    except Exception as e:
        print(f"[AUTO-BAN] Erro ao registrar infração: {e}")
        return None
    finally:
        conn.close()


def ban_player_immediate(gamertag, xuid, reason, infraction_type, evidence=None):
    """
    Banimento IMEDIATO via XUID

    1. Adiciona ao ban.txt do servidor Nitrado
    2. Marca no banco de dados local
    3. Registra infração
    4. Envia notificação Discord
    5. Adiciona ao Muro da Vergonha
    """

    print(f"\n{'='*60}")
    print(f"[AUTO-BAN] INICIANDO BANIMENTO IMEDIATO")
    print(f"Jogador: {gamertag}")
    print(f"XUID: {xuid or 'N/A'}")
    print(f"Motivo: {reason}")
    print(f"Tipo: {infraction_type}")
    print(f"{'='*60}\n")

    # 🛡️ PROTEÇÃO: Verificar se é admin protegido
    if xuid and xuid in PROTECTED_XUIDS:
        print(f"\n{'='*60}")
        print(f"⚠️ [PROTEÇÃO] ADMIN DETECTADO - BAN BLOQUEADO!")
        print(f"Jogador: {gamertag}")
        print(f"XUID: {xuid}")
        print(f"Infração detectada: {infraction_type}")
        print(f"Motivo: {reason}")
        print(f"{'='*60}\n")

        # Registrar infração para auditoria (sem banir)
        record_infraction(
            gamertag=gamertag,
            infraction_type=f"{infraction_type}_ADMIN_PROTECTED",
            description=f"[ADMIN PROTEGIDO] {reason}",
            evidence=evidence,
            xuid=xuid
        )

        print(f"[AUTO-BAN] ℹ️ Infração registrada para auditoria, mas admin NÃO foi banido")
        return False  # Não banir

    # 1. Registrar infração
    infraction_id = record_infraction(
        gamertag=gamertag,
        infraction_type=infraction_type,
        description=reason,
        evidence=evidence,
        xuid=xuid
    )

    # 2. Marcar como banido no banco local
    conn = database.get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE users
                SET is_banned = 1,
                    role = 'banned',
                    ban_reason = ?,
                    banned_at = CURRENT_TIMESTAMP
                WHERE gamertag = ? OR xuid = ?
            """, (reason, gamertag, xuid))
            conn.commit()
            print(f"[AUTO-BAN] ✓ Marcado como banido no banco local")
        except Exception as e:
            print(f"[AUTO-BAN] ✗ Erro ao marcar no banco: {e}")
        finally:
            conn.close()

    # 3. Adicionar ao ban.txt do Nitrado via XUID
    ban_success = add_to_nitrado_banlist(gamertag, xuid, reason)

    # 4. Enviar notificação Discord
    send_ban_notification_discord(gamertag, xuid, reason, infraction_type, evidence, infraction_id)

    # 5. Adicionar ao Muro da Vergonha
    add_to_hall_of_shame(gamertag, xuid, reason, infraction_type, infraction_id)

    # 6. 🔄 FAILOVER: Enfileirar evento se estiver em modo backup
    is_backup_mode = os.getenv("BACKUP_MODE") == "1"
    if is_backup_mode and SYNC_ENABLED:
        try:
            sync_mgr = SyncManager()
            event_data = {
                "gamertag": gamertag,
                "xuid": xuid,
                "reason": reason,
                "infraction_type": infraction_type,
                "evidence": evidence,
                "infraction_id": infraction_id,
                "banned_at": datetime.now().isoformat()
            }
            sync_mgr.queue_event("auto_ban", event_data, "backup")
            print(f"[AUTO-BAN] 🔄 Evento enfileirado para sincronização (modo backup)")
        except Exception as e:
            print(f"[AUTO-BAN] ⚠️ Erro ao enfileirar evento: {e}")

    if ban_success:
        print(f"\n[AUTO-BAN] ✅ BANIMENTO COMPLETO: {gamertag}")
        return True
    else:
        print(f"\n[AUTO-BAN] ⚠️ BANIMENTO PARCIAL: {gamertag} (local OK, Nitrado falhou)")
        return False


def add_to_nitrado_banlist(gamertag, xuid, reason):
    """Adiciona jogador ao ban.txt do servidor Nitrado via FTP"""

    ftp_host = os.getenv("FTP_HOST")
    ftp_user = os.getenv("FTP_USER")
    ftp_pass = os.getenv("FTP_PASS")
    ftp_port = int(os.getenv("FTP_PORT", 21))

    if not all([ftp_host, ftp_user, ftp_pass]):
        print(f"[AUTO-BAN] ✗ Credenciais FTP não configuradas")
        return False

    try:
        # Conectar ao FTP
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port, timeout=30)
        ftp.login(ftp_user, ftp_pass)

        # Caminho do arquivo de banimentos
        ban_file_path = "/dayzxb/config/ban.txt"

        # Baixar ban.txt atual
        ban_list = []
        try:
            bio = BytesIO()
            ftp.retrbinary(f"RETR {ban_file_path}", bio.write)
            bio.seek(0)
            ban_list = bio.read().decode("utf-8", errors="ignore").splitlines()
        except Exception:
            print(f"[AUTO-BAN] Arquivo ban.txt não existe, será criado")

        # Usar XUID se disponível, senão gamertag
        ban_id = xuid if xuid else gamertag

        # Verificar se já está banido
        for line in ban_list:
            if ban_id.lower() in line.lower():
                print(f"[AUTO-BAN] ✓ {gamertag} ({ban_id}) já está banido no Nitrado")
                ftp.quit()
                return True

        # Adicionar novo ban
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if xuid:
            new_ban_line = f"{xuid}  // {gamertag} - {reason} - {timestamp} [AUTO-BAN]"
        else:
            new_ban_line = f"{gamertag}  // {reason} - {timestamp} [AUTO-BAN]"

        ban_list.append(new_ban_line)

        # Upload novo ban.txt
        bio = BytesIO("\n".join(ban_list).encode("utf-8"))
        bio.seek(0)
        ftp.storbinary(f"STOR {ban_file_path}", bio)

        ftp.quit()

        print(f"[AUTO-BAN] ✓ Adicionado ao ban.txt do Nitrado")
        return True

    except Exception as e:
        print(f"[AUTO-BAN] ✗ Erro ao adicionar ao Nitrado: {e}")
        return False


def send_ban_notification_discord(gamertag, xuid, reason, infraction_type, evidence, infraction_id):
    """Envia notificação de banimento para Discord"""

    webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")

    if not webhook_url or webhook_url == "seu_webhook_url_aqui":
        print(f"[AUTO-BAN] ⚠️ Webhook Discord não configurado")
        return False

    # Determinar cor baseado na severidade
    severity = "CRÍTICA"
    for sev, types in InfractionType.CATEGORIES.items():
        if infraction_type in types:
            severity = sev
            break

    color = 0xFF0000 if severity == "CRÍTICA" else 0xFF6600  # Vermelho ou Laranja

    # Criar embed
    embed = {
        "title": "🔨 BANIMENTO AUTOMÁTICO",
        "description": f"**{gamertag}** foi banido automaticamente do servidor!",
        "color": color,
        "fields": [
            {
                "name": "👤 Jogador",
                "value": f"**{gamertag}**",
                "inline": True
            },
            {
                "name": "🆔 XUID",
                "value": xuid or "N/A",
                "inline": True
            },
            {
                "name": "⚠️ Severidade",
                "value": f"**{severity}**",
                "inline": True
            },
            {
                "name": "🚨 Infração",
                "value": f"`{infraction_type}`",
                "inline": False
            },
            {
                "name": "📋 Motivo",
                "value": reason,
                "inline": False
            }
        ],
        "footer": {
            "text": f"ID da Infração: {infraction_id} | Sistema Anti-Cheat BigodeTexas"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # Adicionar evidências se disponível
    if evidence:
        embed["fields"].append({
            "name": "🔍 Evidência",
            "value": f"```{evidence[:200]}```",
            "inline": False
        })

    payload = {
        "username": "Sistema Anti-Cheat",
        "avatar_url": "https://i.imgur.com/S71j4qO.png",
        "embeds": [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"[AUTO-BAN] ✓ Notificação enviada ao Discord")
            return True
        else:
            print(f"[AUTO-BAN] ✗ Erro ao enviar Discord: {response.status_code}")
            return False
    except Exception as e:
        print(f"[AUTO-BAN] ✗ Erro ao enviar Discord: {e}")
        return False


def add_to_hall_of_shame(gamertag, xuid, reason, infraction_type, infraction_id):
    """Adiciona ao Muro da Vergonha (tabela já registrada em infractions)"""

    # A tabela infractions já serve como "Muro da Vergonha"
    # Apenas marcar para exibição pública

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Verificar se jogador tem Discord ID
        cur.execute("SELECT discord_id FROM users WHERE gamertag = ? OR xuid = ?", (gamertag, xuid))
        row = cur.fetchone()
        discord_id = row[0] if row else None

        if discord_id:
            cur.execute("""
                UPDATE infractions
                SET discord_id = ?
                WHERE id = ?
            """, (discord_id, infraction_id))
            conn.commit()

        print(f"[AUTO-BAN] ✓ Adicionado ao Muro da Vergonha")
        return True

    except Exception as e:
        print(f"[AUTO-BAN] ✗ Erro ao adicionar ao Muro: {e}")
        return False
    finally:
        conn.close()


def get_hall_of_shame(limit=50):
    """Retorna lista do Muro da Vergonha para exibição no site"""

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                gamertag,
                xuid,
                infraction_type,
                severity,
                description,
                detected_at,
                evidence
            FROM infractions
            WHERE auto_banned = 1 AND ban_lifted = 0
            ORDER BY detected_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cur.fetchall():
            results.append({
                "gamertag": row[0],
                "xuid": row[1],
                "infraction_type": row[2],
                "severity": row[3],
                "description": row[4],
                "detected_at": row[5],
                "evidence": row[6]
            })

        return results

    except Exception as e:
        print(f"[AUTO-BAN] Erro ao buscar Muro da Vergonha: {e}")
        return []
    finally:
        conn.close()


# ==================== FUNÇÕES DE DETECÇÃO ====================

def detect_lag_machine(player_name, item_count_per_minute):
    """Detecta Lag Machine (spam de construção)"""
    if item_count_per_minute > 10:
        return True, f"Spam de construção: {item_count_per_minute} itens/min"
    return False, None


def detect_fly_hack(player_name, height, location):
    """Detecta Fly Hack (construção em altura ilegal)"""
    max_height = 120  # Padrão para cidades

    # Verificar se está em cidade (altura máxima menor)
    # Verificar se está em floresta (altura máxima maior)

    if height > 1000:
        return True, f"Sky Base: Construção a {height}m de altura"
    elif height > max_height:
        return True, f"Fly Hack: Construção a {height}m (máx: {max_height}m)"

    return False, None


def detect_underground_base(player_name, height):
    """Detecta Underground Base"""
    if height < -10:
        return True, f"Underground Base: Construção a {height}m abaixo do solo"
    return False, None


def detect_banned_item(player_name, item_name):
    """Detecta uso de itens banidos"""
    banned_items = ["TireRepairKit", "Shelter"]

    if any(banned in item_name for banned in banned_items):
        return True, f"Item banido: {item_name}"
    return False, None


# Inicializar tabela ao importar
ensure_infractions_table()


if __name__ == "__main__":
    print("Sistema de Banimento Automático - BigodeTexas")
    print("\nTipos de Infrações Detectadas:\n")

    for severity, types in InfractionType.CATEGORIES.items():
        print(f"\n{severity}:")
        for t in types:
            print(f"  - {t}")
