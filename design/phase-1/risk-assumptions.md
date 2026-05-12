# Risks, Assumptions, and Acceptance Tests (Phase 1)

## Assumptions

- MVP is play-money only; no real-money settlement or KYC required.
- Server is authoritative for deck, actions, and outcomes.
- Tech stack: Node/TS backend (API/WebSocket), Postgres for persistence, Redis for ephemeral room state (implementation-agnostic at design stage).
- Private rooms by default; invite tokens provide access control.

## Key Risks and Mitigations

- Real-time correctness risk: bugs in side-pot or all-in handling.
  - Mitigation: exhaustive unit tests with deterministic seeds and recorded action replays; implement replay tests.
- Cheating and information leaks (accidental broadcast of hole cards).
  - Mitigation: personalized state model, strict server-side filters, integration tests that assert no hole-cards appear in public views.
- Scale and performance with many concurrent rooms.
  - Mitigation: design Redis-based room state, stateless app servers, and per-room shard strategy; load-test in Phase 2/3.
- Legal/regulatory risk if payments are introduced.
  - Mitigation: keep MVP play-money only; require business/legal review before any payment feature.

## Acceptance Tests (actionable, automated where possible)

1. Room creation flow
   - Steps: host creates room with `seatCount=6`, `blinds=5/10`, starting stack 2000 -> returns `roomId` and invite token.
   - Pass: invite allows 1+ guests to join and take seats; server persists room config.

2. Full hand lifecycle (single hand)
   - Steps: two players seated, host starts; server posts blinds, deals hole cards (personalized), accepts actions through to showdown.
   - Pass: pot calculation, side-pot logic, winner payout recorded in `hands` and `player_hands`; hand history contains full action log.

3. Seeded shuffle replay determinism
   - Steps: run `replay_hand_from_seed(seed, n)` twice.
   - Pass: identical hole and board cards and winner determination.

4. Side-pot and multiple all-ins
   - Steps: create scenario with 3 players where two go all-in for different amounts; continue to showdown.
   - Pass: side-pot ownership and payouts match expected manual calculation; odd-chip distribution deterministic.

5. Disconnect/reconnect
   - Steps: mid-hand disconnect of player A; player reconnects using `reconnect_request` and reclaims seat.
   - Pass: game state synchronized, player's hole cards restored in personal view, no state corruption.

6. Privacy test
   - Steps: request a `state_sync` for spectator or other player while a hand is live.
   - Pass: spectator/public view contains no opponents' hole cards; only the owner receives `deal:hole`.

7. Export hand history
   - Steps: complete several hands, request JSON/CSV export.
   - Pass: export contains full action log per hand, player stacks before/after, pot/side-pot detail.

8. WebSocket event contract
   - Steps: run integration test that subscribes to gameplay events and sends valid `action:post` messages.
   - Pass: server validates action legality, rejects illegal actions with `error` events, and broadcasts `action:posted` to room.

## Next verification tasks

- Turn acceptance tests into automated integration tests (use headless client mocks and seeded engine runs).
- Add explicit test cases for edge cases (wheel straights, split pots, run-it-twice behavior when implemented).
