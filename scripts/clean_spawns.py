import xml.etree.ElementTree as ET
import sys
import copy


def calculate_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def clean_spawns(xml_file, output_file, threshold=100.0):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return

    # 1. Collect Avoidance Zones (Heli, Police, etc)
    avoidance_points = []
    avoidance_events = [
        "StaticHeliCrash",
        "StaticPoliceCar",
        "StaticPoliceSituation",
        "StaticMilitaryConvoy",
    ]

    print(f"Loading avoidance zones from: {avoidance_events}")

    for event in root.findall("event"):
        name = event.get("name")
        if name in avoidance_events:
            for pos in event.findall("pos"):
                x = float(pos.get("x"))
                z = float(pos.get("z"))
                avoidance_points.append((x, z))

    print(f"Found {len(avoidance_points)} points to avoid (Threshold: {threshold}m).")

    # 2. Filter Truck Spawns
    truck_event_name = "VehicleTruck01"
    truck_event = None

    # Find the truck event element
    for event in root.findall("event"):
        if event.get("name") == truck_event_name:
            truck_event = event
            break

    if not truck_event:
        print(f"Event {truck_event_name} not found!")
        return

    original_count = 0
    removed_count = 0
    kept_positions = []

    # Iterate over a copy of the list so we can modify the original or just rebuild it
    # Easier to clear children and re-add valid ones

    # First, separate 'pos' elements from others (like 'zone')
    all_children = list(truck_event)
    pos_elements = [child for child in all_children if child.tag == "pos"]
    other_elements = [child for child in all_children if child.tag != "pos"]

    print(f"Analyzing {len(pos_elements)} truck positions...")

    valid_pos_elements = []

    for pos in pos_elements:
        original_count += 1
        tx = float(pos.get("x"))
        tz = float(pos.get("z"))

        collision = False
        for ax, az in avoidance_points:
            dist = calculate_distance((tx, tz), (ax, az))
            if dist < threshold:
                collision = True
                print(
                    f"   [REMOVE] Truck at ({tx:.1f}, {tz:.1f}) too close to event at ({ax:.1f}, {az:.1f}) - Dist: {dist:.1f}m"
                )
                break

        if collision:
            removed_count += 1
        else:
            valid_pos_elements.append(pos)

    # 3. Rebuild the event
    # Clear all children
    for child in list(truck_event):
        truck_event.remove(child)

    # Add back non-pos elements (like <zone>)
    for elem in other_elements:
        truck_event.append(elem)

    # Add back valid pos elements
    for elem in valid_pos_elements:
        truck_event.append(elem)

    print(
        f"Done. Removed {removed_count} conflicting spawns. Kept {len(valid_pos_elements)}."
    )

    # 4. Save
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    print(f"Saved cleaned file to: {output_file}")


if __name__ == "__main__":
    input_xml = "temp_spawns.xml"
    output_xml = "clean_cfgeventspawns.xml"
    clean_spawns(input_xml, output_xml)
