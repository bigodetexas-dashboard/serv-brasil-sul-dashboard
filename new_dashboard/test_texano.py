import requests
import re
import json

# Use a session to persist cookies
s = requests.Session()

# 1. Login via Dev Bypass (Redirects to Admin Panel)
login_url = "http://127.0.0.1:5001/dev_login"
print(f"Logging in via {login_url}...")
try:
    r = s.get(login_url)
    print(f"Login Status: {r.status_code}")
    print(f"Final URL: {r.url}")

    # 2. Extract CSRF Token from the page using Regex
    # Look for <meta name="csrf-token" content="...">
    match = re.search(r'<meta name="csrf-token" content="([^"]+)">', r.text)
    if match:
        token = match.group(1)
        print(f"CSRF Token Found: {token}")
    else:
        print("CSRF Token NOT FOUND on page!")
        token = None

    # 3. Ask Texano
    url = "http://127.0.0.1:5001/api/admin/texano/ask"
    payload = {"prompt": "Ola Texano, status do sistema?"}
    headers = {}
    if token:
        headers["X-CSRFToken"] = token

    print(f"Asking Texano: {url}...")
    r = s.post(url, json=payload, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")
