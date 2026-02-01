import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def check_tables():
    print(f"Connecting to: {DATABASE_URL.split('@')[-1] if DATABASE_URL else 'None'}")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        tables = ["clans", "clan_members", "clan_members_v2"]
        for table in tables:
            print(f"\nChecking table: {table}")
            try:
                cur.execute(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"
                )
                columns = cur.fetchall()
                if columns:
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
                else:
                    print("  Table not found.")
            except Exception as e:
                print(f"  Error checking table {table}: {e}")
                conn.rollback()

        conn.close()
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    check_tables()
