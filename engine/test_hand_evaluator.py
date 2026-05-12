import unittest

from engine.hand import (
    evaluate_seven_card_hand,
    determine_winners,
    replay_hand_from_seed,
    CATEGORY_STRAIGHT_FLUSH,
    CATEGORY_QUADS,
    CATEGORY_FULL_HOUSE,
    CATEGORY_FLUSH,
    CATEGORY_STRAIGHT,
    CATEGORY_TRIPS,
    CATEGORY_TWO_PAIR,
    CATEGORY_PAIR,
    CATEGORY_HIGH_CARD,
)


class TestHandEvaluator(unittest.TestCase):
    def test_category_detection(self):
        # Straight flush (9-T-J-Q-K of hearts)
        sf_cards = ['9h','Th','Jh','Qh','Kh','2d','3c']
        cat, tie = evaluate_seven_card_hand(sf_cards)
        self.assertEqual(cat, CATEGORY_STRAIGHT_FLUSH)

        # Quads (9x)
        quads = ['9h','9d','9s','9c','Kh','2d','3c']
        cat, tie = evaluate_seven_card_hand(quads)
        self.assertEqual(cat, CATEGORY_QUADS)

        # Full house
        fh = ['Kh','Kd','Ks','Qh','Qd','2s','3c']
        cat, tie = evaluate_seven_card_hand(fh)
        self.assertEqual(cat, CATEGORY_FULL_HOUSE)

        # Flush
        fl = ['2h','5h','7h','9h','Kh','3d','4s']
        cat, tie = evaluate_seven_card_hand(fl)
        self.assertEqual(cat, CATEGORY_FLUSH)

        # Straight
        st = ['9h','Th','Jd','Qc','Ks','2d','3c']
        cat, tie = evaluate_seven_card_hand(st)
        self.assertEqual(cat, CATEGORY_STRAIGHT)

        # Trips
        tr = ['9h','9d','9s','Qc','Ks','2d','3c']
        cat, tie = evaluate_seven_card_hand(tr)
        self.assertEqual(cat, CATEGORY_TRIPS)

        # Two pair
        tp = ['9h','9d','Th','Td','Ks','2d','3c']
        cat, tie = evaluate_seven_card_hand(tp)
        self.assertEqual(cat, CATEGORY_TWO_PAIR)

        # Pair
        p = ['9h','9d','Th','8d','Ks','2d','3c']
        cat, tie = evaluate_seven_card_hand(p)
        self.assertEqual(cat, CATEGORY_PAIR)

        # High card
        hc = ['2h','5d','7s','9c','Kh','3d','4s']
        cat, tie = evaluate_seven_card_hand(hc)
        self.assertEqual(cat, CATEGORY_HIGH_CARD)

    def test_deterministic_replay_and_winner(self):
        seed = 2026
        hole1, board1, winners1 = replay_hand_from_seed(seed, 6)
        hole2, board2, winners2 = replay_hand_from_seed(seed, 6)
        self.assertEqual(hole1, hole2)
        self.assertEqual(board1, board2)
        self.assertEqual(winners1, winners2)

        # Winners must be valid indices
        for w in winners1:
            self.assertTrue(0 <= w < 6)

    def test_determine_winners_tie(self):
        # Construct a tie: both players have same best five cards from board
        board = ['Ah','Kh','Qh','Jh','Th']  # royal flush on board
        hole_cards = [['2c','3d'], ['4s','5d']]
        winners = determine_winners(hole_cards, board)
        # both players share the same best hand from board -> tie
        self.assertEqual(set(winners), {0,1})


if __name__ == '__main__':
    unittest.main()
