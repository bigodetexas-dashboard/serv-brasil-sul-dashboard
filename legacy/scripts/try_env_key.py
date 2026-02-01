import os
import requests


def load_env_key():
    key = None
    try:
        # Try finding .env in current dir
        path = ".env"
        if not os.path.exists(path):
            print("No .env found in current directory")
            return None

        with open(path, "r") as f:
            for line in f:
                if line.strip().startswith("RENDER_API_KEY="):
                    key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    return key
    except Exception as e:
        print(f"Error reading .env: {e}")
    return None


key = load_env_key()
if not key:
    print("RENDER_API_KEY not found in .env")
else:
    # Print only last 4 chars for safety
    safe_key = key[-4:] if len(key) > 4 else "***"
    print(f"Found key ending in ...{safe_key}")

    headers = {"Authorization": f"Bearer {key}"}
    try:
        # Minimal request to list services or check user
        print("Testing connection to Render API...")
        r = requests.get("https://api.render.com/v1/owners", headers=headers)
        print(f"Status Code: {r.status_code}")

        if r.status_code == 200:
            print("SUCCESS: Key is valid.")
            print(f"Response: {r.text[:100]}...")
        else:
            print("FAILURE: Key returned error.")
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"Request failed: {e}")
