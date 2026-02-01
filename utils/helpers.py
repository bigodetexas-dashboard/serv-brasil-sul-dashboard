import os
import json
import database


def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar {filename}: {e}")


def find_item_by_key(key):
    """Busca um item em todas as categorias do arquivo items.json"""
    items_data = load_json("items.json")
    for _category, items in items_data.items():
        if key in items:
            return items[key]
    return None


def calculate_kd(kills, deaths):
    """Calcula o K/D de um jogador"""
    return float(kills) if deaths == 0 else round(kills / deaths, 2)


def get_user_clan(user_id):
    """Retorna a tag do clã e os dados do clã do usuário."""
    clans = database.get_all_clans()
    uid = str(user_id)

    for tag, data in clans.items():
        members = data.get("members", [])
        if isinstance(members, str):
            try:
                members = json.loads(members)
            except Exception:
                members = []

        if data.get("leader") == uid or uid in members:
            return tag, data
    return None, None
