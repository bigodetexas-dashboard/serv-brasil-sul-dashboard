"""
FTP helper utilities for DayZ server file management.
Provides functions for secure FTP_TLS connection and file upload operations.
"""

import ftplib  # nosec B402 - FTP secured with FTP_TLS by default, see FTP_USE_TLS
import json
import os

from dotenv import load_dotenv

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT") or "21")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
# Use TLS by default for security, set to False only if server doesn't support it
FTP_USE_TLS = os.getenv("FTP_USE_TLS", "True").lower() == "true"


import time


def connect_ftp(retries=3, delay=2):
    """
    Estabelece conexÃ£o segura com o servidor FTP usando TLS.
    Tenta conectar 'retries' vezes com 'delay' segundos de intervalo.
    """
    for attempt in range(retries):
        try:
            # SECURITY: Use FTP_TLS for encrypted connections
            if FTP_USE_TLS:
                ftp = ftplib.FTP_TLS()  # nosec B321 - Using secure FTP_TLS with encryption
                ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
                ftp.login(FTP_USER, FTP_PASS)
                # Enable data channel protection (encrypt file transfers)
                ftp.prot_p()
            else:
                # Fallback to plain FTP only if explicitly disabled
                ftp = ftplib.FTP()  # nosec B321
                ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
                ftp.login(FTP_USER, FTP_PASS)

            return ftp
        except (ftplib.all_errors, OSError, ConnectionError) as e:
            print(f"[FTP] Connect Error (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff-ish
            else:
                return None
    return None


def upload_spawn_request(item_name, coords):
    """Gera o JSON de spawn e envia para o FTP do servidor DayZ"""
    spawn_data = {
        "items": [
            {
                "name": item_name,
                "coords": coords,
            }
        ]
    }

    filename = f"spawns_{int(time.time())}.json"  # Unique filename to avoid collisions
    temp_file = "spawns.json"  # Force standard name for server to pick up (server script expects specific name?)
    # INIT.C expects "spawns.json", so we must use that name.
    # Concurrency risk: if 2 people buy at same time, one overwrites other.
    # TODO: Modify init.c to read *any* json file in a folder later. For now, we stick to protocol.

    filename = "spawns.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(spawn_data, f)

        ftp = connect_ftp(retries=4, delay=2)
        if ftp:
            # Tenta entrar no diretÃ³rio de perfil (padrÃ£o Nitroserv/Nitrado)
            for path in ["/dayzxb/config", "SC", "profile"]:
                try:
                    ftp.cwd(path)
                    break
                except (ftplib.error_perm, OSError):
                    continue  # Try next path

            with open(filename, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()

            # Limpa arquivo local em caso de sucesso
            if os.path.exists(filename):
                os.remove(filename)
            return True
        else:
            print("[FTP] Falha crÃ­tica: NÃ£o foi possÃ­vel conectar apÃ³s vÃ¡rias tentativas.")
            # Don't delete local file if failed? No, we should clean up or it accumulates.
            if os.path.exists(filename):
                os.remove(filename)
            return False

    except (ftplib.error_perm, IOError, OSError) as e:
        print(f"Erro upload spawn: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False
    return False
