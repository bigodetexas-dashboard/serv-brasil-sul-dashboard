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
            return None

        ftp.cwd(mission_root)
        missions = ftp.nlst()
        if len(missions) > 0:
            return f"{mission_root}/{missions[0]}/db"
    except Exception:
        return None
    return None


def update_or_create_child(parent, tag, text=None, attrib=None):
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    if text is not None:
        child.text = str(text)
    if attrib is not None:
        child.attrib = attrib
    return child


def fix_types():
    ftp = connect_ftp()
    if not ftp:
        return

    db_path = find_db_path(ftp)
    if not db_path:
        print("Could not find DB path")
        ftp.quit()
        return

    remote_file = f"{db_path}/types.xml"
    local_file = "temp_types.xml"

    # ensure we have the latest
    print(f"Downloading {remote_file}...")
    try:
        with open(local_file, "wb") as f:
            ftp.retrbinary(f"RETR {remote_file}", f.write)
    except Exception as e:
        print(f"Download failed: {e}")
        ftp.quit()
        return

    print("Requesting 50 Trucks, 45 Days Lifetime...")

    try:
        tree = ET.parse(local_file)
        root = tree.getroot()

        target_type = "Truck_01_Covered"
        found = False

        for type_el in root.findall("type"):
            if type_el.get("name") == target_type:
                found = True
                print(f"Updating '{target_type}'...")

                # Apply User Config + Safe Defaults
                update_or_create_child(type_el, "nominal", "50")
                update_or_create_child(type_el, "lifetime", "3888000")  # 45 days
                update_or_create_child(type_el, "restock", "0")
                update_or_create_child(type_el, "min", "35")  # ~70% of nominal
                update_or_create_child(type_el, "quantmin", "-1")
                update_or_create_child(type_el, "quantmax", "-1")
                update_or_create_child(type_el, "cost", "100")

                update_or_create_child(
                    type_el,
                    "flags",
                    attrib={
                        "count_in_cargo": "0",
                        "count_in_hoarder": "0",
                        "count_in_map": "1",
                        "count_in_player": "0",
                    },
                )

                update_or_create_child(type_el, "category", attrib={"name": "vehicles"})

                print("Update complete.")
                break

        if not found:
            print(f"Error: '{target_type}' not found in file!")
            ftp.quit()
            return

        # Save fixed file
        fixed_file = "fixed_types.xml"
        tree.write(fixed_file, encoding="UTF-8", xml_declaration=True)

        # Upload
        print(f"Uploading fix to {remote_file}...")
        with open(fixed_file, "rb") as f:
            ftp.storbinary(f"STOR {remote_file}", f)
        print("UPLOAD SUCCESSFUL!")

    except Exception as e:
        print(f"Processing error: {e}")

    ftp.quit()


if __name__ == "__main__":
    fix_types()
