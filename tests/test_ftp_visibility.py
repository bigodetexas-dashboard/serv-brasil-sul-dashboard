import os
import sys
from dotenv import load_dotenv
from ftplib import FTP

load_dotenv()


def test_ftp():
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    passwd = os.getenv("FTP_PASS")
    port = int(os.getenv("FTP_PORT", 21))

    print(f"Connecting to {host}...")
    try:
        ftp = FTP()
        ftp.connect(host, port, timeout=10)
        ftp.login(user, passwd)
        print("Logged in.")

        # Test paths from bot_main.py logic
        paths = [
            "/dayzxb_missions/dayzOffline.chernarusplus",
            "/dayzxb/profile",
            "/dayzxb/config/RotateLogs",
        ]

        found_logs = []

        for p in paths:
            print(f"Checking {p}...")
            try:
                ftp.cwd(p)
                files = ftp.nlst()
                logs = [
                    f
                    for f in files
                    if f.upper().endswith(".ADM") or f.upper().endswith(".RPT")
                ]
                print(f"  -> Found {len(logs)} log files.")
                if logs:
                    found_logs.extend([f"{p}/{f}" for f in logs])
            except Exception as e:
                print(f"  -> Failed: {e}")

        ftp.quit()

        if found_logs:
            print(f"\nSUCCESS! Found {len(found_logs)} logs.")
            print(f"Latest: {found_logs[-1]}")
        else:
            print("\nWARNING: No logs found in standard paths.")

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    test_ftp()
