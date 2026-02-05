import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SQLITE_DB_PATH = "bigode_unified.db"
PG_DB_URL = (
    os.getenv("DATABASE_URL")
    or "postgresql://bigode_user:bigode_password@localhost:5432/bigode_unified"
)


def get_sqlite_conn():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"âŒ SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(SQLITE_DB_PATH)


def get_pg_conn():
    try:
        return psycopg2.connect(PG_DB_URL)
    except Exception as e:
        print(f"âŒ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)


def migrate_table(sqlite_cursor, pg_cursor, table_name):
    print(f"ðŸ“¦ Migrating table '{table_name}'...", end=" ")

    # Get data from SQLite
    try:
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("Skipped (No data)")
            return

        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        # Insert into PostgreSQL
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s ON CONFLICT DO NOTHING"
        execute_values(pg_cursor, query, rows)

        print(f"âœ… Executed ({len(rows)} rows)")

        # Update sequence if ID column exists
        if "id" in columns:
            pg_cursor.execute(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 1)) FROM {table_name};"
            )

    except Exception as e:
        print(f"âŒ Error: {e}")


def main():
    print("ðŸš€ Starting Migration: SQLite -> PostgreSQL")

    sqlite_conn = get_sqlite_conn()
    pg_conn = get_pg_conn()

    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    # 1. APPLY SCHEMAS
    print("\nðŸ“œ Applying PostgreSQL Schemas...")
    try:
        # Core Schema
        with open("scripts/schema_core_postgres.sql", "r", encoding="utf-8") as f:
            print("   - Applying Core Schema...")
            pg_cur.execute(f.read())

        # Achievements Schema (New Logic)
        # Note: We need to point to the correct path where this legacy script is
        achievements_schema_path = "legacy/scripts/schema_achievements_history.sql"
        if os.path.exists(achievements_schema_path):
            with open(achievements_schema_path, "r", encoding="utf-8") as f:
                print("   - Applying Achievements/History Schema...")
                pg_cur.execute(f.read())
        else:
            print(f"âš ï¸ Warning: Achievements schema not found at {achievements_schema_path}")

        pg_conn.commit()
        print("âœ… Schemas Applied Successfully!")
    except Exception as e:
        pg_conn.rollback()
        print(f"âŒ Error applying schema: {e}")
        sys.exit(1)

    # 2. MIGRATE DATA
    print("\nðŸ“¦ Migrating Data...")

    tables = [
        "users",
        "clans",
        "clan_members",
        "transactions",
        "shop_items",  # Corrected name from items? verifying sqlite schema
        "bounties",
        "pvp_kills",
        "player_identities",
        "ip_history",
    ]
    # Note: excluding 'user_achievements' etc as they don't exist in source SQLite usually

    try:
        for table in tables:
            migrate_table(sqlite_cur, pg_cur, table)

        pg_conn.commit()
        print("\nâœ¨ Migration Completed Successfully!")

    except Exception as e:
        pg_conn.rollback()
        print(f"\nðŸ”¥ Critical Error during migration: {e}")
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
