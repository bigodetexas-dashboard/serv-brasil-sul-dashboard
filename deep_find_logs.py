# deep_find_logs.py
import os
import ftplib
from dotenv import load_dotenv

load_dotenv()


def deep_list():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")

    ftp = ftplib.FTP()
    ftp.connect(host, 21)
    ftp.login(user, passwd)

    found = []

    def traverse(path):
        print(f"Checking {path}...")
        try:
            ftp.cwd(path)
            items = ftp.nlst()
            for item in items:
                if item in [".", ".."]:
                    continue

                full_path = os.path.join(path, item).replace("\\", "/")
                if item.lower().endswith(".adm") or item.lower().endswith(".rpt"):
                    print(f"FOUND: {full_path}")
                    found.append(full_path)

                if "." not in item:  # assume it might be a dir
                    traverse(full_path)
                    ftp.cwd(path)  # back
        except:
            pass

    traverse("/")
    print("\n--- SUMMARY ---")
    for f in found:
        print(f)
    ftp.quit()


if __name__ == "__main__":
    deep_list()
