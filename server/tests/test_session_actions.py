import unittest

from fastapi.testclient import TestClient

from server.app import app


class SessionActionTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_post_valid_action_and_broadcast(self):
        payload = {
            "seat_count": 6,
            "game_type": "no-limit",
            "blinds": {"small": 5, "big": 10},
            "starting_stack": 2000,
            "name": "Action Room",
        }
        r = self.client.post("/rooms", json=payload)
        room_id = r.json().get("roomId")

        r1 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Alice"})
        p1 = r1.json().get("playerId")
        r2 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Bob"})
        p2 = r2.json().get("playerId")

        with self.client.websocket_connect(f"/ws/{room_id}/{p1}") as ws1:
            _ = ws1.receive_json()
            with self.client.websocket_connect(f"/ws/{room_id}/{p2}") as ws2:
                _ = ws2.receive_json()

                # start a hand (creates session)
                rsh = self.client.post(f"/rooms/{room_id}/start_hand")
                self.assertEqual(rsh.status_code, 200)

                # drain initial messages
                _ = ws1.receive_json()
                _ = ws1.receive_json()
                _ = ws2.receive_json()
                _ = ws2.receive_json()

                # with two players, the small blind (p2) acts first in our session logic
                ws2.send_json({"type": "action:post", "payload": {"actionType": "call"}})

                m1 = ws1.receive_json()
                m2 = ws2.receive_json()
                posted = None
                for m in (m1, m2):
                    if m.get("type") == "action:posted":
                        posted = m
                        break

                self.assertIsNotNone(posted)
                self.assertEqual(posted.get("from"), p2)


if __name__ == "__main__":
    unittest.main()
