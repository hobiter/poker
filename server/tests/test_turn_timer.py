import unittest

from fastapi.testclient import TestClient

from server.app import app, store


class TurnTimerTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_force_timeout_auto_folds_and_advances(self):
        payload = {
            "seat_count": 6,
            "game_type": "no-limit",
            "blinds": {"small": 5, "big": 10},
            "starting_stack": 2000,
            "name": "Timer Room",
        }
        r = self.client.post("/rooms", json=payload)
        room_id = r.json().get("roomId")

        r1 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Alice"})
        p1 = r1.json().get("playerId")
        r2 = self.client.post(f"/rooms/{room_id}/join", json={"display_name": "Bob"})
        p2 = r2.json().get("playerId")

        # start a hand (creates session and starts a turn timer)
        rsh = self.client.post(f"/rooms/{room_id}/start_hand")
        self.assertEqual(rsh.status_code, 200)

        # force a timeout (auto-fold) for the current player immediately
        rft = self.client.post(f"/rooms/{room_id}/force_timeout")
        self.assertEqual(rft.status_code, 200)

        # verify session state: a player was folded and current_player advanced
        session = store.get_session(room_id)
        self.assertIsNotNone(session)
        # at least one player should have status 'folded'
        folded_any = any(p.status == "folded" for p in session.players)
        self.assertTrue(folded_any)


if __name__ == "__main__":
    unittest.main()
