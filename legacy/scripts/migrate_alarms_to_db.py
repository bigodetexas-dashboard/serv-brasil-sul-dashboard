import json
import sqlite3
import os

DB_FILE = "bigode_unified.db"
JSON_FILE = "alarms.json"


def migrate_alarms():
    if not os.path.exists(JSON_FILE):
        print(f"{JSON_FILE} not found.")
        return

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            alarms = json.load(f)

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        count = 0
        for alarm_id, data in alarms.items():
            # data: {"name": "...", "owner_id": "...", "x": ..., "z": ..., "radius": ...}
            cur.execute(
                "INSERT INTO bases (owner_id, name, x, z, radius) VALUES (?, ?, ?, ?, ?)",
                (
                    str(data["owner_id"]),
                    data["name"],
                    data["x"],
                    data["z"],
                    data["radius"],
                ),
            )
            count += 1

        conn.commit()
        conn.close()
        print(f"Migrated {count} alarms to bases table.")

    except Exception as e:
        print(f"Migration error: {e}")


if __name__ == "__main__":
    migrate_alarms()
