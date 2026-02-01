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
DB_PATH = os.path.join(project_root, "new_dashboard", "bigode_unified.db")


def sync_logs():
    """Executa uma rodada de sincronização com tratamento de erros."""
    print(f"[{datetime.now()}] Iniciando sincronização de logs...")

    try:
        parser = DayZLogParser()
        local_log = "monitor_server_logs.txt"

        # 1. Baixar Logs (O parser já tenta credenciais dinâmicas)
        if not parser.fetch_logs(local_log):
            print("[ERRO] Falha ao baixar logs. Verificando conexão...")
            return False

        # 2. Parsear Conexões
        connections = parser.parse_connections(local_log)
        if not connections:
            print("[INFO] Log processado. Nenhuma nova conexão.")
            return True

        print(f"[INFO] Processando {len(connections)} eventos de log...")

        # 3. Conectar ao Banco
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        updated_count = 0
        unknown_count = 0

        for event in connections:
            gamertag = event.get("gamertag")
            nitrado_id = event.get("player_id")
            ip = event.get("ip")

            if not nitrado_id:
                continue

            # Tenta encontrar o jogador pela Gamertag para ver se já vinculou no site
            cur.execute(
                "SELECT gamertag, discord_id, xbox_id FROM player_identities WHERE LOWER(gamertag) = LOWER(?)",
                (gamertag,),
            )
            row = cur.fetchone()

            if row:
                existing_discord_id = row[1]
                existing_xbox_id = row[2]

                # 1. Atualiza IDs técnicos vindos do jogo (Nitrado e IP)
                cur.execute(
                    """
                    UPDATE player_identities
                    SET nitrado_id = ?, last_ip = ?, last_seen = datetime('now')
                    WHERE LOWER(gamertag) = LOWER(?)
                """,
                    (nitrado_id, ip, gamertag),
                )
                updated_count += 1

                # 2. DETECTOR DE ALTS POR REDE (IP)
                if ip:
                    cur.execute(
                        "SELECT gamertag, discord_id FROM player_identities WHERE last_ip = ? AND discord_id != ? AND discord_id IS NOT NULL",
                        (ip, existing_discord_id),
                    )
                    alt_network = cur.fetchone()
                    if alt_network:
                        print(
                            f"⚠️ [ALERTA ALT NETWORK] {gamertag} compartilha IP ({ip}) com {alt_network[0]} (Discord: {alt_network[1]})"
                        )

                # 3. DETECTOR DE ALTS POR HARDWARE (Xbox ID)
                if existing_xbox_id:
                    cur.execute(
                        "SELECT gamertag, discord_id FROM player_identities WHERE xbox_id = ? AND discord_id != ? AND discord_id IS NOT NULL",
                        (existing_xbox_id, existing_discord_id),
                    )
                    alt_hardware = cur.fetchone()
                    if alt_hardware:
                        print(
                            f"🔥 [ALERTA ALT HARDWARE] {gamertag} usa o MESMO CONSOLE de {alt_hardware[0]} (Discord: {alt_hardware[1]})"
                        )
            else:
                # Jogador novo (sem vínculo no site), verificamos se o IP dele "dedura" um Alt
                cur.execute(
                    "SELECT discord_id, gamertag FROM player_identities WHERE last_ip = ? AND discord_id IS NOT NULL",
                    (ip,),
                )
                alt_tracker = cur.fetchone()
                if alt_tracker:
                    print(
                        f"🔍 [ALERTA ALT TRACK] Novo jogador {gamertag} detectado no IP de {alt_tracker[1]} (Discord: {alt_tracker[0]})"
                    )

                try:
                    cur.execute(
                        """
                        INSERT INTO player_identities (gamertag, nitrado_id, last_ip, last_seen)
                        VALUES (?, ?, ?, datetime('now'))
                    """,
                        (gamertag, nitrado_id, ip),
                    )
                    unknown_count += 1
                except sqlite3.IntegrityError:
                    pass

        conn.commit()
        conn.close()

        print(
            f"[OK] Fim do ciclo. Atualizados: {updated_count}, Novos: {unknown_count}"
        )

        if os.path.exists(local_log):
            os.remove(local_log)
        return True

    except Exception as e:
        print(f"[CRÍTICO] Falha no ciclo de monitoramento: {e}")
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
