# -*- coding: utf-8 -*-
"""
Sistema de Guerra entre Clãs - BigodeTexas
"""
import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db")


def get_war_db():
    """Conecta ao banco de dados"""
    try:
        if os.path.exists(DB_PATH):
            return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"[WAR SYSTEM] Erro ao conectar: {e}")
    return None


def ensure_clan_wars_table():
    """Garante que a tabela clan_wars existe no banco de dados"""
    conn = get_war_db()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clan_wars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan1_tag TEXT NOT NULL,
                clan2_tag TEXT NOT NULL,
                clan1_kills INTEGER DEFAULT 0,
                clan2_kills INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(clan1_tag, clan2_tag)
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        print(f"[WAR SYSTEM] Erro ao criar tabela: {e}")
        return False
    finally:
        conn.close()


def update_war_scores(killer_clan, victim_clan):
    """Atualiza o placar de guerra entre dois clãs"""
    if not killer_clan or not victim_clan or killer_clan == victim_clan:
        return None

    ensure_clan_wars_table()

    conn = get_war_db()
    if not conn:
        return None

    try:
        cur = conn.cursor()

        # Normalizar ordem dos clãs (alfabética) para evitar duplicatas
        clan_a, clan_b = sorted([killer_clan, victim_clan])

        # Verificar se há guerra ativa entre os clãs
        cur.execute("""
            SELECT id, clan1_tag, clan1_kills, clan2_kills
            FROM clan_wars
            WHERE ((clan1_tag = ? AND clan2_tag = ?) OR (clan1_tag = ? AND clan2_tag = ?))
            AND is_active = 1
        """, (clan_a, clan_b, clan_b, clan_a))

        war = cur.fetchone()

        if not war:
            return None  # Não há guerra ativa

        war_id, war_clan1, clan1_kills, clan2_kills = war

        # Atualizar score da guerra
        if killer_clan == war_clan1:
            cur.execute("""
                UPDATE clan_wars
                SET clan1_kills = clan1_kills + 1
                WHERE id = ?
            """, (war_id,))
            result = {
                "killer_clan": killer_clan,
                "victim_clan": victim_clan,
                "score": f"{clan1_kills + 1} x {clan2_kills}"
            }
        else:
            cur.execute("""
                UPDATE clan_wars
                SET clan2_kills = clan2_kills + 1
                WHERE id = ?
            """, (war_id,))
            result = {
                "killer_clan": killer_clan,
                "victim_clan": victim_clan,
                "score": f"{clan1_kills} x {clan2_kills + 1}"
            }

        conn.commit()
        print(f"[WAR SYSTEM] {killer_clan} matou {victim_clan} | Score: {result['score']}")
        return result

    except Exception as e:
        print(f"[WAR SYSTEM] Erro ao atualizar guerra: {e}")
        return None
    finally:
        conn.close()
