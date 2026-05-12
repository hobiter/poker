import unittest

from fastapi.testclient import TestClient

from server.app import app


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_create_and_join_room(self):
        payload = {
            "seat_count": 6,
            "game_type": "no-limit",
            "blinds": {"small": 5, "big": 10},
            "starting_stack": 2000,
            "name": "Test Room",
        }
        r = self.client.post("/rooms", json=payload)
        self.assertEqual(r.status_code, 200)
        room_id = r.json().get("roomId")
        self.assertIsNotNone(room_id)

        r2 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Alice"})
        self.assertEqual(r2.status_code, 200)
        self.assertIn("playerId", r2.json())


if __name__ == "__main__":
    unittest.main()
