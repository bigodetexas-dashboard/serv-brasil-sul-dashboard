import os
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("FTP_HOST")
user = os.getenv("FTP_USER")
pw = os.getenv("FTP_PASS")
port = int(os.getenv("FTP_PORT", 21))


def list_ftp():
    try:
        ftp = FTP()
        print(f"Connecting to {host}:{port}...")
        ftp.connect(host, port)
        ftp.login(user, pw)

        def walk(path):
            print(f"\n[DIR] {path if path else '/'}")
            items = []
            ftp.retrlines("LIST " + path, items.append)
            # Filter for files and directories
            for item in items:
                print(item)
                parts = item.split()
                if len(parts) < 9:
                    continue
                name = parts[-1]
                if item.startswith("d") and name not in [".", ".."]:
                    walk(path + "/" + name if path else name)

        walk("")
        ftp.quit()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    list_ftp()
