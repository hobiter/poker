import unittest

from fastapi.testclient import TestClient

from server.app import app


class WSTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ws_connect_and_sync_and_broadcast(self):
        payload = {
            "seat_count": 6,
            "game_type": "no-limit",
            "blinds": {"small": 5, "big": 10},
            "starting_stack": 2000,
            "name": "WS Room",
        }
        r = self.client.post("/rooms", json=payload)
        room_id = r.json().get("roomId")

        with self.client.websocket_connect(f"/ws/{room_id}/client1") as ws:
            data = ws.receive_json()
            self.assertEqual(data["type"], "state_sync")
            self.assertIn("publicView", data)
            self.assertIn("personalView", data)

            # send an action, expect broadcast back
            ws.send_json({"type": "action:post", "payload": {"action": "ping"}})
            msg = ws.receive_json()
            self.assertEqual(msg["type"], "action:posted")
            self.assertEqual(msg["from"], "client1")


if __name__ == "__main__":
    unittest.main()
