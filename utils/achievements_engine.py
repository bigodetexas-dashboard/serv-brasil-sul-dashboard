import sqlite3
import os
import datetime
import json

# Unified DB Path
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db"
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class AchievementsEngine:
    @staticmethod
    def log_activity(discord_id, event_type, icon, title, description, details=None):
        """Logs an event to activity_history."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            details_str = json.dumps(details) if details else "{}"
            cur.execute(
                """
                INSERT INTO activity_history (discord_id, event_type, icon, title, description, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
                (str(discord_id), event_type, icon, title, description, details_str),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"[ACHIEVEMENT ENGINE ERROR] Failed to log activity: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_progress(discord_id, achievement_key, increment=1):
        """Updates progress and unlocks achievement if target reached."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Get current progress and max
            cur.execute(
                """
                SELECT ua.progress, ua.unlocked, a.max_progress, a.name, a.reward, a.icon
                FROM achievements a
                LEFT JOIN user_achievements ua
                ON a.achievement_key = ua.achievement_key AND ua.discord_id = ?
                WHERE a.achievement_key = ?
            """,
                (str(discord_id), achievement_key),
            )

            row = cur.fetchone()
            if not row:
                # Achievement might exist in definitions but not in user_achievements yet
                # Or achievement key is wrong. Let's check definitions first.
                cur.execute(
                    "SELECT max_progress, name, reward, icon FROM achievements WHERE achievement_key = ?",
                    (achievement_key,),
                )
                def_row = cur.fetchone()
                if not def_row:
                    print(f"[ACHIEVEMENT] Unknown key: {achievement_key}")
                    return False

                # Init user progress
                current_progress = 0
                max_progress = def_row["max_progress"]
                unlocked = False
                name = def_row["name"]
                icon = def_row["icon"]
            else:
                current_progress = row["progress"] if row["progress"] else 0
                max_progress = row["max_progress"]
                unlocked = row["unlocked"] if row["unlocked"] else False
                name = row["name"]
                icon = row["icon"]

            if unlocked:
                return False  # Already done

            new_progress = current_progress + increment
            new_unlocked = new_progress >= max_progress

            if new_unlocked:
                print(f"[ACHIEVEMENT UNLOCKED] {name} for {discord_id}")
                # Log the achievement event
                AchievementsEngine.log_activity(
                    discord_id,
                    "achievement",
                    icon,
                    "Conquista Desbloqueada!",
                    f"Você desbloqueou: {name}",
                    {"key": achievement_key},
                )

            # Upsert
            cur.execute(
                """
                INSERT INTO user_achievements (discord_id, achievement_key, progress, unlocked, unlocked_at, updated_at)
                VALUES (?, ?, ?, ?, CASE WHEN ? THEN datetime('now') ELSE NULL END, datetime('now'))
                ON CONFLICT(discord_id, achievement_key) DO UPDATE SET
                    progress = excluded.progress,
                    unlocked = excluded.unlocked,
                    unlocked_at = excluded.unlocked_at,
                    updated_at = excluded.updated_at
            """,
                (
                    str(discord_id),
                    achievement_key,
                    new_progress,
                    1 if new_unlocked else 0,
                    1 if new_unlocked else 0,
                ),
            )

            conn.commit()
            return new_unlocked

        except Exception as e:
            print(f"[ACHIEVEMENT ENGINE ERROR] Update failed: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def process_kill(killer_id, victim_id, weapon, distance):
        """Processed a kill event: Logs history and checks achievements."""
        # 1. Log History
        AchievementsEngine.log_activity(
            killer_id,
            "kill",
            "⚔️",
            "Eliminação Confirmada",
            f"Eliminou um jogador a {distance}m",
            {"weapon": weapon, "distance": distance, "victim": victim_id},
        )

        # 2. Update Achievements
        # First Blood
        AchievementsEngine.update_progress(killer_id, "first_kill", 1)
        # Killer stats
        AchievementsEngine.update_progress(killer_id, "killer_10", 1)
        AchievementsEngine.update_progress(killer_id, "killer_50", 1)
        AchievementsEngine.update_progress(killer_id, "killer_100", 1)
        AchievementsEngine.update_progress(killer_id, "killer_500", 1)
