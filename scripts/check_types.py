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
        print(f"Connected to {FTP_HOST}")
        return ftp
    except Exception as e:
        print(f"FTP Connection failed: {e}")
        return None


def find_db_path(ftp):
    # Search for mission/db folder where types.xml resides
    possible_roots = ["/dayzxb_missions", "/dayz_missions", "/mpmissions"]

    try:
        ftp.cwd("/")
        roots = ftp.nlst()

        mission_root = None
        for root in possible_roots:
            clean_root = root.strip("/")
            if clean_root in roots or root in roots:
                mission_root = root
                break

        if not mission_root:
            print("Could not find mission root folder.")
            return None

        ftp.cwd(mission_root)
        missions = ftp.nlst()

        if len(missions) > 0:
            target_mission = missions[0]
            print(f"Targeting Mission: {target_mission}")
            return f"{mission_root}/{target_mission}/db"

    except Exception as e:
        print(f"Error traversing: {e}")
        return None


def check_types():
    ftp = connect_ftp()
    if not ftp:
        return

    db_path = find_db_path(ftp)
    if not db_path:
        ftp.quit()
        return

    remote_file = f"{db_path}/types.xml"
    local_file = "temp_types.xml"

    print(f"Downloading {remote_file}...")
    try:
        with open(local_file, "wb") as f:
            ftp.retrbinary(f"RETR {remote_file}", f.write)
        print("Download successful.")
    except Exception as e:
        print(f"Failed to download types.xml: {e}")
        ftp.quit()
        return

    ftp.quit()

    # Analyze XML
    print("\n--- ANALYZING TRUCK CONFIG ---")
    try:
        tree = ET.parse(local_file)
        root = tree.getroot()

        target_type = "Truck_01_Covered"
        found = False

        for type_el in root.findall("type"):
            if type_el.get("name") == target_type:
                found = True
                print(f"Found <type name='{target_type}'>")

                # Helper to print child text
                def print_val(tag):
                    child = type_el.find(tag)
                    val = child.text if child is not None else "MISSING"
                    print(f"  <{tag}>{val}</{tag}>")

                print_val("nominal")
                print_val("lifetime")
                print_val("restock")
                print_val("min")
                print_val("quantmin")
                print_val("quantmax")
                print_val("cost")

                flags = type_el.find("flags")
                if flags is not None:
                    print(
                        f"  <flags count_in_cargo='{flags.get('count_in_cargo')}' count_in_hoarder='{flags.get('count_in_hoarder')}' count_in_map='{flags.get('count_in_map')}' count_in_player='{flags.get('count_in_player')}'/>"
                    )
                else:
                    print("  <flags ... /> MISSING")

                cat = type_el.find("category")
                if cat is not None:
                    print(f"  <category name='{cat.get('name')}'/>")
                else:
                    print("  <category ... /> MISSING")

                break

        if not found:
            print(f"Type '{target_type}' NOT FOUND in types.xml")

    except Exception as e:
        print(f"XML Parse Error: {e}")


if __name__ == "__main__":
    check_types()
