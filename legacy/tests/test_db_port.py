import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url:
    # Try port 5432
    new_url = url.replace(":6543", ":5432")
    print(f"Testing Port 5432: {new_url.split('@')[-1]}")
    try:
        conn = psycopg2.connect(new_url)
        print("Success! Port 5432 works.")
        conn.close()
    except Exception as e:
        print(f"Failed Port 5432: {e}")
