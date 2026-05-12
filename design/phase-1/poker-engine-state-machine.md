# Poker Engine State Machine (Phase 1)

This document describes the server-authoritative state machine for a single hand/session. It is intended as a spec for implementation and testing.

## High-level states

- LOBBY: Waiting for host to start session or for minimum players.
- PRE_HAND: Assign dealer, collect blinds/antes, handle straddle if enabled.
- DEAL: Deal hole cards to active players.
- PREFLOP_BETTING: Preflop betting round.
- FLOP: Deal flop.
- FLOP_BETTING: Flop betting round.
- TURN: Deal turn.
- TURN_BETTING: Turn betting round.
- RIVER: Deal river.
- RIVER_BETTING: River betting round.
- SHOWDOWN: Reveal required hole cards and evaluate hands.
- HAND_END: Distribute pots, persist hand history, advance dealer/button.
- PAUSED: Game paused by host.
- ENDED: Session ended.

## Events (examples)

- `start_session` — host starts the session.
- `start_hand` — server begins hand setup when enough players present.
- `post_blind_complete` — blinds collected.
- `deal_complete` — hole cards dealt.
- `player_action` — fold/check/call/bet/raise/all-in from a player.
- `action_timeout` — player timed out (auto-action applied).
- `all_actions_complete` — betting round finished.
- `reveal_request` — showdown reveal requested.
- `hand_settled` — pots awarded and history persisted.

## Transition rules (summary)

- LOBBY -> PRE_HAND: `start_hand` and min players seated.
- PRE_HAND -> DEAL: after `post_blind_complete` and blinds validated.
- DEAL -> PREFLOP_BETTING: immediately after `deal_complete`.
- PREFLOP_BETTING -> FLOP: on `all_actions_complete` (or all but one player folded).
- FLOP -> FLOP_BETTING -> TURN -> TURN_BETTING -> RIVER -> RIVER_BETTING -> SHOWDOWN: repeated pattern.
- SHOWDOWN -> HAND_END: after evaluating hands and agreeing reveal policy.
- HAND_END -> PRE_HAND or ENDED: continue while session active; otherwise ENDED.

## Legal action validation (server responsibilities)

- Enforce minimum raise rule: a raise must be at least previous_raise_amount or big blind (depending on rules).
- Prevent illegal betting sizes (e.g., negative amounts, exceeding player's stack unless all-in).
- Maintain accurate per-player stacks and committed bets for side-pot calculation.

## Side-pot calculation (brief)

1. Track each player's total committed amount in the hand.
2. When a player is all-in, create side pots by sorting players by committed amount.
3. Each pot is awarded among eligible players who contested that pot.

## Pseudocode — processing a player action

```text
function processAction(hand, playerId, action) {
  if (!isLegal(action, hand)) return error
  applyActionToState(hand, playerId, action)
  recordHandAction(hand.id, playerId, action)
  if (isEndOfRound(hand)) {
    if (onlyOnePlayerRemaining(hand)) {
      moveToShowdownOrEnd(hand)
    } else {
      advanceToNextStreet(hand)
      if (nextStreetIsDeal) dealCommunityCards(hand)
    }
  } else {
    advanceTurnToNextPlayer(hand)
  }
}
```

## Deterministic simulation and testing

- The engine should support deterministic seeds for unit tests (mock RNG/seeded shuffle).
- Provide a replay mode that can feed recorded `hand_actions` into the engine to validate identical final states.

## Edge cases to specify in implementation tests

- Multiple all-ins with differing stack sizes.
- Odd-chip distribution when splitting pots.
- Disconnects during action and timeouts.
- Rejoining and seat reclamation during an in-progress hand.

---

This spec is intentionally concise; during implementation expand each section into detailed unit tests and API contracts.
