import aiohttp
import json
import os
from datetime import datetime

# URL do Webhook do n8n (será configurada na VPS)
N8N_WEBHOOK_URL = os.getenv("N8N_BASE_ALARM_URL", "")


async def send_n8n_base_alert(
    player_name,
    coords,
    base_name,
    chat_id,
    is_group=False,
    event_type="Atividade Próxima",
):
    """
    Envia um alerta de base para o n8n para ser disparado via TELEGRAM.
    chat_id: ID do usuário ou do grupo no Telegram.
    is_group: Define se o destino é um grupo de clã.
    """
    if not N8N_WEBHOOK_URL:
        # Silencioso se não houver URL
        return

    payload = {
        "timestamp": datetime.now().isoformat(),
        "platform": "telegram",
        "event": "BASE_ALARM",
        "base_name": base_name,
        "chat_id": chat_id,
        "is_group": is_group,
        "intruder_name": player_name,
        "coords": coords,
        "event_type": event_type,
        "message": f"🚨 **ALARME BIGODE TEXAS**\n\n⚠️ **Atividade Detectada!**\n🏰 **Base:** {base_name}\n👤 **Intruso:** `{player_name}`\n📍 **Coords:** `{coords}`\n\n*Fique atento para defender seu território!* ⚔️",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL, json=payload, timeout=10
            ) as response:
                if response.status == 200:
                    print(f"[Telegram/n8n] Alerta enviado para base {base_name}")
                else:
                    print(f"[Telegram/n8n] Erro: {response.status}")
    except Exception as e:
        print(f"[Telegram/n8n] Falha na conexão: {e}")
