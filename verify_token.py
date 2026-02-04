import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if not token:
    print("TOKEN is None or Empty")
else:
    print(f"TOKEN length: {len(token)}")
    print(f"TOKEN starts with: {token[:5]}...")
    print(f"TOKEN ends with: ...{token[-5:]}")
    print(f"Contains spaces: {' ' in token}")
    print(f"Contains quotes: {'"' in token or "'" in token}")
