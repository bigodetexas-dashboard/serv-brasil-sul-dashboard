import os
import sys
from dotenv import load_dotenv
from ftplib import FTP

load_dotenv()


def list_ftp_root():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")
    port = int(os.getenv("FTP_PORT", 21))

    print(f"Connecting to {host}...")
    try:
        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(user, passwd)
        print("Logged in. Root listing:")

        def list_recursive(path, depth=0):
            if depth > 2:
                return
            try:
                ftp.cwd(path)
                items = ftp.nlst()
                for item in items:
                    prefix = "  " * depth
                    print(f"{prefix}- {item}")
                    # Try to enter it to see if it's a dir (lazy check)
                    try:
                        list_recursive(f"{path}/{item}", depth + 1)
                        ftp.cwd(path)  # back
                    except:
                        pass
            except:
                pass

        ftp.retrlines("LIST")

        print("\nExploring folders...")
        items = ftp.nlst()
        for item in items:
            print(f"Folder/File: {item}")

        ftp.quit()

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    list_ftp_root()
