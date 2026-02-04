import os
import sys
from ftplib import FTP
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

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
        return ftp
    except Exception as e:
        print(f"FTP Connection failed: {e}")
        return None


def find_db_path(ftp):
    possible_roots = ["/dayzxb_missions", "/dayz_missions", "/mpmissions"]
    try:
        ftp.cwd("/")
        roots = ftp.nlst()
        mission_root = None
        for root in possible_roots:
            if root.strip("/") in roots or root in roots:
                mission_root = root
                break

        if not mission_root:
            return None

        ftp.cwd(mission_root)
        missions = ftp.nlst()
        if len(missions) > 0:
            return f"{mission_root}/{missions[0]}"  # cfgeventgroups usually in mission root, sometimes in db?
            # usually cfgeventgroups.xml is in mission folder alongside cfgeventspawns.xml
    except Exception:
        return None
    return None


def check_groups():
    ftp = connect_ftp()
    if not ftp:
        return

    mission_path = find_db_path(ftp)
    if not mission_path:
        print("Could not find mission path")
        ftp.quit()
        return

    remote_file = f"{mission_path}/cfgeventgroups.xml"
    local_file = "temp_groups.xml"

    print(f"Downloading {remote_file}...")
    try:
        with open(local_file, "wb") as f:
            ftp.retrbinary(f"RETR {remote_file}", f.write)
    except Exception as e:
        print(f"Download failed (maybe file doesn't exist?): {e}")
        # Try db folder just in case
        try:
            remote_file_db = f"{mission_path}/db/cfgeventgroups.xml"
            print(f"Trying {remote_file_db}...")
            with open(local_file, "wb") as f:
                ftp.retrbinary(f"RETR {remote_file_db}", f.write)
        except Exception as e2:
            print(f"Download failed again: {e2}")
            ftp.quit()
            return

    ftp.quit()

    print("\n--- ANALYZING GROUPS ---")
    try:
        tree = ET.parse(local_file)
        root = tree.getroot()

        truck_group_found = False

        for group in root.findall("group"):
            name = group.get("name")
            if "Truck" in name or "Vehicle" in name:
                print(f"Found Group: '{name}'")
                children = [
                    c.get("type") or c.get("name") for c in group.findall("child")
                ]
                print(f"  - Children: {children}")

                if name == "TruckSpawns":
                    truck_group_found = True

        if not truck_group_found:
            print("Group 'TruckSpawns' NOT FOUND.")

    except Exception as e:
        print(f"XML Parse Error: {e}")


if __name__ == "__main__":
    check_groups()
