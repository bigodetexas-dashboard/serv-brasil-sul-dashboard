import ftplib
import json
import os
from dotenv import load_dotenv

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", 21))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")


def connect_ftp():
    """Estabelece conexão com o servidor FTP"""
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.voidcmd("TYPE I")  # Force Binary Mode for SIZE support
        return ftp
    except Exception as e:
        print(f"Erro FTP: {e}")
        return None


def upload_spawn_request(item_name, coords, gamertag=None):
    """Gera o JSON de spawn e envia para o FTP do servidor DayZ"""
    spawn_data = {
        "items": [{"name": item_name, "coords": coords, "gamertag": gamertag}]
    }

    filename = "spawns.json"
    try:
        with open(filename, "w") as f:
            json.dump(spawn_data, f)

        ftp = connect_ftp()
        if ftp:
            # Tenta entrar no diretório de perfil (padrão Nitroserv/Nitrado)
            for path in ["/dayzxb/config", "SC", "profile"]:
                try:
                    ftp.cwd(path)
                    break
                except:
                    continue

            with open(filename, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()

            # Limpa arquivo local
            if os.path.exists(filename):
                os.remove(filename)
            return True
    except Exception as e:
        print(f"Erro upload spawn: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False
    return False
