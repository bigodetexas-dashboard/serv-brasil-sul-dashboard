"""
Módulo de integração com a API da Nitrado para gerenciamento do servidor DayZ.
Contém funções para restart, banimento e monitoramento de status.
"""

import os
import aiohttp
from dotenv import load_dotenv
from utils.ftp_utils import get_players_from_logs

load_dotenv()

NITRADO_TOKEN = os.getenv("NITRADO_TOKEN")
SERVICE_ID = os.getenv("SERVICE_ID")


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
                        return True, "Servidor reiniciando com sucesso!"
                    else:
                        print(f"[AVISO] API: {data}")
                        return False, f"Erro API: {data.get('message')}"
                else:
                    text = await response.text()
                    print(f"❌ ERRO API: {response.status} - {text}")
                    return False, f"Erro HTTP: {response.status}"
    except aiohttp.ClientError as e:
        print(f"[ERRO] Erro de rede Nitrado: {e}")
        return False, f"Erro de conexão: {e}"
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao reiniciar: {e}")
        return False, f"Erro inesperado: {e}"


async def stop_server():
    """Envia comando de stop para a API da Nitrado."""
    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/stop"
    headers = {"Authorization": f"Bearer {NITRADO_TOKEN}"}

    print(f"[STOP] Tentando parar servidor ID {SERVICE_ID}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print("[SUCESSO] Servidor parando!")
                        return True, "Servidor parando com sucesso!"
                    else:
                        return False, f"Erro API: {data.get('message')}"
                else:
                    return False, f"Erro HTTP: {response.status}"
    except Exception as e:
        return False, f"Erro inesperado: {e}"


async def ban_player(target_arg):
    """
    Bane um jogador via API da Nitrado (Adiciona a banlist).
    Aceita string (Gamertag) ou dict ({'name': ..., 'id': ...}).
    """
    identifier = target_arg

    if isinstance(target_arg, dict):
        # Prefere ID se disponível
        if target_arg.get("id"):
            identifier = target_arg["id"]
            print(f"[BAN] Usando ID Xbox para banir: {identifier}")
        else:
            identifier = target_arg.get("name")
            print(f"[BAN] ID não encontrado, usando Gamertag: {identifier}")

    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/games/banlist"
    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"identifier": identifier}

    print(f"[BAN] Tentando banir {identifier}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"[SUCESSO] {identifier} foi banido!")
                        return True
                    else:
                        print(f"[ERRO BAN] API Resposta: {data}")
                else:
                    print(f"[ERRO BAN] Status: {response.status}")
    except aiohttp.ClientError as e:
        print(f"[ERRO BAN] Erro de rede: {e}")
    except Exception as e:
        print(f"[ERRO BAN] Erro inesperado: {e}")

    return False


async def kick_player(target_arg):
    """Expulsa um jogador via API da Nitrado."""
    identifier = target_arg
    if isinstance(target_arg, dict):
        identifier = target_arg.get("name")  # Kick geralmente usa nome

    url = (
        f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/games/players/kick"
    )
    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"identifier": identifier}

    print(f"[KICK] Tentando expulsar {identifier}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"[SUCESSO] {identifier} foi expulso!")
                        return True
                    else:
                        print(f"[ERRO KICK] API Resposta: {data}")
                else:
                    print(f"[ERRO KICK] Status: {response.status}")
    except aiohttp.ClientError as e:
        print(f"[KICK] Erro de rede: {e}")
    except Exception as e:
        print(f"[KICK] Erro inesperado: {e}")

    return False


# Cache para evitar conexões FTP excessivas e lidar com lag de logs
_ftp_players_cache = {"data": [], "timestamp": 0}
_player_history_file = "player_history.json"
_player_history_cache = {}  # Gamertag -> Timestamp
_history_loaded = False


def _load_history():
    """Carrega o histórico de jogadores do arquivo json."""
    import json

    global _player_history_cache, _history_loaded
    if _history_loaded:
        return

    if os.path.exists(_player_history_file):
        try:
            with open(_player_history_file, "r") as f:
                _player_history_cache = json.load(f)
        except Exception as e:
            print(f"[CACHE] Erro ao carregar histórico: {e}")
    _history_loaded = True


def _save_history():
    """Salva o histórico de jogadores."""
    import json

    try:
        with open(_player_history_file, "w") as f:
            json.dump(_player_history_cache, f)
    except Exception as e:
        print(f"[CACHE] Erro ao salvar histórico: {e}")


def _update_history(players):
    """Atualiza o timestamp e ID dos jogadores detectados."""
    import time

    now = time.time()
    updated = False

    for p in players:
        name = ""
        pid = None

        if isinstance(p, dict):
            name = p.get("name")
            pid = p.get("id")
        elif isinstance(p, str):
            name = p

        if name:
            # Recupera dados anteriores para não sobrescrever ID com None se já tínhamos um
            old_data = _player_history_cache.get(name)

            # Normaliza old_data para dict
            if isinstance(old_data, (float, int)):
                old_data = {"time": old_data, "id": None}
            elif old_data is None:
                old_data = {"time": 0, "id": None}

            # Atualiza
            new_data = {"time": now, "id": pid if pid else old_data.get("id")}

            _player_history_cache[name] = new_data
            updated = True

    if updated:
        _save_history()


async def get_online_players():
    """Retorna lista de jogadores online no servidor Nitrado com persistência robusta."""
    import time

    # Garantir que o histórico está carregado
    _load_history()

    data = await get_server_status()
    players = []
    p_count = 0

    if data and "data" in data and "gameserver" in data["data"]:
        gs = data["data"]["gameserver"]
        players = gs.get("query", {}).get("players", [])
        p_count = gs.get("query", {}).get("player_current", 0)

        # Normalização da lista (garantir nomes únicos)
        if players:
            # Em alguns casos a API retorna dicts ou strings? Geralmente strings ou dicts com name.
            # O código anterior assumia lista de strings? O log retorna strings.
            # Se a API retornar objetos, precisamos extrair nomes.
            # Mas debug_players.py mostra players=[] então não sabemos o formato exato
            # Assumindo strings por compatibilidade com logs.
            pass

        # Atualiza histórico com o que veio da API (se veio algo)
        if players:
            _update_history(players)

        # Se a lista via API estiver incompleta (menor que o count)
        # Consultamos os logs/cache
        if p_count > 0 and len(players) < p_count:
            now = time.time()

            # Só consulta FTP se o cache expirou (60s)
            log_players = []
            if now - _ftp_players_cache["timestamp"] > 60:
                print(
                    f"[NITRADO] Lista parcial ({len(players)}/{p_count}). Sincronizando logs..."
                )
                # Passa p_count como meta para o FTP buscar em múltiplos arquivos se precisar
                log_players = await get_players_from_logs(min_target=p_count)

                _ftp_players_cache["data"] = log_players
                _ftp_players_cache["timestamp"] = now
            else:
                log_players = _ftp_players_cache["data"]

            # Atualiza histórico com o que veio do log
            if log_players:
                _update_history(log_players)

            # Build final list: API + Log
            # Normalizar para dicts para deduplicação
            combined_map = {}

            # Adiciona API (assumindo strings por padrão na query list antiga)
            for p in players:
                if isinstance(p, str):
                    combined_map[p] = {"name": p, "id": None}
                elif isinstance(p, dict):
                    combined_map[p.get("name")] = p

            # Adiciona Log (dicts com ID) - Sobrescreve API se tiver ID
            for p in log_players:
                if isinstance(p, dict):
                    combined_map[p["name"]] = p
                elif isinstance(p, str):
                    # Fallback para string antiga
                    if p not in combined_map:
                        combined_map[p] = {"name": p, "id": None}

            # Se ainda faltar gente, completamos com o histórico recente
            if len(combined_map) < p_count:
                needed = p_count - len(combined_map)

                # Helper para ordenar por tempo (compatível com float antigo ou dict novo)
                def get_time(item):
                    val = _player_history_cache[item]
                    if isinstance(val, dict):
                        return val.get("time", 0)
                    return val  # é float

                candidates = [
                    p for p in _player_history_cache.keys() if p not in combined_map
                ]
                candidates.sort(key=get_time, reverse=True)

                filled = candidates[:needed]
                for p in filled:
                    # Recupera ID do cache se houver
                    cache_val = _player_history_cache[p]
                    cached_id = None
                    if isinstance(cache_val, dict):
                        cached_id = cache_val.get("id")

                    combined_map[p] = {"name": p, "id": cached_id}

            # Retorna lista de dicts
            final_list = list(combined_map.values())
            final_list.sort(key=lambda x: x["name"])
            return final_list

    return []


async def get_server_status():
    """Retorna o status completo do gameserver Nitrado."""
    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers"
    headers = {"Authorization": f"Bearer {NITRADO_TOKEN}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"[NITRADO] Erro Status: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"[NITRADO] Erro de rede ao buscar status: {e}")
        return None
    except Exception as e:
        print(f"[NITRADO] Erro inesperado ao buscar status: {e}")
        return None


async def get_ftp_credentials():
    """Busca credenciais de FTP via API da Nitrado."""
    data = await get_server_status()
    if data and "data" in data and "gameserver" in data["data"]:
        gs = data["data"]["gameserver"]
        return {
            "primary_ip": gs.get("ip"),
            "host": gs.get("ip"),
            "user": gs.get("username"),
            "port": gs.get("ftp_port", 21),
        }
    return None
