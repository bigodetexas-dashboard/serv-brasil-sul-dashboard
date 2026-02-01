import unittest
import os
import json
from flask import Flask
from flask_socketio import SocketIO

# Add project root to path
import sys

# Add project root and new_dashboard to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "new_dashboard"))

from new_dashboard.app import app, socketio
from repositories.events_repository import EventsRepository


class TestRealTimeEvents(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret"
        os.environ["SECRET_KEY"] = "test_secret"
        self.app = app.test_client()
        self.socket_client = socketio.test_client(app, flask_test_client=self.app)
        self.socket_client.connect()

        # Sanity Check: Can we receive a direct emit?
        socketio.emit("test_event", {"data": "test"})
        received_sanity = self.socket_client.get_received("/")
        print(f"[DEBUG] Sanity Check Received: {received_sanity}")

    def test_emit_killfeed(self):
        # 1. Simulate Bot sending a Killfeed event
        headers = {"X-Bot-Secret": "test_secret"}
        data = {
            "type": "KILLFEED",
            "content": "Player1 killed Player2",
            "related_id": 123,
        }

        response = self.app.post(
            "/api/events/emit",
            headers=headers,
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # 2. Check if SocketIO client received the message
        received = self.socket_client.get_received()
        print(f"[DEBUG] Received messages: {received}")  # DEBUG

        # We expect at least one message on 'killfeed_update' channel
        found = False
        for msg in received:
            if msg["name"] == "killfeed_update":
                found = True
                payload = msg["args"][0]
                self.assertEqual(payload["message"], "Player1 killed Player2")
                self.assertIsNotNone(payload["timestamp"])
                break

        self.assertTrue(found, "Did not receive 'killfeed_update' event")

    def test_unauthorized_emit(self):
        # Try without secret
        data = {"type": "KILLFEED", "content": "Fake News"}
        response = self.app.post(
            "/api/events/emit", data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
