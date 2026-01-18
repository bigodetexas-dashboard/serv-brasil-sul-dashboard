"""
Módulo de integração com a API da Nitrado para gerenciamento do servidor DayZ.
Contém funções para restart, banimento e monitoramento de status.
"""

import os
import aiohttp
from dotenv import load_dotenv

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


async def ban_player(gamertag):
    """Bane um jogador via API da Nitrado (Adiciona a banlist)."""
    # Note: The endpoint /gameservers/{id}/games/banlist is used for managing bans.
    # Payload usually requires "identifier" (Gamertag).

    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/games/banlist"
    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"identifier": gamertag}

    print(f"[BAN] Tentando banir {gamertag}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"[SUCESSO] {gamertag} foi banido!")
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


async def kick_player(gamertag):
    """Expulsa um jogador via API da Nitrado."""
    url = (
        f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/games/players/kick"
    )
    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"identifier": gamertag}

    print(f"[KICK] Tentando expulsar {gamertag}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"[SUCESSO] {gamertag} foi expulso!")
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


async def get_online_players():
    """Retorna lista de jogadores online no servidor Nitrado."""
    data = await get_server_status()
    if data and "data" in data and "gameserver" in data["data"]:
        gs = data["data"]["gameserver"]
        players = gs.get("query", {}).get("players", [])
        return players if isinstance(players, list) else []
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
