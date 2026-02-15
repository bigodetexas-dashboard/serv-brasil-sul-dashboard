"""One-time migration: JSON files -> SQLite (bigode_unified.db)"""
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Migrate players_db.json -> users table
with open("players_db.json", "r", encoding="utf-8") as f:
    players = json.load(f)

migrated_players = 0
for gamertag, stats in players.items():
    cur.execute("SELECT id FROM users WHERE nitrado_gamertag = ?", (gamertag,))
    row = cur.fetchone()
    if row:
        cur.execute(
            """UPDATE users SET kills=?, deaths=?, killstreak=?, best_killstreak=?,
            longest_shot=?, total_playtime=?, weapons_stats=?, last_death_time=?, first_seen=?
            WHERE nitrado_gamertag=?""",
            (stats.get("kills", 0), stats.get("deaths", 0), stats.get("killstreak", 0),
             stats.get("best_killstreak", 0), stats.get("longest_shot", 0),
             stats.get("total_playtime", 0), json.dumps(stats.get("weapons_stats", {})),
             stats.get("last_death_time", 0), stats.get("first_seen", 0), gamertag),
        )
    else:
        # Use placeholder discord_id for unlinked players (UNIQUE NOT NULL constraint)
        placeholder_id = f"unlinked_{gamertag}"
        cur.execute(
            """INSERT INTO users (discord_id, discord_username, nitrado_gamertag, balance,
            kills, deaths, killstreak, best_killstreak, longest_shot, total_playtime,
            weapons_stats, last_death_time, first_seen)
            VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (placeholder_id, "", gamertag,
             stats.get("kills", 0), stats.get("deaths", 0), stats.get("killstreak", 0),
             stats.get("best_killstreak", 0), stats.get("longest_shot", 0),
             stats.get("total_playtime", 0), json.dumps(stats.get("weapons_stats", {})),
             stats.get("last_death_time", 0), stats.get("first_seen", 0)),
        )
    migrated_players += 1
print(f"Players migrated: {migrated_players}")

# 2. Migrate links.json -> update discord_id on users that match gamertag
with open("links.json", "r", encoding="utf-8") as f:
    links = json.load(f)

for gamertag, discord_id in links.items():
    cur.execute("UPDATE users SET discord_id = ? WHERE nitrado_gamertag = ?",
                (str(discord_id), gamertag))
    if cur.rowcount == 0:
        cur.execute(
            "INSERT INTO users (discord_id, discord_username, nitrado_gamertag) VALUES (?, ?, ?)",
            (str(discord_id), "", gamertag),
        )
    print(f"  Link: {gamertag} -> {discord_id}")

# 3. Migrate economy.json -> update users with economy data
with open("economy.json", "r", encoding="utf-8") as f:
    economy = json.load(f)

for discord_id, eco_data in economy.items():
    gt = eco_data.get("gamertag", "")
    cur.execute("SELECT id FROM users WHERE discord_id = ?", (str(discord_id),))
    row = cur.fetchone()
    if row:
        cur.execute(
            """UPDATE users SET balance=?, inventory=?, transactions=?,
            achievements=?, favorites=?, last_daily=?, gamertag=?
            WHERE discord_id=?""",
            (eco_data.get("balance", 0),
             json.dumps(eco_data.get("inventory", {})),
             json.dumps(eco_data.get("transactions", [])),
             json.dumps(eco_data.get("achievements", {})),
             json.dumps(eco_data.get("favorites", [])),
             eco_data.get("last_daily"),
             gt, str(discord_id)),
        )
    else:
        cur.execute(
            """INSERT INTO users (discord_id, discord_username, nitrado_gamertag,
            balance, inventory, transactions, achievements, favorites, last_daily, gamertag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(discord_id), "", gt or "",
             eco_data.get("balance", 0),
             json.dumps(eco_data.get("inventory", {})),
             json.dumps(eco_data.get("transactions", [])),
             json.dumps(eco_data.get("achievements", {})),
             json.dumps(eco_data.get("favorites", [])),
             eco_data.get("last_daily"), gt),
        )
    print(f"  Economy: {discord_id} (balance={eco_data.get('balance', 0)})")

