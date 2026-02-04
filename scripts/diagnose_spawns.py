import os
import sys
from ftplib import FTP
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load env from project root
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


def find_events_xml(ftp):
    """Recursively search for events.xml"""
    search_paths = ["/dayz_missions", "/mpmissions"]

    target_file = None

    # Helper to walk
    def walk(path):
        nonlocal target_file
        if target_file:
            return

        try:
            ftp.cwd(path)
            items = []
            ftp.retrlines("MLSD", items.append)

            # Parse MLSD format roughly or just use nlst for simple servers
            # Nitrado supports MLSD usually.
            # Let's try simple NLST for compatibility if MLSD fails/is complex
        except:
            pass

    # Simple approach: Check standard paths
    possible_roots = []
    try:
        ftp.cwd("/")
        roots = ftp.nlst()
        print(f"Root folders: {roots}")

        # Determine mission folder
        mission_root = None
        if "dayzxb_missions" in roots:
            mission_root = "/dayzxb_missions"
        elif "dayz_missions" in roots:
            mission_root = "/dayz_missions"
        elif "mpmissions" in roots:
            mission_root = "/mpmissions"

        if mission_root:
            print(f"Checking mission root: {mission_root}")
            ftp.cwd(mission_root)
            missions = ftp.nlst()
            print(f"Missions found: {missions}")

            # Select the first mission found (usually there's only one active or it's obvious)
            target_mission = None
            if len(missions) > 0:
                target_mission = missions[0]  # Pick the first one
                print(f"Selected Mission: {target_mission}")

            if target_mission:
                # Try to download events.xml
                events_path = f"{mission_root}/{target_mission}/db/events.xml"
                spawns_path = f"{mission_root}/{target_mission}/cfgeventspawns.xml"

                print(f"Attempting to download config files from: {target_mission}")

                # Download events.xml
                try:
                    with open("temp_events.xml", "wb") as f:
                        ftp.retrbinary(f"RETR {events_path}", f.write)
                    print(f"DOWNLOADED: {events_path} -> temp_events.xml")
                except Exception as e:
                    print(f"Failed to download events.xml: {e}")

                # Download cfgeventspawns.xml (to check coordinates)
                try:
                    with open("temp_spawns.xml", "wb") as f:
                        ftp.retrbinary(f"RETR {spawns_path}", f.write)
                    print(f"DOWNLOADED: {spawns_path} -> temp_spawns.xml")
                except Exception as e:
                    print(f"Failed to download cfgeventspawns.xml: {e}")

                return events_path  # Return REMOTE path for main() to use (or skip)

    except Exception as e:
        print(f"Error traversing: {e}")

    return None


def analyze_events_xml(local_path):
    try:
        tree = ET.parse(local_path)
        root = tree.getroot()

        truck_events = []

        print("\n--- ANALYZING TRUCK EVENTS ---")
        for event in root.findall("event"):
            name = event.get("name")
            if "Truck" in name or "Vehicle" in name or "Caminhao" in name:
                print(f"Event: {name}")
                # Check children/positions
                children = [c.get("type") for c in event.findall("child")]
                print(f"  - Children: {children}")

                # Check positions (posdef, etc)
                # Sometimes they link to other events like StaticHeliCrash?
                # Or they use 'pos' params.

                # Common issue: Using the same usage name as another event
                usage = [u.get("name") for u in event.findall("usage")]
                print(f"  - Usage: {usage}")

                # If usage is 'Military' or 'Police', it might spawn on those points.
                if "HeliCrash" in str(children) or "Police" in str(children):
                    print("  !!! ALERT: This event seems linked to Heli/Police!")

    except Exception as e:
        print(f"XML Parse Error: {e}")


def main():
    ftp = connect_ftp()
    if not ftp:
        return

    remote_path = find_events_xml(ftp)
    if remote_path:
        local_filename = "temp_events.xml"
        try:
            with open(local_filename, "wb") as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write)
            print(f"Downloaded {local_filename}")

            analyze_events_xml(local_filename)
        except Exception as e:
            print(f"Download error: {e}")
    else:
        print("Could not find events.xml automatically.")

    ftp.quit()


if __name__ == "__main__":
    main()
