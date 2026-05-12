"""Hand evaluation and deterministic replay helpers for Texas Hold'em.

Provides:
- `evaluate_seven_card_hand(cards)` -> (category, tiebreaker_tuple)
- `determine_winners(hole_cards_list, board_cards)` -> list of winner indices
- `replay_hand_from_seed(seed, num_players)` -> (hole_cards_list, board, winners)
"""
from collections import Counter, defaultdict
from typing import List, Tuple, Optional

from .deck import Deck

# Category ranking: higher is better
CATEGORY_HIGH_CARD = 0
CATEGORY_PAIR = 1
CATEGORY_TWO_PAIR = 2
CATEGORY_TRIPS = 3
CATEGORY_STRAIGHT = 4
CATEGORY_FLUSH = 5
CATEGORY_FULL_HOUSE = 6
CATEGORY_QUADS = 7
CATEGORY_STRAIGHT_FLUSH = 8

RANK_CHAR_TO_VALUE = {r: i for i, r in enumerate(['2','3','4','5','6','7','8','9','T','J','Q','K','A'], start=2)}


def card_rank(card: str) -> int:
    return RANK_CHAR_TO_VALUE[card[0]]


def card_suit(card: str) -> str:
    return card[1]


def _find_straight_top(ranks_set: set) -> Optional[int]:
    """Return the top rank of the highest straight in ranks_set, or None.

    Handles wheel (A-2-3-4-5) by treating Ace as rank 1 when appropriate.
    """
    if not ranks_set:
        return None
    s = set(ranks_set)
    if 14 in s:
        s.add(1)
    for top in range(14, 4, -1):
        if all((top - off) in s for off in range(5)):
            return 5 if top == 5 and 1 in s else top
    return None


def evaluate_seven_card_hand(cards: List[str]) -> Tuple[int, Tuple[int, ...]]:
    """Evaluate 5-7 cards and return a comparable ranking tuple.

    Returns (category, tiebreaker_tuple) where higher tuples are better.
    """
    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate")

    ranks = [card_rank(c) for c in cards]
    suits = [card_suit(c) for c in cards]
    rank_counts = Counter(ranks)
    # group cards by suit
    suits_map = defaultdict(list)
    for c in cards:
        suits_map[card_suit(c)].append(card_rank(c))

    # Straight flush
    for s, ranks_in_suit in suits_map.items():
        if len(set(ranks_in_suit)) >= 5:
            top_sf = _find_straight_top(set(ranks_in_suit))
            if top_sf:
                return (CATEGORY_STRAIGHT_FLUSH, (top_sf,))

    # Quads
    quads = [r for r, cnt in rank_counts.items() if cnt == 4]
    if quads:
        q = max(quads)
        kicker = max([r for r in ranks if r != q])
        return (CATEGORY_QUADS, (q, kicker))

    # Full house
    trips = sorted([r for r, cnt in rank_counts.items() if cnt >= 3], reverse=True)
    pairs = sorted([r for r, cnt in rank_counts.items() if cnt >= 2], reverse=True)
    if trips:
        top_trip = trips[0]
        # choose best possible pair/trip as second component
        remaining_pairs = [r for r in pairs if r != top_trip]
        if remaining_pairs:
            return (CATEGORY_FULL_HOUSE, (top_trip, remaining_pairs[0]))

    # Flush
    for s, ranks_in_suit in suits_map.items():
        if len(set(ranks_in_suit)) >= 5:
            top_flush = tuple(sorted(set(ranks_in_suit), reverse=True)[:5])
            return (CATEGORY_FLUSH, top_flush)

    # Straight
    straight_top = _find_straight_top(set(ranks))
    if straight_top:
        return (CATEGORY_STRAIGHT, (straight_top,))

    # Trips
    if trips:
        top_trip = trips[0]
        kickers = sorted([r for r in ranks if r != top_trip], reverse=True)[:2]
        return (CATEGORY_TRIPS, (top_trip, *kickers))

    # Two pair
    if len(pairs) >= 2:
        top_pair, second_pair = pairs[0], pairs[1]
        kicker = max([r for r in ranks if r != top_pair and r != second_pair])
        return (CATEGORY_TWO_PAIR, (top_pair, second_pair, kicker))

    # Pair
    if pairs:
        pair_rank = pairs[0]
        kickers = sorted([r for r in ranks if r != pair_rank], reverse=True)[:3]
        return (CATEGORY_PAIR, (pair_rank, *kickers))

    # High card
    top_cards = tuple(sorted(set(ranks), reverse=True)[:5])
    return (CATEGORY_HIGH_CARD, top_cards)


def determine_winners(hole_cards_list: List[List[str]], board_cards: List[str]) -> List[int]:
    """Given list of players' hole cards and board, return winner indices (can be multiple ties)."""
    scores = []
    for hole in hole_cards_list:
        full = hole + board_cards
        score = evaluate_seven_card_hand(full)
        scores.append(score)
    # find max score
    best = None
    winners: List[int] = []
    for i, s in enumerate(scores):
        if best is None or s > best:
            best = s
            winners = [i]
        elif s == best:
            winners.append(i)
    return winners


def replay_hand_from_seed(seed: int, num_players: int) -> Tuple[List[List[str]], List[str], List[int]]:
    """Deterministically deal a hand from `seed` and return hole cards, board, and winners."""
    d = Deck()
    d.shuffle(seed)
    hole_cards = d.deal_hole_cards(num_players, 2)
    board = d.draw(3) + d.draw(1) + d.draw(1)
    winners = determine_winners(hole_cards, board)
    return hole_cards, board, winners