# 4. Migrate clans.json -> clans + clan_members_v2
with open("clans.json", "r", encoding="utf-8") as f:
    clans = json.load(f)

for clan_name, clan_data in clans.items():
    if clan_name == "wars":
        for war_id, war_data in clan_data.items():
            if war_data.get("active"):
                cur.execute(
                    """INSERT OR IGNORE INTO clan_wars (clan1_tag, clan2_tag, clan1_kills, clan2_kills, is_active)
                    VALUES (?, ?, ?, ?, 1)""",
                    (war_data.get("clan1", ""), war_data.get("clan2", ""),
                     war_data.get("score", {}).get(war_data.get("clan1", ""), 0),
                     war_data.get("score", {}).get(war_data.get("clan2", ""), 0)),
                )
        continue

    leader = clan_data.get("leader", "")
    members = clan_data.get("members", [])
    invites = clan_data.get("invites", [])

    cur.execute(
        """INSERT OR IGNORE INTO clans (name, tag, leader_id, balance, invites, total_kills, total_deaths)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (clan_name, clan_name, str(leader), clan_data.get("balance", 0),
         json.dumps(invites), clan_data.get("total_kills", 0),
         clan_data.get("total_deaths", 0)),
    )
    cur.execute("SELECT id FROM clans WHERE name = ?", (clan_name,))
    clan_row = cur.fetchone()
    if clan_row:
        clan_id = clan_row[0]
        cur.execute(
            "INSERT OR IGNORE INTO clan_members_v2 (clan_id, discord_id, role) VALUES (?, ?, 'leader')",
            (clan_id, str(leader)),
        )
        for mid in members:
            cur.execute(
                "INSERT OR IGNORE INTO clan_members_v2 (clan_id, discord_id, role) VALUES (?, ?, 'member')",
                (clan_id, str(mid)),
            )
    print(f"  Clan: {clan_name} (leader={leader}, members={len(members)})")

# 5. Migrate bounties.json
with open("bounties.json", "r", encoding="utf-8") as f:
    bounties = json.load(f)
for target, bdata in bounties.items():
    cur.execute(
        "INSERT INTO bounties (target_gamertag, amount, placed_by, created_at) VALUES (?, ?, ?, ?)",
        (target, bdata.get("amount", 0), bdata.get("placed_by", ""), bdata.get("created_at", "")),
    )
print(f"Bounties migrated: {len(bounties)}")

# 6. Migrate alarms.json
with open("alarms.json", "r", encoding="utf-8") as f:
    alarms = json.load(f)
for alarm_key, adata in alarms.items():
    cur.execute(
        """INSERT OR IGNORE INTO alarms (alarm_key, owner_id, name, x, z, radius, telegram_id, is_group, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (alarm_key, adata.get("owner_id", ""), adata.get("name", ""),
         adata.get("x", 0), adata.get("z", 0), adata.get("radius", 100),
         adata.get("telegram_id", ""), adata.get("is_group", False),
         adata.get("created_at", "")),
    )
print(f"Alarms migrated: {len(alarms)}")

# 7. Migrate pvp_events.db events -> bigode_unified events table
pvp_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pvp_events.db")
if os.path.exists(pvp_db):
    pvp_conn = sqlite3.connect(pvp_db)
    pvp_cur = pvp_conn.cursor()
    pvp_cur.execute("SELECT event_type, game_x, game_y, game_z, weapon, killer_name, victim_name, distance, timestamp FROM events")
    events = pvp_cur.fetchall()
    for ev in events:
        cur.execute(
            """INSERT INTO events (event_type, game_x, game_y, game_z, weapon, killer_name, victim_name, distance, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", ev,
        )
    pvp_conn.close()
    print(f"PvP events migrated: {len(events)}")

conn.commit()

# Verify
print("\n=== VERIFICATION ===")
for t in ["users", "clans", "clan_members_v2", "bounties", "alarms", "events"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} rows")

conn.close()
print("\nMigration complete!")
