import xml.etree.ElementTree as ET
import sys


def parse_coords(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return {}

    events = {}

    for event in root.findall("event"):
        name = event.get("name")
        coords = []
        for pos in event.findall("pos"):
            # Round coordinates to 1 decimal place to handle slight variations if any
            # though usually they are exact strings in XML copy-paste errors
            x = float(pos.get("x"))
            z = float(pos.get("z"))
            coords.append((x, z))

        events[name] = set(coords)

    return events


def calculate_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def check_overlap(events, target_event_name, threshold=10.0):
    if target_event_name not in events:
        print(f"Target event '{target_event_name}' not found in file.")
        return

    target_coords = list(events[target_event_name])  # Convert to list for iteration
    print(
        f"Checking proxmity (< {threshold}m) for '{target_event_name}' ({len(target_coords)} positions)..."
    )

    collision_found = False
    for name, coords in events.items():
        if name == target_event_name:
            continue

        if (
            name != "StaticHeliCrash"
            and name != "StaticPoliceCar"
            and name != "StaticPoliceSituation"
        ):
            continue

        count = 0
        for tx, tz in target_coords:
            for ox, oz in coords:
                dist = calculate_distance((tx, tz), (ox, oz))
                if dist < threshold:
                    if count == 0:
                        print(f"!!! PROXIMITY COLLISION with '{name}' !!!")
                        collision_found = True

                    print(
                        f"   -> Distance {dist:.2f}m | Target: ({tx}, {tz}) vs {name}: ({ox}, {oz})"
                    )
                    count += 1
                    if count >= 10:  # Increased limit to see more
                        print("      ... and more.")
                        break  # Next event
            if count >= 10:
                break

    if not collision_found:
        print(f"No collisions within {threshold}m found for {target_event_name}.")


if __name__ == "__main__":
    file_path = "temp_spawns.xml"
    events = parse_coords(file_path)

    print("--- CHECKING TRUCK COLLISIONS (50m Radius) ---")
    check_overlap(events, "VehicleTruck01", threshold=50.0)
