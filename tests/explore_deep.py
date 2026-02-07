import os
import sys
from dotenv import load_dotenv
from ftplib import FTP

load_dotenv()


def explore_dayzxb():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")

    print(f"Connecting to {host}...")
    try:
        ftp = FTP(host)
        ftp.login(user, passwd)

        print("\nListing /dayzxb:")
        ftp.cwd("/dayzxb")
        ftp.retrlines("LIST")

        items = ftp.nlst()
        for item in items:
            try:
                ftp.cwd(f"/dayzxb/{item}")
                print(f"\n--- Contents of /dayzxb/{item} ---")
                ftp.retrlines("LIST")

                subitems = ftp.nlst()
                for si in subitems:
                    if si.upper().endswith(".ADM") or si.upper().endswith(".RPT"):
                        print(f"  [LOG FOUND] {si}")
                ftp.cwd("/dayzxb")
            except:
                pass

        ftp.quit()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    explore_dayzxb()
