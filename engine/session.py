"""Session lifecycle primitives for Texas Hold'em.

This module provides a lightweight `Session` and `PlayerState` used for
managing blinds, simple action validation (fold/call/all-in/check), betting
round completion detection, and pot / side-pot calculation. It's intentionally
minimal to serve as the basis for the next Phase 2 implementation steps.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import uuid
import time

from .deck import Deck
from .hand import determine_winners


STREETS = ("preflop", "flop", "turn", "river", "showdown", "finished")


@dataclass
class PlayerState:
    id: str
    seat: int
    stack: int
    contribution: int = 0
    round_contribution: int = 0
    has_acted: bool = False
    status: str = "active"  # active, folded, allin, busted
    hole_cards: Optional[List[str]] = None

    def __repr__(self) -> str:  # pragma: no cover - small helper
        return f"<Player id={self.id} seat={self.seat} stack={self.stack} contrib={self.contribution} status={self.status}>"


class Session:
    def __init__(self, players: List[Tuple[str, int]], dealer_index: int = 0, small_blind: int = 5, big_blind: int = 10):
        if not players:
            raise ValueError("At least one player required")
        self.players: List[PlayerState] = [PlayerState(id=p[0], seat=i, stack=p[1]) for i, p in enumerate(players)]
        self.dealer_index = dealer_index % len(self.players)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck: Optional[Deck] = None
        self.community: List[str] = []
        self.street: Optional[str] = None
        self.hand_id: Optional[str] = None
        self.current_player_idx: Optional[int] = None
        self.turn_timeout_seconds: int = 30
        self.turn_started_at: Optional[float] = None

    @property
    def player_count(self) -> int:
        return len(self.players)

    def start_hand(self, seed: Optional[int] = None) -> None:
        """Prepare a new hand: shuffle, deal hole cards, post blinds, set first actor."""
        self.deck = Deck()
        self.deck.shuffle(seed)
        hole_cards = self.deck.deal_hole_cards(self.player_count, 2)
        for i, p in enumerate(self.players):
            p.hole_cards = hole_cards[i]
            p.contribution = 0
            p.round_contribution = 0
            p.has_acted = False
            if p.stack <= 0:
                p.status = "busted"
            else:
                p.status = "active"

        self.community = []
        self.street = "preflop"
        self.hand_id = str(seed) if seed is not None else str(uuid.uuid4())

        # Post blinds and set current player to the seat after the big blind
        _, big_idx = self._post_blinds()
        self.current_player_idx = (big_idx + 1) % self.player_count
        self.start_turn_timer()

    def _blind_indices(self) -> Tuple[int, int]:
        n = self.player_count
        if n == 2:
            return self.dealer_index, (self.dealer_index + 1) % n
        return (self.dealer_index + 1) % n, (self.dealer_index + 2) % n

    def _post_blinds(self) -> Tuple[int, int]:
        small_idx, big_idx = self._blind_indices()
        self._post(small_idx, self.small_blind)
        self._post(big_idx, self.big_blind)
        return small_idx, big_idx

    def _post(self, idx: int, amount: int) -> None:
        p = self.players[idx]
        pay = min(amount, p.stack)
        p.stack -= pay
        p.contribution += pay
        p.round_contribution += pay
        if p.stack == 0:
            p.status = "allin"

    def get_highest_contribution(self) -> int:
        return max((p.contribution for p in self.players), default=0)

    def get_round_highest(self) -> int:
        return max((p.round_contribution for p in self.players), default=0)

    def get_to_call(self, idx: int) -> int:
        highest = self.get_round_highest()
        return max(0, highest - self.players[idx].round_contribution)

    def legal_actions(self, idx: int) -> List[Dict]:
        p = self.players[idx]
        if p.status != "active" or idx != self.current_player_idx:
            return []
        to_call = self.get_to_call(idx)
        actions: List[Dict] = []
        if to_call == 0:
            actions.append({"action": "check"})
            if p.stack > 0:
                actions.append({"action": "bet", "min": 1, "max": p.stack})
                actions.append({"action": "allin", "amount": p.stack})
        else:
            call_amount = min(to_call, p.stack)
            actions.append({"action": "fold"})
            actions.append({"action": "call", "amount": call_amount})
            if p.stack > call_amount:
                min_raise_total = self.get_round_highest() + self.big_blind
                actions.append({"action": "raise", "min": min_raise_total, "max": p.round_contribution + p.stack})
            else:
                actions.append({"action": "allin", "amount": p.stack})
        return actions

    def validate_action(self, idx: int, action: str, amount: Optional[int] = None) -> None:
        actions = self.legal_actions(idx)
        allowed = {a["action"]: a for a in actions}
        if action not in allowed:
            raise ValueError("Action not allowed")

        spec = allowed[action]
        if action in {"bet", "raise"}:
            if amount is None:
                raise ValueError("Bet/raise requires an amount")
            minimum = spec.get("min", 0)
            maximum = spec.get("max", 0)
            if amount < minimum or amount > maximum:
                raise ValueError(f"{action} amount must be between {minimum} and {maximum}")

    def apply_action(self, idx: int, action: str, amount: Optional[int] = None) -> None:
        self.validate_action(idx, action, amount)
        p = self.players[idx]
        if p.status != "active":
            raise ValueError("Player cannot act: not active")
        if action == "fold":
            p.status = "folded"
            p.has_acted = True
            return

        if action == "check":
            if self.get_to_call(idx) != 0:
                raise ValueError("Cannot check when there's an outstanding bet")
            p.has_acted = True
            return

        if action == "call":
            to_call = self.get_to_call(idx)
            pay = min(to_call, p.stack)
            p.stack -= pay
            p.contribution += pay
            p.round_contribution += pay
            if p.stack == 0:
                p.status = "allin"
            p.has_acted = True
            return

        if action == "allin":
            previous_highest = self.get_round_highest()
            pay = p.stack
            p.stack = 0
            p.contribution += pay
            p.round_contribution += pay
            p.status = "allin"
            p.has_acted = True
            if p.round_contribution > previous_highest:
                self._reset_other_active_actors(idx)
            # if this changes the round-highest, caller of apply_action should handle
            return

        if action == "bet" or action == "raise":
            if amount is None or amount <= 0:
                raise ValueError("Bet/raise requires positive amount")
            target_total = amount
            pay = min(target_total - p.round_contribution, p.stack)
            p.stack -= pay
            p.contribution += pay
            p.round_contribution += pay
            if p.stack == 0:
                p.status = "allin"
            p.has_acted = True
            self._reset_other_active_actors(idx)
            return

        raise ValueError(f"Unknown action: {action}")

    def _reset_other_active_actors(self, actor_idx: int) -> None:
        for i, player in enumerate(self.players):
            if i != actor_idx and player.status == "active":
                player.has_acted = False

    def is_betting_round_complete(self) -> bool:
        # round-highest determines required matching for this betting round
        highest = self.get_round_highest()
        active_players = [p for p in self.players if p.status != "folded"]
        if len(active_players) <= 1:
            return True
        for p in active_players:
            if p.status == "allin":
                continue
            if not p.has_acted:
                return False
            if p.round_contribution != highest:
                return False
        return True

    def deal_next_community(self) -> None:
        if not self.deck:
            raise RuntimeError("Deck not initialized")
        if self.street == "preflop":
            self.community.extend(self.deck.draw(3))
            self.street = "flop"
        elif self.street == "flop":
            self.community.extend(self.deck.draw(1))
            self.street = "turn"
        elif self.street == "turn":
            self.community.extend(self.deck.draw(1))
            self.street = "river"
        elif self.street == "river":
            self.street = "showdown"
        # reset per-round contributions for next betting round
        for p in self.players:
            p.round_contribution = 0
            p.has_acted = False
        # set current player to left of dealer for postflop
        self.current_player_idx = self._next_active_index(self.dealer_index)

    def compute_pots(self) -> List[Dict]:
        """Compute main pot and side pots.

        Returns list of pots in creation order: [{amount: int, participants: [seat_indices]}]
        """
        contributions: Dict[int, int] = {i: p.contribution for i, p in enumerate(self.players) if p.contribution > 0}
        pots: List[Dict] = []
        while contributions:
            nonzero = {i: c for i, c in contributions.items() if c > 0}
            if not nonzero:
                break
            min_c = min(nonzero.values())
            participants = list(nonzero.keys())
            pot_amount = min_c * len(participants)
            pots.append({"amount": pot_amount, "participants": participants})
            # subtract min_c
            for i in participants:
                contributions[i] -= min_c
            contributions = {i: c for i, c in contributions.items() if c > 0}
        return pots

    def settle_if_hand_over(self) -> Optional[Dict]:
        """Award chips when the hand has ended.

        Returns a summary dict when the hand is finished, otherwise None.
        """
        if self.street == "finished":
            return None

        contenders = [i for i, p in enumerate(self.players) if p.status != "folded"]
        if len(contenders) == 1:
            winner = contenders[0]
            amount = sum(p.contribution for p in self.players)
            self.players[winner].stack += amount
            self.street = "finished"
            self.current_player_idx = None
            result = {
                "type": "hand:finished",
                "reason": "uncontested",
                "awards": [{"playerId": self.players[winner].id, "amount": amount}],
            }
            self._clear_contributions()
            return result

        if self.street != "showdown":
            return None

        awards: List[Dict] = []
        for pot in self.compute_pots():
            participants = [i for i in pot["participants"] if self.players[i].status != "folded"]
            hole_cards_list = [self.players[i].hole_cards for i in participants]
            winners_local = determine_winners(hole_cards_list, self.community)
            winners = [participants[i] for i in winners_local]
            share = pot["amount"] // len(winners)
            remainder = pot["amount"] % len(winners)
            for offset, winner in enumerate(winners):
                award = share + (remainder if offset == 0 else 0)
                self.players[winner].stack += award
                awards.append({"playerId": self.players[winner].id, "amount": award})

        self.street = "finished"
        self.current_player_idx = None
        result = {
            "type": "hand:finished",
            "reason": "showdown",
            "awards": awards,
            "community": self.community,
        }
        self._clear_contributions()
        return result

    def _clear_contributions(self) -> None:
        for player in self.players:
            player.contribution = 0
            player.round_contribution = 0

    def showdown(self) -> List[Tuple[List[int], int]]:
        """Run showdown and return list of (winner_seat_indices, awarded_amount) per pot.

        NOTE: simple integer split used for ties; remainder goes to the first winner.
        """
        pots = self.compute_pots()
        results: List[Tuple[List[int], int]] = []
        for pot in pots:
            participants = [i for i in pot["participants"] if self.players[i].status != "folded"]
            if not participants:
                # nobody eligible (shouldn't happen) — skip
                results.append(([], pot["amount"]))
                continue
            # build hole list in participant order
            hole_cards_list = [self.players[i].hole_cards for i in participants]
            winners_local = determine_winners(hole_cards_list, self.community)
            # map local indices back to seat indices
            winners = [participants[i] for i in winners_local]
            share = pot["amount"] // len(winners)
            # award shares (not mutating stacks here, just return results)
            results.append((winners, share))
        return results

    def _next_active_index(self, from_idx: int) -> Optional[int]:
        n = len(self.players)
        for step in range(1, n + 1):
            i = (from_idx + step) % n
            p = self.players[i]
            if p.status == "active":
                return i
        return None

    def advance_turn(self) -> None:
        """Advance `current_player_idx` to the next active player, or None if none."""
        if self.current_player_idx is None:
            return
        nxt = self._next_active_index(self.current_player_idx)
        self.current_player_idx = nxt

    def _next_to_act_index(self, from_idx: int) -> Optional[int]:
        """Return next index who still needs to act this round (round_contribution < round_highest)."""
        n = len(self.players)
        highest = self.get_round_highest()
        for step in range(1, n + 1):
            i = (from_idx + step) % n
            p = self.players[i]
            if p.status != "active":
                continue
            if (not p.has_acted or p.round_contribution < highest) and p.stack > 0:
                return i
        return None

    def advance_to_next_to_act(self) -> None:
        """Advance `current_player_idx` to the next player who still needs to act this round."""
        if self.current_player_idx is None:
            return
        nxt = self._next_to_act_index(self.current_player_idx)
        self.current_player_idx = nxt

    def start_turn_timer(self, timeout_seconds: Optional[int] = None) -> None:
        self.turn_started_at = time.time()
        if timeout_seconds is not None:
            self.turn_timeout_seconds = timeout_seconds

    def time_remaining(self) -> Optional[float]:
        if self.turn_started_at is None:
            return None
        elapsed = time.time() - self.turn_started_at
        return max(0.0, self.turn_timeout_seconds - elapsed)

    def force_timeout(self) -> Optional[str]:
        """Force the current player to timeout (auto-fold). Returns folded player id or None."""
        if self.current_player_idx is None:
            return None
        idx = self.current_player_idx
        p = self.players[idx]
        if p.status != "active":
            return None
        p.status = "folded"
        p.has_acted = True
        folded_id = p.id
        # advance to next to act
        self.advance_to_next_to_act()
        self.start_turn_timer()
        return folded_id
