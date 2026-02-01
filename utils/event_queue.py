import json
import os
import time
from datetime import datetime

QUEUE_FILE = "pending_events.json"


def add_to_queue(event_type, player_name, data):
    """Adiciona um evento à fila local de pendências."""
    queue = load_queue()
    event = {
        "id": f"{int(time.time())}_{player_name}",
        "type": event_type,
        "player": player_name,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    queue.append(event)
    save_queue(queue)
    print(f"[QUEUE] Evento {event_type} para {player_name} salvo localmente.")


def load_queue():
    """Carrega a fila local."""
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_queue(queue):
    """Salva a fila local."""
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)


def get_pending_count():
    """Retorna o número de eventos pendentes."""
    return len(load_queue())


def clear_queue():
    """Limpa a fila local."""
    save_queue([])
