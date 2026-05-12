# WebSocket Event List (Phase 1)

This file lists the realtime events and payload shapes used between clients and the server. Each event is prefixed with the direction: `C->S` (client to server) or `S->C` (server to client).

## Connection lifecycle

- C->S: `connect` — handshake/auth when a client connects (token or guest name).
- S->C: `connected` — ack with assigned `clientId` and session information.
- C->S: `reconnect_request` — request full state for a seat/player after transient disconnect.
- S->C: `state_sync` — full or partial personalized state snapshot.

## Room & lobby events

- C->S: `room:create` { settings }
- S->C: `room:created` { roomId, inviteToken }
- C->S: `room:join` { roomId | inviteToken, displayName }
- S->C: `room:joined` { roomState }
- C->S: `seat:take` { seatNumber }
- S->C: `seat:update` { seatNumber, playerSummary }
- C->S: `room:leave`
- S->C: `room:update` { publicRoomState }

## Gameplay events

- S->C: `hand:start` { handId, buttonSeat }
- S->C: `deal:hole` { handId, cards }  // personalized: only to that player
- S->C: `deal:community` { handId, street, cards }
- C->S: `action:post` { handId, actionType, amount }
- S->C: `action:posted` { handId, player, actionType, amount, newStack }
- S->C: `timer:update` { player, remainingSeconds }
- S->C: `pot:update` { total, sidePots }
- S->C: `showdown:request` { handId }
- S->C: `showdown:reveal` { handId, reveals } // only reveals allowed cards
- S->C: `hand:end` { handId, winners, payouts }

## Admin / Host events

- C->S: `admin:pause` { reason }
- S->C: `admin:paused`
- C->S: `admin:resume`
- S->C: `admin:resumed`
- C->S: `admin:kick` { seatNumber }

## Chat & social

- C->S: `chat:message` { text }
- S->C: `chat:message` { from, text, timestamp }

## Error and diagnostics

- S->C: `error` { code, message }
- S->C: `warning` { code, message }

## Notes

- `state_sync` should contain two parts: `publicView` (table, community cards, public bets, pot) and `personalView` (player hole cards, allowed actions). Server must never include other players' hole cards in `publicView`.
- All messages should include `roomId` and `sessionId` when applicable.
