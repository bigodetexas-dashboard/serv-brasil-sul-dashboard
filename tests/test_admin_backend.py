import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from new_dashboard.app import app
from new_dashboard.admin_routes import get_system_diagnostics


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for tests
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # Simulate Admin Login
            sess["discord_user_id"] = "test_user_123"
            sess["discord_username"] = "Admin Tester"
        yield client


def test_system_diagnostics():
    """Test if the system diagnostics gathering works"""
    with app.app_context():
        diag = get_system_diagnostics()
        print(f"\n[DIAGNOSTICS PULSE]: {diag}")
        assert "status" in diag
        assert "db_status" in diag
        assert "security_level" in diag


@patch("new_dashboard.admin_routes.query_db")
def test_check_alts(mock_query, client):
    """Test the Alt detection logic"""
    # Mock finding the target user
    mock_query.side_effect = [
        # 1. Target User Lookup
        {"gamertag": "SuspectOne", "last_ip": "1.2.3.4", "xbox_id": "XB123"},
        # 2. IP Matches
        [
            {"gamertag": "InnocentOne", "discord_id": "999"},
            {"gamertag": "SuspectAlt", "discord_id": "888"},
        ],
        # 3. Xbox Matches
        [],
    ]

    response = client.post("/admin/check_alts", json={"gamertag": "SuspectOne"})
    data = response.get_json()

    print(f"\n[ALTS CHECK RESPONSE]: {data}")
    assert response.status_code == 200
    assert data["success"] is True
    assert data["alts_count"] == 2
    assert "SuspectAlt (IP)" in data["alts"] or "InnocentOne (IP)" in data["alts"]


@patch("new_dashboard.admin_routes.ask_gemini")
def test_texano_chat(mock_ask, client):
    """Test the Texano AI chat endpoint with context injection"""
    # Mock AI response
    mock_ask.return_value = "Entendido, Xerife. O sistema está estável."

    # Payload
    payload = {"prompt": "Como está o servidor?"}

    response = client.post("/admin/texano/ask", json=payload)
    data = response.get_json()

    print(f"\n[TEXANO RESPONSE]: {data}")

    # Assertions
    assert response.status_code == 200
    assert data["success"] is True
    assert data["response"] == "Entendido, Xerife. O sistema está estável."

    # Verify Context Injection happened
    # Check if ask_gemini was called with a prompt containing our context marker
    args, _ = mock_ask.call_args
    sent_prompt = args[0]
    assert "[CONTEXTO TÉCNICO AVANÇADO]" in sent_prompt
    assert "[SUA PERSONA: TEXANO]" in sent_prompt
    print("\n[CONTEXT INJECTION VERIFIED] ✅ - Texano received system telemetry.")


if __name__ == "__main__":
    # Manually run if executed directly
    print("Running Manual Verification...")
    # Just a simple run wrapper for the functions above
    pass
