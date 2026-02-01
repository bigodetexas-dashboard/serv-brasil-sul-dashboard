import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def list_tables():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        tables = [r[0] for r in cur.fetchall()]
        print(f"Tables: {tables}")

        for table in tables:
            cur.execute(
                f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}'"
            )
            cols = cur.fetchall()
            print(f"  {table}: {cols}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    list_tables()
