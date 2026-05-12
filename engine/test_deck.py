import unittest

from engine.deck import Deck


class TestDeck(unittest.TestCase):
    def test_same_seed_reproducible(self):
        seed = 42
        d1 = Deck()
        d1.shuffle(seed)
        order1 = d1.cards.copy()

        d2 = Deck()
        d2.shuffle(seed)
        order2 = d2.cards.copy()

        self.assertEqual(order1, order2)

    def test_different_seeds_differ(self):
        d1 = Deck(); d1.shuffle(1); order1 = d1.cards.copy()
        d2 = Deck(); d2.shuffle(2); order2 = d2.cards.copy()
        # Extremely unlikely to collide; for test purposes they should differ
        self.assertNotEqual(order1, order2)

    def test_deal_unique_cards_and_count(self):
        d = Deck(); d.shuffle(7)
        hands = d.deal_hole_cards(5, 2)
        all_cards = [c for hand in hands for c in hand]
        self.assertEqual(len(all_cards), 10)
        self.assertEqual(len(set(all_cards)), 10)
        self.assertEqual(len(d.cards), 52 - 10)

    def test_replay_deal_with_seed(self):
        seed = 99
        d1 = Deck(); d1.shuffle(seed); hands1 = d1.deal_hole_cards(6, 2)
        d2 = Deck(); d2.shuffle(seed); hands2 = d2.deal_hole_cards(6, 2)
        self.assertEqual(hands1, hands2)


if __name__ == "__main__":
    unittest.main()
