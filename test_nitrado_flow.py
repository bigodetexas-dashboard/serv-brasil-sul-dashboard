# test_nitrado_flow.py
import os
import time
from dotenv import load_dotenv
from bot_main import find_latest_adm_log, connect_ftp

load_dotenv()


def test_flow():
    print("--- INICIANDO TESTE DE FLUXO NITRADO ---")
    ftp = connect_ftp()
    if not ftp:
        print("[ERRO] FALHA NA CONEXAO FTP")
        return

    print("[OK] CONECTADO AO FTP")
    latest = find_latest_adm_log(ftp)
    if latest:
        print(f"[OK] LOG ENCONTRADO: {latest}")
    else:
        print("[AVISO] NENHUM LOG ENCONTRADO")

    ftp.quit()


if __name__ == "__main__":
    test_flow()
