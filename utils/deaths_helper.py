# -*- coding: utf-8 -*-
"""
Helper functions para Deaths (Kill Feed)
"""

import re


def parse_death_from_log(line):
    """
    Detecta eventos de morte nos logs do DayZ

    Retorna dict com dados da morte ou None
    """
    # Padrão: morte por animal
    # Exemplo: Player "Jogador789" (id=789 pos=<10000.0, 5.0, 2000.0>) killed by Wolf
    animal_pattern = r'Player "(?P<victim>[^"]+)" \(id=\d+ pos=<(?P<x>[-0-9.]+), (?P<y>[-0-9.]+), (?P<z>[-0-9.]+)>\) killed by (?P<animal>Wolf|Bear)'
    animal_match = re.search(animal_pattern, line)

    if animal_match:
        victim_x = float(animal_match.group("x"))
        victim_y = float(animal_match.group("y"))
        victim_z = float(animal_match.group("z"))

        return {
            "type": "animal",
            "victim": animal_match.group("victim").strip(),
            "animal": animal_match.group("animal").lower(),
            "coord_x": victim_x,
            "coord_y": victim_y,
            "coord_z": victim_z,
            "location_name": get_location_name(victim_x, victim_z),
        }

    return None


def get_location_name(x, z):
    """
    Retorna nome da cidade mais próxima baseado em coordenadas

    Cidades principais do Chernarus
    """
    cities = {
        "Cherno": (6700, 2500),
        "Elektro": (10000, 2000),
        "Berezino": (12000, 9000),
        "Novo": (11500, 14500),
        "Severograd": (8000, 12500),
        "Vybor": (3800, 8900),
        "Zelenogorsk": (2500, 5000),
        "NWAF": (4500, 10000),
        "NEAF": (12000, 12500),
    }

    min_distance = float("inf")
    closest_city = "Desconhecido"

    for city_name, (city_x, city_z) in cities.items():
        distance = ((x - city_x) ** 2 + (z - city_z) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_city = city_name

    # Se estiver muito longe de qualquer cidade (>2000m), retornar "Floresta"
    if min_distance > 2000:
        return "Floresta"

    return closest_city


def save_death_to_db(death_data, conn):
    """
    Salva evento de morte no banco deaths_log

    Args:
        death_data: dict com dados da morte
        conn: conexão psycopg2
    """
    cur = conn.cursor()

    try:
        if death_data["type"] == "pvp":
            cur.execute(
                """
                INSERT INTO deaths_log (
                    killer_gamertag, victim_gamertag,
                    death_type, death_cause,
                    weapon, distance,
                    coord_x, coord_z, location_name,
                    coins_gained
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    death_data.get("killer"),
                    death_data.get("victim"),
                    "pvp",
                    "player",
                    death_data.get("weapon"),
                    death_data.get("distance"),
                    death_data.get("coord_x"),
                    death_data.get("coord_z"),
                    death_data.get("location_name"),
                    50,  # Recompensa padrão
                ),
            )

        elif death_data["type"] == "animal":
            cur.execute(
                """
                INSERT INTO deaths_log (
                    victim_gamertag,
                    death_type, death_cause,
                    coord_x, coord_y, coord_z, location_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    death_data.get("victim"),
                    "animal",
                    death_data.get("animal"),
                    death_data.get("coord_x"),
                    death_data.get("coord_y"),
                    death_data.get("coord_z"),
                    death_data.get("location_name"),
                ),
            )

        conn.commit()
        return True

    except Exception as e:
        print(f"[DEATHS] Erro ao salvar morte: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
