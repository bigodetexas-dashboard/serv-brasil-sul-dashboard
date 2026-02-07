# list_nitrado_dirs.py
import os
import ftplib
from dotenv import load_dotenv

load_dotenv()


def list_dirs():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")

    ftp = ftplib.FTP()
    ftp.connect(host, 21)
    ftp.login(user, passwd)

    for path in ["/", "/dayzxb", "/dayzxb/profile", "/profile"]:
        print(f"\n--- LISTING: {path} ---")
        try:
            ftp.cwd(path)
            items = ftp.nlst()
            for item in items:
                print(f"  {item}")
        except Exception as e:
            print(f"  [ERRO] {e}")

    ftp.quit()


if __name__ == "__main__":
    list_dirs()
