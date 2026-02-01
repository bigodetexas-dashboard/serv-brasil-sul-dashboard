# -*- coding: utf-8 -*-
"""
Teste de Simulação - Robô de Logs
"""

import os
import sqlite3

# Caminho do banco de dados unificado
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "new_dashboard",
    "bigode_unified.db",
)


def simulation_test():
    print("Iniciando Simulação de Vínculo...")

    # Dados fictícios para simular o log
    mock_gamertag = "BigodeTester"
    mock_nitrado_id = "NIT-123456"
    mock_ip = "127.0.0.1"

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 1. Garantir que o jogador existe na player_identities (simula vínculo no site)
        print(f"Inserindo jogador de teste: {mock_gamertag}...")
        cur.execute(
            "INSERT OR REPLACE INTO player_identities (gamertag, xbox_id) VALUES (?, ?)",
            (mock_gamertag, "XBOX-TEST-999"),
        )

        # 2. Executar a lógica do robô
        print(
            f"Simulando robô encontrando {mock_gamertag} nos logs com ID {mock_nitrado_id}..."
        )
        cur.execute(
            """
            UPDATE player_identities
            SET nitrado_id = ?, last_ip = ?, last_seen = datetime('now')
            WHERE LOWER(gamertag) = LOWER(?)
        """,
            (mock_nitrado_id, mock_ip, mock_gamertag),
        )

        # 3. Verificar resultado
        cur.execute(
            "SELECT nitrado_id, last_ip FROM player_identities WHERE gamertag = ?",
            (mock_gamertag,),
        )
        result = cur.fetchone()

        if result and result[0] == mock_nitrado_id:
            print("[SUCESSO] O Robô vinculou corretamente o Nitrado ID à Gamertag!")
        else:
            print("[FALHA] O vínculo não foi encontrado no banco.")

        conn.commit()
    except Exception as e:
        print(f"[ERRO] Erro no teste: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    simulation_test()
