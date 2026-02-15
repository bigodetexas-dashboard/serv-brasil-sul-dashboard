"""Database layer - SQLite unified storage (bigode_unified.db)"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigode_unified.db")
PVP_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pvp_events.db")


def _get_conn():
    """Returns a connection to bigode_unified.db"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _get_pvp_conn():
    """Returns a connection to pvp_events.db (heatmap/events)"""
    conn = sqlite3.connect(PVP_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes pvp_events.db"""
    conn = sqlite3.connect(PVP_DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        game_x REAL,
        game_y REAL,
        game_z REAL,
        weapon TEXT,
        killer_name TEXT,
        victim_name TEXT,
        distance REAL,
        timestamp DATETIME
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_coords ON events(game_x, game_z)")
    conn.commit()
    conn.close()


# ============================================================
# PVP EVENTS (pvp_events.db - kept separate for heatmap perf)
# ============================================================

def add_event(event_type, x, y, z, weapon, killer, victim, distance, timestamp):
    """Add a PvP event to pvp_events.db"""
    conn = sqlite3.connect(PVP_DB)
    conn.execute(
        """INSERT INTO events (event_type, game_x, game_y, game_z, weapon, killer_name, victim_name, distance, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (event_type, x, y, z, weapon, killer, victim, distance, timestamp),
    )
    conn.commit()
    conn.close()


def get_heatmap_data(since_date, grid_size=50):
    """Returns aggregated heatmap data with grid clustering."""
    conn = sqlite3.connect(PVP_DB)
    cur = conn.cursor()
    query = f"""
    SELECT
        (CAST(game_x / {grid_size} AS INT) * {grid_size}) as gx,
        (CAST(game_z / {grid_size} AS INT) * {grid_size}) as gz,
        COUNT(*) as intensity
    FROM events
    WHERE timestamp >= ? AND event_type = 'kill'
    GROUP BY gx, gz
    """
    cur.execute(query, (since_date,))
    rows = cur.fetchall()
    conn.close()
    return [{"x": r[0], "z": r[1], "count": r[2]} for r in rows]


def get_heatmap_points():
    """Returns all kill coordinates for heatmap visualization."""
    conn = sqlite3.connect(PVP_DB)
    cur = conn.cursor()
    cur.execute("""
    SELECT game_x, game_z FROM events
    WHERE event_type = 'kill' AND game_x IS NOT NULL AND game_z IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"x": r[0], "y": r[1], "value": 1} for r in rows]


def parse_rpt_line(line):
    """Parse DayZ RPT log line for kill events."""
    import re
    pattern1 = r"PlayerKill: Killer=(?P<killer>[^,]+), Victim=(?P<victim>[^,]+), Pos=<(?P<x>[-0-9.]+),\s*[-0-9.]+,\s*(?P<z>[-0-9.]+)>, Weapon=(?P<weapon>[^,]+), Distance=(?P<dist>\d+)"
    match = re.search(pattern1, line)
    if match:
        return {
            "event_type": "kill",
            "game_x": float(match.group("x")),
            "game_y": 0.0,
            "game_z": float(match.group("z")),
            "weapon": match.group("weapon").strip(),
            "killer_name": match.group("killer").strip(),
            "victim_name": match.group("victim").strip(),
            "distance": float(match.group("dist")),
            "timestamp": datetime.now(),
        }
    pattern2 = r"Kill: (?P<killer>\w+) killed (?P<victim>\w+) at \[(?P<x>[-0-9.]+),\s*[-0-9.]+,\s*(?P<z>[-0-9.]+)\] with (?P<weapon>\w+)"
    match = re.search(pattern2, line)
    if match:
        return {
            "event_type": "kill",
            "game_x": float(match.group("x")),
            "game_y": 0.0,
            "game_z": float(match.group("z")),
            "weapon": match.group("weapon").strip(),
            "killer_name": match.group("killer").strip(),
            "victim_name": match.group("victim").strip(),
            "distance": 0.0,
            "timestamp": datetime.now(),
        }
    return None


# ============================================================
# PLAYERS
# ============================================================

def get_all_players():
    """Returns all players as dict {gamertag: stats}"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT nitrado_gamertag, kills, deaths, killstreak, best_killstreak,
        longest_shot, total_playtime, weapons_stats, last_death_time, first_seen
        FROM users WHERE nitrado_gamertag IS NOT NULL AND nitrado_gamertag != ''""")
    rows = cur.fetchall()
    conn.close()
    result = {}
    for r in rows:
        gt = r["nitrado_gamertag"]
        ws = r["weapons_stats"]
        try:
            ws = json.loads(ws) if ws else {}
        except (json.JSONDecodeError, TypeError):
            ws = {}
        result[gt] = {
            "kills": r["kills"] or 0,
            "deaths": r["deaths"] or 0,
            "killstreak": r["killstreak"] or 0,
            "best_killstreak": r["best_killstreak"] or 0,
            "longest_shot": r["longest_shot"] or 0,
            "total_playtime": r["total_playtime"] or 0,
            "weapons_stats": ws,
            "last_death_time": r["last_death_time"] or 0,
            "first_seen": r["first_seen"] or 0,
        }
    return result


def get_player(gamertag):
    """Returns player stats by gamertag."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT kills, deaths, killstreak, best_killstreak, longest_shot,
        total_playtime, weapons_stats, last_death_time, first_seen
        FROM users WHERE nitrado_gamertag = ?""", (gamertag,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    ws = r["weapons_stats"]
    try:
        ws = json.loads(ws) if ws else {}
    except (json.JSONDecodeError, TypeError):
        ws = {}
    return {
        "kills": r["kills"] or 0,
        "deaths": r["deaths"] or 0,
        "killstreak": r["killstreak"] or 0,
        "best_killstreak": r["best_killstreak"] or 0,
        "longest_shot": r["longest_shot"] or 0,
        "total_playtime": r["total_playtime"] or 0,
        "weapons_stats": ws,
        "last_death_time": r["last_death_time"] or 0,
        "first_seen": r["first_seen"] or 0,
    }


def save_player(gamertag, data):
    """Saves player stats by gamertag (upsert)."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE nitrado_gamertag = ?", (gamertag,))
    row = cur.fetchone()
    ws = json.dumps(data.get("weapons_stats", {}))
    if row:
        cur.execute(
            """UPDATE users SET kills=?, deaths=?, killstreak=?, best_killstreak=?,
            longest_shot=?, total_playtime=?, weapons_stats=?, last_death_time=?, first_seen=?
            WHERE nitrado_gamertag=?""",
            (data.get("kills", 0), data.get("deaths", 0), data.get("killstreak", 0),
             data.get("best_killstreak", 0), data.get("longest_shot", 0),
             data.get("total_playtime", 0), ws,
             data.get("last_death_time", 0), data.get("first_seen", 0), gamertag),
        )
    else:
        placeholder_id = f"unlinked_{gamertag}"
        cur.execute(
            """INSERT INTO users (discord_id, nitrado_gamertag, kills, deaths, killstreak,
            best_killstreak, longest_shot, total_playtime, weapons_stats, last_death_time, first_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (placeholder_id, gamertag,
             data.get("kills", 0), data.get("deaths", 0), data.get("killstreak", 0),
             data.get("best_killstreak", 0), data.get("longest_shot", 0),
             data.get("total_playtime", 0), ws,
             data.get("last_death_time", 0), data.get("first_seen", 0)),
        )
    conn.commit()
    conn.close()


def sync_gamertag_to_db(discord_id, gamertag):
    """Sync gamertag to SQLite user record."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET nitrado_gamertag = ? WHERE discord_id = ?",
                    (gamertag, str(discord_id)))
        if cur.rowcount == 0 and gamertag:
            cur.execute(
                "INSERT OR IGNORE INTO users (discord_id, discord_username, nitrado_gamertag) VALUES (?, ?, ?)",
                (str(discord_id), "", gamertag),
            )
        conn.commit()
        conn.close()
    except Exception:
        pass


# ============================================================
# ECONOMY
# ============================================================

def _parse_json_field(value, default):
    """Safely parse a JSON text field from SQLite."""
    if not value:
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def get_economy(user_id):
    """Returns economy data for a user (or all users if user_id='all')."""
    conn = _get_conn()
    cur = conn.cursor()

    if user_id == "all":
        cur.execute("""SELECT discord_id, balance, gamertag, inventory, transactions,
            achievements, favorites, last_daily, purchases FROM users
            WHERE discord_id NOT LIKE 'unlinked_%'""")
        rows = cur.fetchall()
        conn.close()
        result = {}
        for r in rows:
            result[r["discord_id"]] = {
                "balance": r["balance"] or 0,
                "gamertag": r["gamertag"] or "",
                "inventory": _parse_json_field(r["inventory"], {}),
                "transactions": _parse_json_field(r["transactions"], []),
                "achievements": _parse_json_field(r["achievements"], {}),
                "favorites": _parse_json_field(r["favorites"], []),
                "last_daily": r["last_daily"],
                "purchases": r["purchases"] or 0,
            }
        return result

    uid = str(user_id)
    cur.execute("""SELECT discord_id, balance, gamertag, inventory, transactions,
        achievements, favorites, last_daily, purchases FROM users WHERE discord_id = ?""", (uid,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return {}
    return {
        "discord_id": r["discord_id"],
        "balance": r["balance"] or 0,
        "gamertag": r["gamertag"] or "",
        "inventory": _parse_json_field(r["inventory"], {}),
        "transactions": _parse_json_field(r["transactions"], []),
        "achievements": _parse_json_field(r["achievements"], {}),
        "favorites": _parse_json_field(r["favorites"], []),
        "last_daily": r["last_daily"],
        "purchases": r["purchases"] or 0,
    }


def save_economy(user_id, data):
    """Saves economy data for a user."""
    uid = str(user_id)
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE discord_id = ?", (uid,))
    row = cur.fetchone()

    inv = json.dumps(data.get("inventory", {})) if isinstance(data.get("inventory"), dict) else data.get("inventory", "{}")
    trans = json.dumps(data.get("transactions", [])) if isinstance(data.get("transactions"), list) else data.get("transactions", "[]")
    ach = json.dumps(data.get("achievements", {})) if isinstance(data.get("achievements"), dict) else data.get("achievements", "{}")
    favs = json.dumps(data.get("favorites", [])) if isinstance(data.get("favorites"), list) else data.get("favorites", "[]")

    if row:
        cur.execute(
            """UPDATE users SET balance=?, gamertag=?, inventory=?, transactions=?,
            achievements=?, favorites=?, last_daily=?, purchases=?
            WHERE discord_id=?""",
            (data.get("balance", 0), data.get("gamertag", ""),
             inv, trans, ach, favs,
             data.get("last_daily"), data.get("purchases", 0), uid),
        )
    else:
        gt = data.get("gamertag", "")
        cur.execute(
            """INSERT INTO users (discord_id, discord_username, nitrado_gamertag,
            balance, gamertag, inventory, transactions, achievements, favorites, last_daily, purchases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uid, "", gt or "", data.get("balance", 0), gt,
             inv, trans, ach, favs,
             data.get("last_daily"), data.get("purchases", 0)),
        )
    conn.commit()
    conn.close()


def get_all_economy():
    """Returns all economy data."""
    return get_economy("all")


def get_balance(user_id):
    """Returns user balance."""
    eco = get_economy(user_id)
    return eco.get("balance", 0) if eco else 0


def update_balance(user_id, amount, transaction_type="other", details=""):
    """Updates balance and logs transaction."""
    uid = str(user_id)
    eco = get_economy(uid)
    if not eco:
        eco = {"discord_id": uid, "balance": 0, "transactions": []}

    current_balance = eco.get("balance", 0)
    new_balance = current_balance + amount
    if new_balance < 0:
        new_balance = 0

    eco["balance"] = new_balance

    transactions = eco.get("transactions", [])
    if isinstance(transactions, str):
        try:
            transactions = json.loads(transactions)
        except (json.JSONDecodeError, TypeError):
            transactions = []

    transactions.append({
        "type": transaction_type,
        "amount": amount,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "balance_after": new_balance,
    })
    if len(transactions) > 50:
        transactions = transactions[-50:]

    eco["transactions"] = transactions
    save_economy(uid, eco)
    return new_balance


def add_to_inventory(user_id, item_key, item_name):
    """Adds an item to user's virtual inventory."""
    uid = str(user_id)
    eco = get_economy(uid)
    if not eco:
        eco = {"discord_id": uid, "balance": 0, "inventory": {}}

    inventory = eco.get("inventory", {})
    if isinstance(inventory, str):
        try:
            inventory = json.loads(inventory)
        except (json.JSONDecodeError, TypeError):
            inventory = {}

    if item_key in inventory:
        inventory[item_key]["count"] += 1
    else:
        inventory[item_key] = {"name": item_name, "count": 1}

    eco["inventory"] = inventory
    eco["purchases"] = eco.get("purchases", 0) + 1
    save_economy(uid, eco)


# ============================================================
# LINKS (Discord <-> Gamertag)
# ============================================================

def get_all_links():
    """Returns all Discord<->Gamertag links as {gamertag: discord_id}"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT nitrado_gamertag, discord_id FROM users
        WHERE nitrado_gamertag IS NOT NULL AND nitrado_gamertag != ''
        AND discord_id NOT LIKE 'unlinked_%'""")
    rows = cur.fetchall()
    conn.close()
    return {r["nitrado_gamertag"]: r["discord_id"] for r in rows}


def save_link(gamertag, discord_id):
    """Creates or updates a gamertag<->discord link."""
    conn = _get_conn()
    cur = conn.cursor()
    did = str(discord_id)

    # Check if discord_id already has a user row
    cur.execute("SELECT id, nitrado_gamertag FROM users WHERE discord_id = ?", (did,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE users SET nitrado_gamertag = ? WHERE discord_id = ?", (gamertag, did))
    else:
        # Check if gamertag exists with placeholder
        cur.execute("SELECT id FROM users WHERE nitrado_gamertag = ? AND discord_id LIKE 'unlinked_%'", (gamertag,))
        placeholder_row = cur.fetchone()
        if placeholder_row:
            cur.execute("UPDATE users SET discord_id = ? WHERE id = ?", (did, placeholder_row["id"]))
        else:
            cur.execute(
                "INSERT INTO users (discord_id, discord_username, nitrado_gamertag) VALUES (?, ?, ?)",
                (did, "", gamertag),
            )
    conn.commit()
    conn.close()


def remove_link(gamertag):
    """Removes a gamertag link (sets gamertag to NULL, keeps user)."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET nitrado_gamertag = NULL WHERE nitrado_gamertag = ?", (gamertag,))
    conn.commit()
    conn.close()


def get_link_by_gamertag(gamertag):
    """Returns Discord ID linked to a gamertag."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT discord_id FROM users
        WHERE LOWER(nitrado_gamertag) = LOWER(?)
        AND discord_id NOT LIKE 'unlinked_%'""", (gamertag,))
    r = cur.fetchone()
    conn.close()
    return r["discord_id"] if r else None


def get_link_by_discord(discord_id):
    """Returns gamertag linked to a Discord ID."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nitrado_gamertag FROM users WHERE discord_id = ?", (str(discord_id),))
    r = cur.fetchone()
    conn.close()
    return r["nitrado_gamertag"] if r and r["nitrado_gamertag"] else None


# ============================================================
# CLANS
# ============================================================

def get_all_clans():
    """Returns all clans as dict {name: data}"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, tag, leader_id, balance, invites, total_kills, total_deaths FROM clans")
    clans_rows = cur.fetchall()
    result = {}
    for c in clans_rows:
        clan_id = c["id"]
        cur.execute("SELECT discord_id, role FROM clan_members_v2 WHERE clan_id = ? AND role != 'leader'", (clan_id,))
        members = [m["discord_id"] for m in cur.fetchall()]
        invites = _parse_json_field(c["invites"], [])
        result[c["name"]] = {
            "leader": c["leader_id"],
            "members": members,
            "invites": invites,
            "balance": c["balance"] or 0,
            "total_kills": c["total_kills"] or 0,
            "total_deaths": c["total_deaths"] or 0,
            "id": clan_id,
        }
    conn.close()
    return result


def get_clan(tag):
    """Returns clan data by tag/name."""
    clans = get_all_clans()
    return clans.get(tag)


def save_clan(tag, data):
    """Saves clan data (upsert)."""
    conn = _get_conn()
    cur = conn.cursor()
    leader = str(data.get("leader", ""))
    members = data.get("members", [])
    invites = json.dumps(data.get("invites", []))
    balance = data.get("balance", 0)
    total_kills = data.get("total_kills", 0)
    total_deaths = data.get("total_deaths", 0)

    cur.execute("SELECT id FROM clans WHERE name = ?", (tag,))
    row = cur.fetchone()
    if row:
        clan_id = row["id"]
        cur.execute(
            "UPDATE clans SET leader_id=?, balance=?, invites=?, total_kills=?, total_deaths=? WHERE id=?",
            (leader, balance, invites, total_kills, total_deaths, clan_id),
        )
    else:
        cur.execute(
            "INSERT INTO clans (name, tag, leader_id, balance, invites, total_kills, total_deaths) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tag, tag, leader, balance, invites, total_kills, total_deaths),
        )
        clan_id = cur.lastrowid

    # Sync members
    cur.execute("DELETE FROM clan_members_v2 WHERE clan_id = ?", (clan_id,))
    cur.execute(
        "INSERT INTO clan_members_v2 (clan_id, discord_id, role) VALUES (?, ?, 'leader')",
        (clan_id, leader),
    )
    for mid in members:
        cur.execute(
            "INSERT INTO clan_members_v2 (clan_id, discord_id, role) VALUES (?, ?, 'member')",
            (clan_id, str(mid)),
        )
    conn.commit()
    conn.close()


def save_all_clans(clans_data):
    """Saves all clans data (replaces full dataset). Used by cogs that manage wars."""
    for tag, data in clans_data.items():
        if tag == "wars":
            _save_wars(data)
            continue
        save_clan(tag, data)


def _save_wars(wars_data):
    """Saves clan wars data."""
    conn = _get_conn()
    cur = conn.cursor()
    for war_id, war_data in wars_data.items():
        c1 = war_data.get("clan1", "")
        c2 = war_data.get("clan2", "")
        score = war_data.get("score", {})
        active = war_data.get("active", True)
        cur.execute("SELECT id FROM clan_wars WHERE clan1_tag = ? AND clan2_tag = ? AND is_active = 1", (c1, c2))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE clan_wars SET clan1_kills=?, clan2_kills=?, is_active=? WHERE id=?",
                (score.get(c1, 0), score.get(c2, 0), 1 if active else 0, row["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO clan_wars (clan1_tag, clan2_tag, clan1_kills, clan2_kills, is_active) VALUES (?, ?, ?, ?, ?)",
                (c1, c2, score.get(c1, 0), score.get(c2, 0), 1 if active else 0),
            )
    conn.commit()
    conn.close()


def get_clan_wars():
    """Returns active clan wars as dict."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT clan1_tag, clan2_tag, clan1_kills, clan2_kills, started_at FROM clan_wars WHERE is_active = 1")
    rows = cur.fetchall()
    conn.close()
    wars = {}
    for r in rows:
        war_id = f"{r['clan1_tag']}_vs_{r['clan2_tag']}"
        wars[war_id] = {
            "clan1": r["clan1_tag"],
            "clan2": r["clan2_tag"],
            "active": True,
            "started_at": r["started_at"] or "",
            "score": {r["clan1_tag"]: r["clan1_kills"] or 0, r["clan2_tag"]: r["clan2_kills"] or 0},
        }
    return wars


# ============================================================
# BOUNTIES
# ============================================================

def get_all_bounties():
    """Returns all active bounties as {gamertag_lower: data}"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT target_gamertag, amount, placed_by, created_at FROM bounties WHERE is_active = 1")
    rows = cur.fetchall()
    conn.close()
    result = {}
    for r in rows:
        key = r["target_gamertag"].lower()
        if key in result:
            result[key]["amount"] += r["amount"]
        else:
            result[key] = {
                "amount": r["amount"],
                "placed_by": r["placed_by"],
                "created_at": r["created_at"],
            }
    return result


def save_bounty(gamertag, amount, placed_by):
    """Adds a new bounty."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO bounties (target_gamertag, amount, placed_by, created_at) VALUES (?, ?, ?, ?)",
        (gamertag.lower(), amount, str(placed_by), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def claim_bounty(gamertag, claimed_by):
    """Claims all active bounties on a gamertag. Returns total amount."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM bounties WHERE LOWER(target_gamertag) = LOWER(?) AND is_active = 1", (gamertag,))
    total = cur.fetchone()[0] or 0
    if total > 0:
        cur.execute(
            "UPDATE bounties SET is_active = 0, claimed_by = ?, claimed_at = ? WHERE LOWER(target_gamertag) = LOWER(?) AND is_active = 1",
            (str(claimed_by), datetime.now().isoformat(), gamertag),
        )
        conn.commit()
    conn.close()
    return total


# ============================================================
# ALARMS
# ============================================================

def get_all_alarms():
    """Returns all alarms as {alarm_key: data}"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT alarm_key, owner_id, name, x, z, radius, telegram_id, is_group, created_at FROM alarms")
    rows = cur.fetchall()
    conn.close()
    result = {}
    for r in rows:
        result[r["alarm_key"]] = {
            "owner_id": r["owner_id"],
            "name": r["name"],
            "x": r["x"],
            "z": r["z"],
            "radius": r["radius"],
            "telegram_id": r["telegram_id"],
            "is_group": bool(r["is_group"]),
            "created_at": r["created_at"],
        }
    return result


def save_alarm(alarm_key, data):
    """Saves an alarm (upsert)."""
    conn = _get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO alarms (alarm_key, owner_id, name, x, z, radius, telegram_id, is_group, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (alarm_key, data["owner_id"], data["name"], data["x"], data["z"],
         data["radius"], data["telegram_id"], data.get("is_group", False),
         data.get("created_at", datetime.now().isoformat())),
    )
    conn.commit()
    conn.close()


# ============================================================
# BASES (for dashboard/alarm proximity detection)
# ============================================================

def get_active_bases():
    """Returns list of active bases from alarms."""
    alarms = get_all_alarms()
    bases = []
    for aid, data in alarms.items():
        data["id"] = aid
        data["source"] = "alarm"
        bases.append(data)
    return bases


def check_base_permission(base_id, user_discord_id):
    """Check if user has permission on a base. Always False for alarm-based bases."""
    return False


# ============================================================
# ACHIEVEMENTS
# ============================================================

ACHIEVEMENTS_DEF = {
    "first_kill": {
        "name": "\U0001f3af Primeira Vitima",
        "description": "Mate seu primeiro jogador",
        "reward": 500,
        "check": lambda data: data.get("kills", 0) >= 1,
    },
    "assassin": {
        "name": "\U0001f480 Assassino",
        "description": "Acumule 10 kills",
        "reward": 1000,
        "check": lambda data: data.get("kills", 0) >= 10,
    },
    "serial_killer": {
        "name": "\u2620\ufe0f Serial Killer",
        "description": "Acumule 50 kills",
        "reward": 5000,
        "check": lambda data: data.get("kills", 0) >= 50,
    },
    "rich": {
        "name": "\U0001f4b0 Rico",
        "description": "Acumule 10.000 DZ Coins",
        "reward": 0,
        "check": lambda data: data.get("balance", 0) >= 10000,
    },
    "millionaire": {
        "name": "\U0001f48e Milionario",
        "description": "Acumule 100.000 DZ Coins",
        "reward": 10000,
        "check": lambda data: data.get("balance", 0) >= 100000,
    },
    "shopper": {
        "name": "\U0001f6d2 Comprador",
        "description": "Faca 10 compras na loja",
        "reward": 1000,
        "check": lambda data: data.get("purchases", 0) >= 10,
    },
    "veteran": {
        "name": "\u23f0 Veterano",
        "description": "Jogue por 50 horas",
        "reward": 5000,
        "check": lambda data: data.get("hours_played", 0) >= 50,
    },
    "clan_founder": {
        "name": "\U0001f6e1\ufe0f Fundador de Cla",
        "description": "Crie um cla",
        "reward": 0,
        "check": lambda data: data.get("clan_created", False),
    },
}


def check_achievements(user_id):
    """Check and unlock achievements for a player."""
    uid = str(user_id)
    eco = get_economy(uid)
    if not eco:
        return []

    achievements = eco.get("achievements", {})
    if isinstance(achievements, str):
        try:
            achievements = json.loads(achievements)
        except (json.JSONDecodeError, TypeError):
            achievements = {}

    gamertag = eco.get("gamertag", "")
    player_stats = get_player(gamertag) if gamertag else {}

    player_data = {
        "kills": player_stats.get("kills", 0),
        "balance": eco.get("balance", 0),
        "purchases": eco.get("purchases", 0),
        "hours_played": player_stats.get("total_playtime", 0) / 3600,
        "clan_created": False,
    }

    newly_unlocked = []
    for ach_id, ach_def in ACHIEVEMENTS_DEF.items():
        if achievements.get(ach_id, {}).get("unlocked"):
            continue
        if ach_def["check"](player_data):
            achievements[ach_id] = {
                "unlocked": True,
                "date": datetime.now().isoformat(),
            }
            if ach_def["reward"] > 0:
                eco["balance"] = eco.get("balance", 0) + ach_def["reward"]
            newly_unlocked.append((ach_id, ach_def))

    eco["achievements"] = achievements
    save_economy(uid, eco)
    return newly_unlocked


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

# These keep backward compat with bot_main.py and other modules
# that may call these functions
_get_unified_db = _get_conn
get_db_connection = _get_conn
get_connection = _get_conn


def get_pg_conn():
    """Deprecated: PostgreSQL removed. Returns None for compat."""
    return None
