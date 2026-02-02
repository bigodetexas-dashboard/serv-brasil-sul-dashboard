# -*- coding: utf-8 -*-
"""
Robô de Logs Nitrado - BigodeTexas
Sincroniza Nitrado ID dos logs com as identidades do site.
"""

import os
import sys
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv

# Adicionar raiz do projeto ao sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.log_parser import DayZLogParser

load_dotenv()

# Caminho do banco de dados unificado
DB_PATH = os.path.join(project_root, "bigode_unified.db")


def sync_logs():
    """Executa uma rodada de sincronização com tratamento de erros."""
    print(f"[{datetime.now()}] Iniciando ciclo autônomo de logs...")

    try:
        parser = DayZLogParser()
        local_log = "monitor_server_logs.txt"

        # 1. Baixar Logs (.ADM ou .RPT)
        if not parser.fetch_logs(local_log):
            return False

        # 2. Parsear Eventos
        events = parser.parse_log_events(local_log)
        if not events:
            print("[INFO] Nenhum evento novo detectado.")
            if os.path.exists(local_log):
                os.remove(local_log)
            return True

        print(f"[INFO] Processando {len(events)} eventos encontrados...")

        # 3. Conectar ao Banco
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        stats = {"conn": 0, "pvp": 0, "coins": 0}

        for event in events:
            e_type = event.get("type")

            # A. PROCESSAMENTO DE CONEXÃO (Identidades e IPs)
            if e_type == "connection":
                gt, pid, ip = event["gamertag"], event["player_id"], event["ip"]
                cur.execute(
                    "SELECT discord_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?)",
                    (gt,),
                )
                row = cur.fetchone()

                if row:
                    cur.execute(
                        "UPDATE player_identities SET nitrado_id = ?, last_ip = ?, last_seen = datetime('now') WHERE LOWER(gamertag) = LOWER(?)",
                        (pid, ip, gt),
                    )
                else:
                    cur.execute(
                        "INSERT OR IGNORE INTO player_identities (gamertag, nitrado_id, last_ip, last_seen) VALUES (?, ?, ?, datetime('now'))",
                        (gt, pid, ip),
                    )
                stats["conn"] += 1

            # B. PROCESSAMENTO DE PVP (Kills e Recompensas)
            elif e_type == "pvp_kill":
                killer, victim, weapon = (
                    event["killer"],
                    event["victim"],
                    event["weapon"],
                )
                dist, pos = event["distance"], event["pos"]

                # 1. Registrar na tabela 'events' para o Heatmap
                cur.execute(
                    """
                    INSERT INTO events (event_type, killer_name, victim_name, weapon, distance, game_x, game_z, timestamp)
                    VALUES ('kill', ?, ?, ?, ?, ?, ?, ?)
                """,
                    (killer, victim, weapon, dist, pos[0], pos[1], event["timestamp"]),
                )
                stats["pvp"] += 1

                # 2. CREDITAR RECOMPENSA (150 DZCoins)
                # Tenta achar o Discord ID pelo Gamertag
                cur.execute(
                    "SELECT discord_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?) AND discord_id IS NOT NULL",
                    (killer,),
                )
                row = cur.fetchone()

                if row:
                    d_id = row["discord_id"]
                    reward = 150
                    print(
                        f"💰 [ECONOMIA] Creditando {reward} coins para {killer} (ID: {d_id}) por kill em {victim}"
                    )

                    # Atualiza balance na tabela users
                    cur.execute(
                        "UPDATE users SET balance = balance + ? WHERE discord_id = ?",
                        (reward, d_id),
                    )

                    # Tenta registrar histórico se a tabela existir
                    try:
                        cur.execute(
                            "INSERT INTO dashboard_events (event_type, discord_id, content, timestamp) VALUES ('reward', ?, ?, datetime('now'))",
                            (d_id, f"Recebeu {reward} DZCoins por eliminar {victim}"),
                        )
                    except Exception:
                        pass
                    stats["coins"] += 1
                else:
                    print(
                        f"⚠️ [AVISO] {killer} fez uma kill mas não tem Discord vinculado para receber coins."
                    )

            # C. PROCESSAMENTO DE CONSTRUÇÃO (Build e Placement)
            elif e_type in ["build_action", "placement"]:
                player = event.get("player")
                item = event.get("item")
                pos = event.get("pos")
                action = event.get("action", "placed")
                tool = event.get("tool", "none")

                # Registrar como evento para o Heatmap/Logs
                cur.execute(
                    """
                    INSERT INTO events (event_type, killer_name, victim_name, weapon, game_x, game_z, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        e_type,
                        player,
                        item,
                        tool if tool != "none" else action,
                        pos[0],
                        pos[1],
                        event["timestamp"],
                    ),
                )
        conn.commit()
        conn.close()

        print(
            f"[OK] Fim do ciclo. Conexões: {stats['conn']}, Kills: {stats['pvp']}, Recompensas: {stats['coins']}"
        )

        if os.path.exists(local_log):
            os.remove(local_log)
        return True

    except Exception as e:
        print(f"[CRÍTICO] Erro no monitor de logs: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_forever():
    """Mantém o robô rodando eternamente com auto-recuperação."""
    print("========================================")
    print("   BIGODETEXAS - ROBÔ DE LOGS ATIVO     ")
    print("        Status: MODO AUTÔNOMO           ")
    print("========================================")

    consecutive_failures = 0

    while True:
        success = sync_logs()

        if success:
            consecutive_failures = 0
            # Espera 5 minutos para a próxima rodada
            time.sleep(300)
        else:
            consecutive_failures += 1
            wait_time = min(
                60 * consecutive_failures, 3600
            )  # Backoff progressivo até 1h
            print(f"[AUTO-RECOVERY] Falha detectada. Reiniciando em {wait_time}s...")
            time.sleep(wait_time)


if __name__ == "__main__":
    run_forever()
