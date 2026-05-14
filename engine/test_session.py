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
        s.advance_to_next_to_act()
        s.apply_action(1, "allin")
        s.advance_to_next_to_act()
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
        while not s.is_betting_round_complete():
            idx = s.current_player_idx
            self.assertIsNotNone(idx)
            to_call = s.get_to_call(idx)
            if to_call > 0:
                s.apply_action(idx, "call")
            else:
                s.apply_action(idx, "check")
            if not s.is_betting_round_complete():
                s.advance_to_next_to_act()
        self.assertTrue(s.is_betting_round_complete())
        # deal flop and ensure round contributions reset
        s.deal_next_community()
        for p in s.players:
            self.assertEqual(p.round_contribution, 0)
        self.assertEqual(len(s.community), 3)

    def test_postflop_round_requires_each_active_player_to_act(self):
        s = Session([("p0", 100), ("p1", 100), ("p2", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=99)
        while not s.is_betting_round_complete():
            idx = s.current_player_idx
            self.assertIsNotNone(idx)
            to_call = s.get_to_call(idx)
            s.apply_action(idx, "call" if to_call > 0 else "check")
            if not s.is_betting_round_complete():
                s.advance_to_next_to_act()

        s.deal_next_community()
        first_to_act = s.current_player_idx
        s.apply_action(first_to_act, "check")

        self.assertFalse(s.is_betting_round_complete())

    def test_heads_up_dealer_posts_small_blind(self):
        s = Session([("dealer", 100), ("bb", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=7)

        self.assertEqual(s.players[0].contribution, 5)
        self.assertEqual(s.players[1].contribution, 10)
        self.assertEqual(s.current_player_idx, 0)

    def test_uncontested_hand_awards_pot(self):
        s = Session([("p0", 100), ("p1", 100)], dealer_index=0, small_blind=5, big_blind=10)
        s.start_hand(seed=7)
        s.apply_action(0, "fold")

        result = s.settle_if_hand_over()

        self.assertEqual(result["reason"], "uncontested")
        self.assertEqual(s.players[1].stack, 105)
        self.assertEqual(s.street, "finished")
        self.assertIsNone(s.current_player_idx)

    def test_showdown_awards_odd_chip_to_first_winner(self):
        s = Session([("p0", 100), ("p1", 100)], dealer_index=0, small_blind=1, big_blind=2)
        s.start_hand(seed=7)
        s.players[0].hole_cards = ["Ah", "Kd"]
        s.players[1].hole_cards = ["As", "Kc"]
        s.community = ["2h", "3d", "4c", "8s", "9h"]
        s.players[0].stack = 0
        s.players[1].stack = 0
        s.players[0].contribution = 5
        s.players[1].contribution = 4
        s.street = "showdown"

        result = s.settle_if_hand_over()

        self.assertEqual(result["reason"], "showdown")
        self.assertEqual(s.players[0].stack, 5)
        self.assertEqual(s.players[1].stack, 4)
        self.assertEqual(s.street, "finished")


if __name__ == "__main__":
    unittest.main()
