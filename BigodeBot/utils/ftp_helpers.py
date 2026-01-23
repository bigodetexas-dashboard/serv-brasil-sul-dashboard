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


def connect_ftp():
    """Estabelece conexão segura com o servidor FTP usando TLS"""
    try:
        # SECURITY: Use FTP_TLS for encrypted connections
        if FTP_USE_TLS:
            ftp = ftplib.FTP_TLS()  # nosec B321 - Using secure FTP_TLS with encryption
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)
            # Enable data channel protection (encrypt file transfers)
            ftp.prot_p()
        else:
            # Fallback to plain FTP only if explicitly disabled
            # WARNING: This transmits credentials in plain text!
            ftp = ftplib.FTP()  # nosec B321 - Only used if FTP_USE_TLS=False (not recommended)
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)

        return ftp
    except (ftplib.error_perm, OSError, ConnectionError) as e:
        print(f"Erro FTP: {e}")
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

    filename = "spawns.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(spawn_data, f)

        ftp = connect_ftp()
        if ftp:
            # Tenta entrar no diretório de perfil (padrão Nitroserv/Nitrado)
            for path in ["/dayzxb/config", "SC", "profile"]:
                try:
                    ftp.cwd(path)
                    break
                except (ftplib.error_perm, OSError):
                    continue  # Try next path

            with open(filename, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()

            # Limpa arquivo local
            if os.path.exists(filename):
                os.remove(filename)
            return True
    except (ftplib.error_perm, IOError, OSError) as e:
        print(f"Erro upload spawn: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False
    return False
