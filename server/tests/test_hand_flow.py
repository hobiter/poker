import unittest

from fastapi.testclient import TestClient

from server.app import app


class HandFlowTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_start_hand_deals_personalized_holes(self):
        payload = {
            "seat_count": 6,
            "game_type": "no-limit",
            "blinds": {"small": 5, "big": 10},
            "starting_stack": 2000,
            "name": "Deal Room",
        }
        r = self.client.post("/rooms", json=payload)
        room_id = r.json().get("roomId")

        # join two players
        r1 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Alice"})
        p1 = r1.json().get("playerId")
        r2 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Bob"})
        p2 = r2.json().get("playerId")

        # connect websockets for both players
        with self.client.websocket_connect(f"/ws/{room_id}/{p1}") as ws1:
            _ = ws1.receive_json()  # state_sync
            with self.client.websocket_connect(f"/ws/{room_id}/{p2}") as ws2:
                _ = ws2.receive_json()

                # start a hand (server will notify and send personalized hole cards)
                rsh = self.client.post(f"/rooms/{room_id}/start_hand")
                self.assertEqual(rsh.status_code, 200)

                # both sockets should receive a hand:start broadcast and personalized deal:hole
                # receive two messages each (order may vary: public then personal)
                msgs1 = [ws1.receive_json(), ws1.receive_json()]
                msgs2 = [ws2.receive_json(), ws2.receive_json()]

                # find the deal:hole message for each
                deal1 = next((m for m in msgs1 if m.get("type") == "deal:hole"), None)
                deal2 = next((m for m in msgs2 if m.get("type") == "deal:hole"), None)
                self.assertIsNotNone(deal1)
                self.assertIsNotNone(deal2)
                self.assertEqual(len(deal1.get("cards", [])), 2)
                self.assertEqual(len(deal2.get("cards", [])), 2)


if __name__ == "__main__":
    unittest.main()
