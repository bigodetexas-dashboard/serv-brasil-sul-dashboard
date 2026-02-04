import os
import sys
from ftplib import FTP
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load env variables
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
            return f"{mission_root}/{missions[0]}/db"
    except Exception:
        return None
    return None


def update_radius():
    ftp = connect_ftp()
    if not ftp:
        return

    db_path = find_db_path(ftp)
    if not db_path:
        print("Could not find DB path")
        ftp.quit()
        return

    remote_file = f"{db_path}/events.xml"
    local_file = "temp_events.xml"

    print(f"Downloading {remote_file}...")
    try:
        with open(local_file, "wb") as f:
            ftp.retrbinary(f"RETR {remote_file}", f.write)
    except Exception as e:
        print(f"Download failed: {e}")
        ftp.quit()
        return

    print("Updating VehicleTruck01 Radius settings...")
    try:
        tree = ET.parse(local_file)
        root = tree.getroot()

        updated = False
        for event in root.findall("event"):
            if event.get("name") == "VehicleTruck01":
                # Current values might be 1. Update to safer values.
                # User suggestion: distanceradius 300
                # saferadius is also good to increase.

                safe = event.find("saferadius")
                dist = event.find("distanceradius")

                if safe is not None:
                    safe.text = "100"  # Safe buffer
                if dist is not None:
                    dist.text = "300"  # Hard distance from other events

                print("Applied: saferadius=100, distanceradius=300")
                updated = True
                break

        if updated:
            fixed_file = "fixed_events.xml"
            tree.write(fixed_file, encoding="UTF-8", xml_declaration=True)
            print("Uploading fix...")
            with open(fixed_file, "rb") as f:
                ftp.storbinary(f"STOR {remote_file}", f)
            print("UPLOAD SUCCESSFUL!")
        else:
            print("VehicleTruck01 event not found.")

    except Exception as e:
        print(f"Error: {e}")

    ftp.quit()


if __name__ == "__main__":
    update_radius()
