import database
from dotenv import load_dotenv
import os

load_dotenv()


def test_conn():
    print(f"URL: {os.getenv('DATABASE_URL')}")
    conn = database.get_pg_conn()
    if conn:
        print("Connection successful!")
        conn.close()
    else:
        print("Connection failed.")


if __name__ == "__main__":
    test_conn()
