import os
import sys
from ftplib import FTP
from dotenv import load_dotenv

# Load env variables (same as diagnose_spawns)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, ".env"))

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PORT = int(os.getenv("FTP_PORT", 21))


def connect_ftp():
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"Connected to {FTP_HOST}")
        return ftp
    except Exception as e:
        print(f"FTP Connection failed: {e}")
        return None


def find_mission_path(ftp):
    # Same logic as diagnose_spawns to find the correct path
    possible_roots = ["/dayzxb_missions", "/dayz_missions", "/mpmissions"]

    try:
        ftp.cwd("/")
        roots = ftp.nlst()
        print(f"Root folders: {roots}")

        mission_root = None
        for root in possible_roots:
            # Need to check if root is in roots list OR just try to CWD?
            # ftp.nlst() might return full paths or just names.
            # safe matching:
            clean_root = root.strip("/")
            if clean_root in roots or root in roots:
                mission_root = root
                break

        if not mission_root:
            print("Could not find mission root folder.")
            return None

        print(f"Checking mission root: {mission_root}")
        ftp.cwd(mission_root)
        missions = ftp.nlst()
        print(f"Missions found: {missions}")

        if len(missions) > 0:
            target_mission = missions[
                0
            ]  # Assume first mission is the active one for now
            print(f"Targeting Mission: {target_mission}")
            return f"{mission_root}/{target_mission}"

    except Exception as e:
        print(f"Error traversing: {e}")
        return None


def upload_fix():
    print("--- STARTING UPLOAD ---")
    ftp = connect_ftp()
    if not ftp:
        print("Aborting upload due to connection failure.")
        return

    mission_path = find_mission_path(ftp)
    if not mission_path:
        print("Could not determine mission path.")
        ftp.quit()
        return

    # Target file
    # cfgeventspawns.xml is usually in the mission root, NOT in /db (events.xml is in /db)
    # Based on previous retrieval: Spawns Path: .../mission/cfgeventspawns.xml
    remote_file = f"{mission_path}/cfgeventspawns.xml"
    local_file = "clean_cfgeventspawns.xml"

    print(f"Uploading local '{local_file}' to remote '{remote_file}'...")

    try:
        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR {remote_file}", f)
        print("UPLOAD SUCCESSFUL!")
    except Exception as e:
        print(f"Upload failed: {e}")

    ftp.quit()
    print("--- DONE ---")


if __name__ == "__main__":
    upload_fix()
