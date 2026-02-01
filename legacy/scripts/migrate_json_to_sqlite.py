import json
import sqlite3
import os

DB_FILE = "bigode_unified.db"


def migrate_data():
    print("Migrating data from JSON to SQLite...")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # 1. Migrate Users & Economy
    print("- Migrating Economy & Users...")
    try:
        if os.path.exists("economy.json"):
            with open("economy.json", "r", encoding="utf-8") as f:
                economy_data = json.load(f)

            for discord_id, data in economy_data.items():
                balance = data.get("balance", 0)

                # Check link to get gamertag if possible (later) or just insert what we have
                cur.execute(
                    "INSERT OR IGNORE INTO users (discord_id, balance, created_at) VALUES (?, ?, datetime('now'))",
                    (discord_id, balance),
                )
                cur.execute(
                    "UPDATE users SET balance = ? WHERE discord_id = ?",
                    (balance, discord_id),
                )

                # Inventory
                inventory = data.get("inventory", {})

                # Get user_id
                cur.execute("SELECT id FROM users WHERE discord_id = ?", (discord_id,))
                user_row = cur.fetchone()
                if user_row:
                    user_id = user_row[0]

                    for item_key, item_data in inventory.items():
                        count = item_data.get("count", 1)
                        if isinstance(item_data, int):  # Handle old format if any
                            count = item_data

                        cur.execute(
                            "INSERT OR IGNORE INTO user_items (user_id, discord_id, item_key, quantity) VALUES (?, ?, ?, ?)",
                            (user_id, discord_id, item_key, count),
                        )
    except Exception as e:
        print(f"Error migrating economy: {e}")

    # 2. Migrate Links (Gamertags)
    print("- Migrating Gamertag Links...")
    try:
        if os.path.exists("links.json"):
            with open("links.json", "r", encoding="utf-8") as f:
                links = json.load(f)

            for discord_id, gamertag in links.items():
                # Ensure user exists
                cur.execute(
                    "INSERT OR IGNORE INTO users (discord_id, created_at) VALUES (?, datetime('now'))",
                    (discord_id,),
                )
                cur.execute(
                    "UPDATE users SET nitrado_gamertag = ? WHERE discord_id = ?",
                    (gamertag, discord_id),
                )
    except Exception as e:
        print(f"Error migrating links: {e}")

    # 3. Migrate Clans
    print("- Migrating Clans...")
    try:
        if os.path.exists("clans.json"):
            with open("clans.json", "r", encoding="utf-8") as f:
                clans = json.load(f)

            for tag, data in clans.items():
                name = data.get("name", tag)
                leader_id = data.get("leader")
                balance = data.get("balance", 0)
                banner = data.get("banner", "")

                if not leader_id:
                    continue

                # Upsert Clan
                cur.execute(
                    "INSERT OR IGNORE INTO clans (name, leader_discord_id, balance, banner_url, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                    (name, str(leader_id), balance, banner),
                )

                # Get Clan ID
                cur.execute("SELECT id FROM clans WHERE name = ?", (name,))
                clan_row = cur.fetchone()

                if clan_row:
                    clan_id = clan_row[0]
                    # Update balance just in case
                    cur.execute(
                        "UPDATE clans SET balance = ? WHERE id = ?", (balance, clan_id)
                    )

                    # Add Leader
                    cur.execute(
                        "INSERT OR IGNORE INTO clan_members (clan_id, discord_id, role, joined_at) VALUES (?, ?, 'leader', datetime('now'))",
                        (clan_id, str(leader_id)),
                    )

                    # Add Members
                    members = data.get("members", [])
                    if isinstance(members, list):
                        for m_id in members:
                            if str(m_id) != str(leader_id):
                                cur.execute(
                                    "INSERT OR IGNORE INTO clan_members (clan_id, discord_id, role, joined_at) VALUES (?, ?, 'member', datetime('now'))",
                                    (clan_id, str(m_id)),
                                )

    except Exception as e:
        print(f"Error migrating clans: {e}")

    conn.commit()
    conn.close()
    print("Migration completed!")


if __name__ == "__main__":
    migrate_data()
