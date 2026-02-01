import os
import json


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


def calculate_kd(kills, deaths):
    """Calcula o K/D de um jogador"""
    return float(kills) if deaths == 0 else round(kills / deaths, 2)
