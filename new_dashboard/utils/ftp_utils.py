import os
import re
import sqlite3
from datetime import datetime
from ftplib import FTP
from dotenv import load_dotenv
from io import BytesIO
from utils.geolocation import get_location_by_ip, format_location_short

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PORT = int(os.getenv("FTP_PORT", 21))


def get_ftp_connection():
    """Establishes and returns an FTP connection."""
    ftp = FTP()
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp


def _save_guid_to_cache(gamertag, xbox_guid):
    """Salva ou atualiza o GUID Xbox de um jogador no cache SQLite."""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Verifica se já existe
        cursor.execute(
            "SELECT first_seen FROM player_guid_cache WHERE gamertag = ? COLLATE NOCASE",
            (gamertag,),
        )
        existing = cursor.fetchone()

        if existing:
            # Atualiza last_seen e GUID (caso tenha mudado, improvável mas possível)
            cursor.execute(
                """UPDATE player_guid_cache
                   SET xbox_guid = ?, last_seen = CURRENT_TIMESTAMP
                   WHERE gamertag = ? COLLATE NOCASE""",
                (xbox_guid, gamertag),
            )
        else:
            # Insere novo registro
            cursor.execute(
                """INSERT INTO player_guid_cache (gamertag, xbox_guid, last_seen, first_seen)
                   VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (gamertag, xbox_guid),
            )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CACHE] Erro ao salvar GUID de {gamertag}: {e}")


def get_guid_from_cache(gamertag):
    """Recupera o GUID Xbox de um jogador do cache SQLite."""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT xbox_guid FROM player_guid_cache WHERE gamertag = ? COLLATE NOCASE", (gamertag,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"[CACHE] Erro ao buscar GUID de {gamertag}: {e}")
        return None


async def get_players_from_logs(min_target=0):
    """
    Analisa os arquivos de log .ADM recentes via FTP para determinar os jogadores online.
    Scaneia até 3 arquivos (mais recentes) para encontrar jogadores que conectaram há muito tempo.
    """
    ftp = None
    try:
        ftp = get_ftp_connection()
        try:
            ftp.cwd("dayzxb/config")
        except:
            # Se falhar ao entrar na pasta, tenta listar da raiz (compatibilidade)
            pass

        files = []
        try:
            ftp.retrlines("LIST", lambda x: files.append(x))
        except Exception as e:
            print(f"[FTP] Erro ao listar arquivos: {e}")
            return []

        adm_files = []
        for line in files:
            if ".ADM" in line and "crash" not in line.lower():
                # Formato: DayZServer_X1_x64_YYYY-MM-DD_HH-MM-SS.ADM
                parts = line.split()
                if parts:
                    filename = parts[-1]
                    if filename.endswith(".ADM"):
                        adm_files.append(filename)

        if not adm_files:
            return []

        # Ordenar por nome (mais recente primeiro)
        adm_files.sort(reverse=True)

        # Limita a busca (safety cap 15) mas só para se atingir a meta
        files_to_check = adm_files[:15]

        online_players = {}  # Map: name -> {'name': name, 'id': id}
        seen_players = set()  # Rastreia quem já vimos (seja connect ou disconnect)

        # Regex robusta para Xbox: Captura o nome limpo (sem DEAD) e o ID (Hex)
        # Ex: Player "Grafftking"(id=F250...) ou Player "Name" (DEAD) (id=...)
        player_pattern = re.compile(r'Player "([^"]+)"(?: \(DEAD\))?.*?\(id=([A-F0-9]+)')

        print(f"[FTP] Buscando players em {len(files_to_check)} arquivos (Met: {min_target})...")

        for filename in files_to_check:
            # Se já achamos gente suficiente, paramos (otimização)
            # Mas só se min_target for definido e alcançado
            if min_target > 0 and len(online_players) >= min_target:
                break

            print(f"[FTP] Lendo {filename}...")
            bio = BytesIO()
            try:
                ftp.retrbinary(f"RETR {filename}", bio.write)
            except:
                continue

            content = bio.getvalue().decode("utf-8", errors="ignore")
            lines = content.splitlines()

            # Processar as linhas de TRÁS PARA FRENTE (do mais recente para o antigo)
            for line in reversed(lines):
                if not line.strip():
                    continue

                m = player_pattern.search(line)
                if m:
                    p_name = m.group(1)
                    p_id = m.group(2)

                    # Se já vimos o estado mais recente deste player (neste ou em arquivos futuros/mais novos), ignoramos
                    if p_name in seen_players:
                        continue

                    seen_players.add(p_name)

                    # Se o evento mais recente for desconexão, ele está OFF
                    if "disconnected" in line.lower():
                        continue

                    # Tenta extrair IP e porta da linha (formato: ip=1.2.3.4:5678)
                    ip_match = re.search(r"ip=([0-9.]+):(\d+)", line)
                    p_ip = ip_match.group(1) if ip_match else None
                    p_port = int(ip_match.group(2)) if ip_match else None

                    # Se o evento mais recente for qualquer outro (pos, connect, list dump), ele está ON
                    online_players[p_name] = {
                        "name": p_name,
                        "id": p_id,
                        "ip": p_ip,
                        "port": p_port,
                    }

        count = len(online_players)
        print(f"[FTP] Total encontrado: {count} players.")

        # Salva GUIDs no cache para uso futuro
        for player_data in online_players.values():
            if player_data.get("id"):
                _save_guid_to_cache(player_data["name"], player_data["id"])

        # Enriquece com geolocalização (busca IP do banco de dados)
        enriched_players = await _enrich_with_geolocation(list(online_players.values()))

        # Retorna lista de dicionários
        return sorted(enriched_players, key=lambda x: x["name"])

    except Exception as e:
        print(f"[FTP] Erro ao buscar jogadores nos logs: {e}")
        return []
    finally:
        if ftp:
            try:
                ftp.quit()
            except:
                try:
                    ftp.close()
                except:
                    pass


def read_remote_file(path):
    """Lê um arquivo do servidor FTP com tratamento de erro aprimorado."""
    ftp = None
    try:
        ftp = get_ftp_connection()
        bio = BytesIO()
        ftp.retrbinary(f"RETR {path}", bio.write)
        return bio.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[FTP] Erro na leitura ({path}): {e}")
        return None
    finally:
        if ftp:
            try:
                ftp.quit()
            except:
                pass


async def _enrich_with_geolocation(players):
    """
    Enriquece a lista de jogadores com informações de geolocalização.
    Busca o IP do banco de dados (player_identities) e adiciona localização.
    """
    try:
        conn = sqlite3.connect("bigode_unified.db")
        cursor = conn.cursor()

        for player in players:
            gamertag = player.get("name")
            if not gamertag:
                continue

            # Prioridade 1: IP que veio dos logs (mais recente)
            ip = player.get("ip")

            # Prioridade 2: Busca IP do jogador no banco se não veio dos logs
            if not ip:
                cursor.execute(
                    "SELECT last_ip FROM player_identities WHERE gamertag = ? COLLATE NOCASE",
                    (gamertag,),
                )
                result = cursor.fetchone()
                if result and result[0]:
                    ip = result[0]

            # Se temos IP, busca geolocalização
            if ip:
                location_data = await get_location_by_ip(ip)

                if location_data:
                    player["location"] = format_location_short(location_data)
                    player["isp"] = location_data.get("isp", "Unknown")
                else:
                    player["location"] = "Unknown"
                    player["isp"] = "Unknown"
            else:
                player["location"] = "Unknown"
                player["isp"] = "Unknown"

        conn.close()
        return players
    except Exception as e:
        print(f"[GEO] Erro ao enriquecer jogadores: {e}")
        # Retorna jogadores sem geolocalização em caso de erro
        for player in players:
            if "location" not in player:
                player["location"] = "Unknown"
            if "isp" not in player:
                player["isp"] = "Unknown"
        return players


async def get_messages_xml():
    """Busca o conteúdo do arquivo messages.xml via FTP."""
    return read_remote_file("dayzxb/config/messages.xml")
