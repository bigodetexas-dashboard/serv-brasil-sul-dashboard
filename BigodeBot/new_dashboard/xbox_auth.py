"""
Xbox Live authentication module for BigodeTexas Dashboard.
Handles Microsoft OAuth flow and Xbox profile retrieval.
"""

import os
import requests

# Microsoft OAuth2 settings
MS_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MS_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MS_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI", "http://localhost:5001/callback/xbox"
)

# Endpoints
MS_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MS_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
XBOX_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
XBOX_PROFILE_URL = "https://profile.xboxlive.com/users/me/profile/settings"


def get_xbox_login_url():
    """Generates the Microsoft Login URL for Xbox verification"""
    params = {
        "client_id": MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MS_REDIRECT_URI,
        "scope": "XboxLive.signin offline_access",
        "response_mode": "query",
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{MS_AUTH_URL}?{query_string}"


def authenticate_with_xbox(code):
    """
    Full flow to exchange MS code for Xbox Gamertag
    1. MS Token
    2. Xbox Live Token
    3. XSTS Token
    4. Profile
    """
    try:
        # 1. MS Token
        token_data = {
            "client_id": MS_CLIENT_ID,
            "client_secret": MS_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": MS_REDIRECT_URI,
        }
        res = requests.post(MS_TOKEN_URL, data=token_data, timeout=10)
        res.raise_for_status()
        ms_token = res.json()["access_token"]

        # 2. Xbox Live Token
        xbox_auth_data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }
        res = requests.post(XBOX_AUTH_URL, json=xbox_auth_data, timeout=10)
        res.raise_for_status()
        xbox_data = res.json()
        xbox_token = xbox_data["Token"]
        user_hash = xbox_data["DisplayClaims"]["xui"][0]["uhs"]

        # 3. XSTS Token
        xsts_data = {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]},
            "RelyingParty": "http://xboxlive.com",
            "TokenType": "JWT",
        }
        res = requests.post(XSTS_AUTH_URL, json=xsts_data, timeout=10)
        res.raise_for_status()
        xsts_token = res.json()["Token"]

        # 4. Get Gamertag
        headers = {
            "x-xbl-contract-version": "2",
            "Authorization": f"XBL3.0 x={user_hash};{xsts_token}",
            "Accept": "application/json",
        }
        # Get profile with Gamertag
        res = requests.get(
            f"{XBOX_PROFILE_URL}?settings=Gamertag", headers=headers, timeout=10
        )
        res.raise_for_status()
        profile_data = res.json()

        gamertag = None
        if "profileUsers" in profile_data and len(profile_data["profileUsers"]) > 0:
            settings = profile_data["profileUsers"][0].get("settings", [])
            for s in settings:
                if s["id"] == "Gamertag":
                    gamertag = s["value"]
                    break

        return {
            "success": True,
            "gamertag": gamertag,
            "xuid": profile_data["profileUsers"][0]["id"]
            if "profileUsers" in profile_data
            else None,
        }

    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"[XBOX_AUTH_ERROR] {e}")
        return {"success": False, "error": str(e)}
