import unittest

from engine.session import Session


class SessionTests(unittest.TestCase):
    def test_post_blinds_and_turn(self):
        s = Session([("p0", 100), ("p1", 100), ("p2", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=42)
        self.assertEqual(s.players[1].contribution, 5)
        self.assertEqual(s.players[1].stack, 95)
        self.assertEqual(s.players[2].contribution, 10)
        self.assertEqual(s.players[2].stack, 90)
        self.assertEqual(s.get_highest_contribution(), 10)
        big_idx = (s.dealer_index + 2) % s.player_count
        expected_current = (big_idx + 1) % s.player_count
        self.assertEqual(s.current_player_idx, expected_current)

    def test_compute_pots_allin(self):
        s = Session([("p0", 100), ("p1", 15), ("p2", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=123)
        # preflop actions: p0 calls, p1 goes all-in for remaining stack, p2 calls
        s.apply_action(0, "call")
        s.apply_action(1, "allin")
        s.apply_action(2, "call")
        pots = s.compute_pots()
        amounts = [p["amount"] for p in pots]
        self.assertEqual(amounts, [30, 10])
        parts = [set(p["participants"]) for p in pots]
        self.assertEqual(parts[0], {0, 1, 2})
        self.assertEqual(parts[1], {1, 2})

    def test_turn_advances_after_action(self):
        s = Session([("p0", 100), ("p1", 100), ("p2", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=42)
        cur = s.current_player_idx
        # current player folds
        s.apply_action(cur, "fold")
        s.advance_turn()
        # next active should be the following seat
        expected = (cur + 1) % s.player_count
        # if expected is folded or busted we'd loop; for this setup expected is active
        self.assertEqual(s.current_player_idx, expected)

    def test_round_reset_on_deal_next_community(self):
        s = Session([("p0", 100), ("p1", 100), ("p2", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=99)
        # simulate everyone calling to finish preflop
        for i in range(s.player_count):
            if s.players[i].status == "active":
                # call whatever is needed
                to_call = s.get_to_call(i)
                if to_call > 0:
                    s.apply_action(i, "call")
        self.assertTrue(s.is_betting_round_complete())
        # deal flop and ensure round contributions reset
        s.deal_next_community()
        for p in s.players:
            self.assertEqual(p.round_contribution, 0)
        self.assertEqual(len(s.community), 3)


if __name__ == "__main__":
    unittest.main()
