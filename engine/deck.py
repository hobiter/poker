"""Deterministic/shuffleable deck implementation used for engine unit tests."""
import random
from typing import List, Optional

RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
SUITS = ['h','d','c','s']

def make_deck() -> List[str]:
    return [r + s for r in RANKS for s in SUITS]

class Deck:
    """Simple deck with deterministic shuffle support via seed."""
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.cards: List[str] = make_deck()

    def shuffle(self, seed: Optional[int] = None) -> Optional[int]:
        """Shuffle the deck deterministically when `seed` is provided.

        Returns the seed used (or None if not seeded).
        """
        if seed is not None:
            self.seed = seed
            self.rng = random.Random(seed)
        else:
            # non-deterministic shuffle
            self.seed = None
            self.rng = random.Random()
        self.cards = make_deck()
        # Use the RNG's shuffle for deterministic behavior when seeded
        self.rng.shuffle(self.cards)
        return self.seed

    def draw(self, n: int = 1) -> List[str]:
        """Draw `n` cards from the top of the deck (index 0)."""
        if n < 1:
            return []
        if n > len(self.cards):
            raise IndexError("Not enough cards to draw")
        result = self.cards[:n]
        self.cards = self.cards[n:]
        return result

    def deal_hole_cards(self, num_players: int, cards_per_player: int = 2) -> List[List[str]]:
        """Deal hole cards round-robin to players (standard dealing)."""
        if num_players * cards_per_player > len(self.cards):
            raise ValueError("Not enough cards to deal")
        hands: List[List[str]] = [[] for _ in range(num_players)]
        for _ in range(cards_per_player):
            for p in range(num_players):
                hands[p].append(self.draw(1)[0])
        return hands

    def __len__(self) -> int:
        return len(self.cards)

    def __repr__(self) -> str:
        return f"<Deck cards={len(self.cards)} seed={self.seed}>"
