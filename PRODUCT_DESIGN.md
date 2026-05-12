# Product Design Draft: Online Texas Hold’em Poker Website

## Goal

Build a private-room online Texas Hold’em poker platform where users can create invite-only games, configure rules deeply, play in real time, and review detailed player/session analytics such as chip movement, win/loss, VPIP, PFR, aggression, showdown stats, and hand histories.

The product should support casual home games first, but be designed with enough flexibility to support more advanced PokerGG-style configurations later.

---

## 1. Core User Roles

### 1.1 Guest Player

A player who joins through an invitation link.

**Capabilities:**

- Join a room by link.
- Enter display name.
- Select seat if allowed.
- Buy in or receive starting chips.
- Play hands.
- View own stats and session summary.
- Leave room.

### 1.2 Registered Player

Optional account-based player.

**Capabilities:**

- Persistent username/profile.
- Historical stats across sessions.
- Saved player preferences.
- Avatar.
- Rejoin previous games.
- Track long-term performance.

### 1.3 Room Host / Admin

The user who creates the poker room.

**Capabilities:**

- Create room.
- Choose max seats: 6, 9, or 12 players.
- Configure game settings.
- Generate invitation link.
- Approve or reject players.
- Pause/resume game.
- Adjust chips if enabled.
- Kick players.
- End session.
- Export hand history and statistics.

### 1.4 Observer / Spectator

Optional role.

**Capabilities:**

- Watch a game without playing.
- Cannot see hole cards.
- May or may not see player stats depending on room settings.
- Could be disabled for private games.

---

## 2. Room Creation and Invitation System

### 2.1 Create Room Flow

The host clicks **Create Room** and chooses:

**Game type:**

- Texas Hold’em No-Limit.
- Texas Hold’em Pot-Limit.
- Texas Hold’em Fixed-Limit, optional future feature.

**Player capacity:**

- 6-max.
- 9-max.
- 12-max.

**Room visibility:**

- Private invite-only.
- Public lobby, optional future feature.
- Password-protected.

**Buy-in structure:**

- Fixed starting stack.
- Min/max buy-in.
- Host-controlled chip allocation.
- Rebuy allowed or not.

**Blind structure:**

- Fixed blinds.
- Timed blind increases.
- Hand-count-based increases.
- Ante enabled or disabled.

**Advanced settings:**

- Run it twice.
- Straddle.
- Bomb pot.
- All-in insurance, optional later.
- Rabbit hunting, optional.
- Time bank.
- Disconnection rules.

After creation, the system generates:

- Room ID.
- Invitation URL.
- Optional password.
- Optional QR code.
- Admin control panel.

**Example invitation link format** (design-level only, not implementation):

```text
https://example.com/room/abc123?invite=secure-token
```

### 2.2 Invitation Link Design

The invitation link should include a secure, non-guessable token.

**Recommended behavior:**

- Link can be copied by host.
- Link can expire after a configurable period.
- Host can revoke and regenerate link.
- Host can limit link usage by number of joins.
- Link can optionally require host approval before seating.
- Players who disconnect can rejoin using the same link or account.

**Security considerations:**

- Do not expose internal room IDs as the only access control.
- Use random invite tokens.
- Allow password or approval mode for sensitive private games.
- Prevent duplicate joining from same account/device unless allowed.

---

## 3. Poker Table Experience

### 3.1 Table Layout

The table UI should adapt based on player count:

#### 6-Max Table

Best for fast, aggressive games.

**Layout:**

- 6 seats around an oval table.
- Larger avatars and action buttons.
- Easier mobile compatibility.

#### 9-Max Table

Standard full-ring format.

**Layout:**

- 9 seats around the table.
- Balanced spacing.
- Works well on desktop and tablet.

#### 12-Max Table

Extended private/home-game mode.

**Layout:**

- More compact seat design.
- Better suited for desktop.
- Mobile layout may need scrollable or zoomed table mode.

### 3.2 Player Seat Components

Each seat should display:

- Avatar.
- Player name.
- Stack size.
- Current bet.
- Dealer button, small blind, big blind markers.
- Hole cards for the current user.
- Hidden cards for opponents.

**Status:**

- Sitting out.
- Thinking.
- Folded.
- All-in.
- Disconnected.
- Waiting for big blind.
- Time bank countdown.

**Optional mini stats, if enabled:**

- VPIP.
- PFR.
- Stack BB count.

### 3.3 Game Board

The center of the table should show:

- Pot size.
- Side pots.
- Community cards:
  - Flop.
  - Turn.
  - River.
- Current street:
  - Preflop.
  - Flop.
  - Turn.
  - River.
  - Showdown.
- Previous action summary.
- Hand number.
- Blind level, if tournament-style.

### 3.4 Player Actions

**Basic actions:**

- Fold.
- Check.
- Call.
- Bet.
- Raise.
- All-in.
- Sit out.
- Return to game.
- Muck/show cards at showdown.
- Leave table.

**Bet controls:**

- Slider.
- Numeric input.
- Preset buttons:
  - 1/2 pot.
  - 2/3 pot.
  - Pot.
  - 2x.
  - 3x.
  - All-in.

**Advanced action options:**

- Auto-check/fold.
- Call any.
- Fold to any bet.
- Auto-muck.
- Show one card.
- Show both cards.
- Run it twice when all-in, if enabled.

---

## 4. Basic Poker Functions

### 4.1 Hand Lifecycle

Each hand should follow this state machine:

1. Waiting for enough players.
2. Assign dealer button.
3. Post small blind.
4. Post big blind.
5. Deal hole cards.
6. Preflop betting.
7. Deal flop.
8. Flop betting.
9. Deal turn.
10. Turn betting.
11. Deal river.
12. River betting.
13. Showdown.
14. Evaluate hands.
15. Award pot and side pots.
16. Save hand history.
17. Move dealer button.
18. Start next hand.

### 4.2 Required Poker Logic

The backend must reliably handle:

- Deck shuffling.
- Card dealing.
- Turn order.
- Blind posting.
- Minimum raise rules.
- Legal action validation.
- Pot calculation.
- Side pot calculation.
- All-in handling.
- Showdown hand evaluation.
- Split pots.
- Odd chip handling.
- Player disconnect behavior.
- Sit-out behavior.
- Rejoin behavior.
- Hand history generation.

The poker engine should be **server-authoritative**. The client should never be trusted to determine cards, outcomes, pot sizes, or legal actions.

### 4.3 Game Integrity

**Important integrity rules:**

- Server controls shuffle and deal.
- Clients only receive the cards they are allowed to see.
- Opponent hole cards are not sent to clients until showdown or voluntary reveal.
- Every action is recorded in an immutable hand log.
- The system validates every bet, raise, call, and fold.
- Game state is recoverable after server restart.
- Anti-cheating measures should detect suspicious collusion patterns over time.

---

## 5. Advanced Poker Configurations

The advanced settings should be grouped into a host-facing **Game Configuration Panel**.

### 5.1 Room Format

**Settings:**

- Seat count:
- **Game speed:**
  - Normal.
  - Turbo.
  - Custom action timer.
- **Game mode:**
  - Cash game.
  - Sit-and-go.
  - Tournament, future phase.
  - Club/private league, future phase.
- **Entry mode:**
  - Anyone with link.
  - Password required.
  - Host approval required.
  - Whitelist only.

### 5.2 Blind and Ante Settings

**Options:**

- Small blind.
- Big blind.
- Ante.
- Button ante.
- Straddle allowed.
- Mississippi straddle, optional.
- Blind increase schedule.
- Custom blind levels.
- Pause blind timer.
- Cap blinds at max level.

**Example configuration:**

| Setting           | Value        |
| ----------------- | ------------ |
| Small Blind       | 5            |
| Big Blind         | 10           |
| Starting Stack    | 2,000        |
| Ante              | Off          |
| Straddle          | Optional     |
| Blind Increase    | Every 20 min |

### 5.3 Buy-In and Chip Settings

**Options:**

- Starting stack.
- Minimum buy-in.
- Maximum buy-in.
- Rebuy enabled/disabled.
- Add-on enabled/disabled.
- Host approval for rebuys.
- Auto top-up.
- Chip denomination display.

**Display stack as:**

- Chips.
- Big blinds.
- Both.

**Advanced host controls:**

- Manually adjust player stack.
- Issue chips.
- Remove chips.
- Lock chip changes after session starts.
- Export final chip ledger.

### 5.4 Betting Rules

**Options:**

- No-limit.
- Pot-limit.
- Fixed-limit.
- Minimum raise enforcement.
- Maximum bet cap, optional for friendly games.
- All-in allowed.
- Short all-in reopen action rule.
- Allow bet slider presets.
- Allow custom bet sizes.
- Allow rabbit hunt, optional.

### 5.5 Special Game Modes

**Run It Twice**

When players are all-in before river:

- Run remaining board once.
- Run remaining board twice.
- Run remaining board three times, optional.
- Require all all-in players to agree.
- Split pot by board result.

**Bomb Pot**

Host can enable:

- Scheduled bomb pot every N hands.
- Random bomb pot chance.
- Double-board bomb pot.
- Mandatory ante amount.

**Straddle**

**Options:**

- No straddle.
- UTG straddle.
- Button straddle.
- Any-position straddle, optional.
- Straddle amount multiplier.

**Rabbit Hunting**

Optional setting where folded players may see what the next cards would have been after the hand ends.

**Recommended default:** Disabled.

**Reason:** It slows down gameplay and may encourage results-oriented thinking.

**Insurance**

Optional advanced/future feature. If included, it must be carefully designed because it affects expected value, game economics, and fairness.

### 5.6 Time Controls

**Options:**

- **Action timer:**
  - 10 seconds.
  - 20 seconds.
  - 30 seconds.
  - Custom.
- **Time bank:**
  - Disabled.
  - Fixed per hand.
  - Fixed per session.
  - Replenish every N hands.
- **Auto-action when timer expires:**
  - Check if possible.
  - Fold if facing bet.
  - Sit out after repeated timeout.

### 5.7 Table Behavior Settings

**Options:**

- Auto-start when minimum players seated.
- Minimum players required: Custom.
- Allow spectators.
- Allow chat.
- Allow emojis.
- Allow voice chat, optional future feature.
- Show mucked cards.
- Show all-in equity, optional.
- Show player stats at table.
- Show previous hand summary.
- Enable hand replay.

---

## 6. Data Analysis System

The data analysis system should be one of the major differentiators of the platform.

It should track statistics at four levels:

1. Hand-level data.
2. Session-level data.
3. Player-level data.
4. Room/club-level data.

### 6.1 Hand History

Every completed hand should generate a structured hand record.

A hand history should include:

- Room ID.
- Session ID.
- Hand number.
- Timestamp.
- Button position.
- Blinds and antes.
- Player seats.
- Starting stacks.
- Hole cards, with visibility rules.
- Community cards.
- Action log.
- Pot and side pot details.
- Showdown result.
- Winner or winners.
- Rake, if any.
- Final stacks.

**Example hand history** (design illustration only):

```text
Hand #104
Blinds: 5/10
Button: Alice
Players:
- Alice: 1,950
- Bob: 2,100
- Chen: 1,800

Preflop:
Bob posts SB 5
Chen posts BB 10
Alice raises to 30
Bob calls 25
Chen folds

Flop:
Pot 70
Board: Ah 9d 4c
Bob checks
Alice bets 45
Bob folds

Result:
Alice wins 70
```

### 6.2 Chip Summary

The chip summary should show each player’s movement over a session.

**Metrics:**

- Starting chips.
- Buy-ins.
- Rebuys.
- Add-ons.
- Cash-outs.
- Ending chips.
- Net win/loss.
- Biggest stack reached.
- Lowest stack reached.
- Hands played.
- BB/100.
- Profit per hour.

**Example chip summary table:**

| Player | Buy-In | Cash-Out | Net   | Hands | BB/100 |
| ------ | ------ | -------- | ----- | ----- | ------ |
| Alice  | 2,000  | 3,250    | +1,250| 104   | +48.1  |
| Bob    | 2,000  | 1,400    | -600  | 104   | -23.0  |
| Chen   | 2,000  | 2,350    | +350  | 89    | +15.7  |

### 6.3 Win/Loss Analysis

Per-player win/loss analytics:

- Net chips won/lost.
- Net big blinds won/lost.
- Win rate by hour.
- Win rate by 100 hands.
- Largest pot won.
- Largest pot lost.
- Biggest winning hand.
- Biggest losing hand.
- Profit graph over time.
- Session ranking.
- Cumulative player leaderboard.

**Visualizations:**

- Line chart: chip stack over time.
- Bar chart: net profit by player.
- Pie chart: pot share won.
- Heatmap: position profitability.
- Table: hand-by-hand ledger.

### 6.4 VPIP

VPIP stands for **Voluntarily Put Money In Pot**.

It measures how often a player voluntarily invests chips preflop.

**Counts as VPIP:**

- Calling preflop.
- Raising preflop.
- Limping.
- Completing small blind voluntarily.

**Does not count as VPIP:**

- Posting forced big blind.
- Posting forced small blind only, unless the player completes/calls/raises.
- Checking in big blind when no raise occurs.

**Formula:**

```text
VPIP = Hands where player voluntarily put money in preflop / Eligible hands
```

**Example:**

- Player played 100 eligible hands.
- Player voluntarily entered pot in 32 hands.
- **VPIP = 32%**

### 6.5 PFR

PFR stands for **Preflop Raise**.

It measures how often a player raises before the flop.

**Counts as PFR:**

- Open-raising.
- 3-betting.
- 4-betting.
- Any preflop raise.

**Does not count as PFR:**

- Calling.
- Limping.
- Checking in the big blind.
- Posting blinds.

**Formula:**

```text
PFR = Hands where player made a preflop raise / Eligible hands
```

**Example:**

- Player played 100 eligible hands.
- Player raised preflop in 18 hands.
- **PFR = 18%**

### 6.6 Additional Recommended Stats

**Preflop Stats**

- VPIP.
- PFR.
- Limp percentage.
- Open raise percentage.
- 3-bet percentage.
- Fold to 3-bet percentage.
- Cold call percentage.
- Steal attempt percentage.
- Fold big blind to steal.
- Fold small blind to steal.

**Postflop Stats**

- Continuation bet percentage.
- Fold to continuation bet.
- Check-raise percentage.
- Went to showdown percentage.
- Won at showdown percentage.
- Won when saw flop.
- Aggression factor.
- Aggression frequency.

**Positional Stats**

Stats by position:

- Small blind.
- Big blind.
- Under the gun.
- Hijack.
- Cutoff.
- Button.

Useful metrics by position:

- VPIP by position.
- PFR by position.
- Net win/loss by position.
- BB/100 by position.
- 3-bet by position.

**Pot-Level Stats**

- Average pot size.
- Largest pot.
- Pots won uncontested.
- Multiway pots won.
- Heads-up pots won.
- All-in pots won.
- Showdown pots won.

**Session-Level Stats**

- Hands played.
- Duration.
- Average hands per hour.
- Total chips in play.
- Biggest winner.
- Biggest loser.
- Most aggressive player.
- Tightest player.
- Loosest player.

---

## 7. Analytics Dashboard Design

### 7.1 Host Dashboard

The host should see:

- Current player stacks.
- Total chips issued.
- Total chips on table.
- Buy-in ledger.
- Cash-out ledger.
- Net win/loss by player.
- Hand count.
- Session duration.
- Export buttons.

**Recommended exports:**

- CSV.
- JSON.
- PDF session report.
- Poker hand history text format, optional.

### 7.2 Player Dashboard

Each player should see:

- Personal win/loss.
- Stack graph.
- VPIP.
- PFR.
- Aggression.
- Biggest pot won.
- Biggest pot lost.
- Recent hands.
- Position performance.
- Showdown performance.

**Privacy options:**

- Only show personal stats.
- Show table-wide stats after session ends.
- Show real-time table stats.
- Hide hole-card-based analysis until hand is complete.

### 7.3 Room-Level Analytics

For recurring private groups:

- Lifetime leaderboard.
- Total sessions played.
- Total hands played.
- Biggest lifetime winner.
- Most active player.
- Average VPIP/PFR per player.
- Head-to-head results.
- Monthly reports.
- Exportable club accounting.

---

## 8. Suggested Main Pages

### 8.1 Landing Page

**Purpose:**

- Explain product.
- Let users create or join a room.

**Sections:**

- Create private poker room.
- Join by invite link.
- Feature overview.
- Security/fairness explanation.
- Responsible play disclaimer.

### 8.2 Create Room Page

**Includes:**

- Room name.
- Seat count.
- Blind settings.
- Buy-in settings.
- Timer settings.
- Advanced options.
- Privacy settings.
- Create button.

### 8.3 Lobby / Waiting Room

**Includes:**

- Room name.
- Player list.
- Seat selection.
- Invite link.
- Game configuration summary.
- Host controls.
- Ready button.
- Start game button.

### 8.4 Poker Table Page

**Includes:**

- Poker table.
- Player seats.
- Community cards.
- Pot.
- Action buttons.
- Chat.
- Hand history sidebar.
- Room settings summary.
- Stats panel.

### 8.5 Session Summary Page

**Includes:**

- Final stacks.
- Buy-ins and cash-outs.
- Net results.
- Player rankings.
- Hand count.
- Biggest pots.
- VPIP/PFR table.
- Export report.

### 8.6 Player Profile Page

**Includes:**

- Historical sessions.
- Long-term stats.
- Graphs.
- Favorite formats.
- Recent hands.
- Achievements, optional.

---

## 9. Recommended Technical Architecture

Although no code should be written yet, the system should be designed around real-time reliability.

### 9.1 Frontend

**Recommended responsibilities:**

- Render table state.
- Send player actions.
- Display animations.
- Show cards, pots, stacks, timers, and analytics.
- Handle reconnect UI.
- Avoid doing authoritative poker calculations.

**Possible frontend stack:**

- React / Next.js.
- TypeScript.
- Tailwind CSS.
- WebSocket client.
- Charting library for analytics.

### 9.2 Backend

**Recommended responsibilities:**

- Authoritative poker engine.
- Room management.
- Player session management.
- Legal action validation.
- Deck shuffle and card dealing.
- Pot and side-pot calculation.
- Hand evaluation.
- Hand history storage.
- Real-time event broadcasting.
- Analytics calculation.

**Possible backend stack:**

- Node.js with TypeScript.
- NestJS or Fastify.
- WebSocket server.
- PostgreSQL.
- Redis for real-time room state.
- Background workers for analytics.

### 9.3 Real-Time Communication

Use WebSockets for:

- Player joining/leaving.
- Seat updates.
- Card dealing.
- Betting actions.
- Timer updates.
- Chat.
- Showdown.
- Stack updates.
- Reconnect state sync.

**Important design principle:**

The server sends each player a **personalized game-state view**.

**Example:**

- Alice receives Alice’s hole cards.
- Bob receives Bob’s hole cards.
- Spectators receive no hole cards.
- At showdown, only revealed cards are broadcast.

### 9.4 Database Design Concept

**Core entities:**

#### User

Stores registered user information.

**Fields:**

- User ID.
- Username.
- Email, optional.
- Avatar.
- Created date.

#### Room

Stores room-level configuration.

**Fields:**

- Room ID.
- Host ID.
- Room name.
- Seat count.
- Invite token.
- Privacy settings.
- Game configuration.
- Created date.
- Status.

#### Session

Represents one active or completed game session.

**Fields:**

- Session ID.
- Room ID.
- Start time.
- End time.
- Total hands.
- Total chips issued.
- Status.

#### PlayerSession

Represents a player inside a session.

**Fields:**

- Player session ID.
- User ID or guest ID.
- Seat number.
- Buy-in amount.
- Ending stack.
- Net result.
- Hands played.
- VPIP count.
- PFR count.

#### Hand

Stores each completed hand.

**Fields:**

- Hand ID.
- Session ID.
- Hand number.
- Button seat.
- Small blind.
- Big blind.
- Board cards.
- Pot result.
- Started at.
- Ended at.

#### HandAction

Stores every action inside a hand.

**Fields:**

- Action ID.
- Hand ID.
- Player ID.
- Street.
- Action type.
- Amount.
- Timestamp.
- Stack before.
- Stack after.

#### PlayerHand

Stores player-specific hand data.

**Fields:**

- Hand ID.
- Player ID.
- Seat.
- Starting stack.
- Ending stack.
- Hole cards, encrypted or access-controlled.
- Voluntarily put money in pot.
- Preflop raised.
- Went to showdown.
- Won hand.

---

## 10. Game Fairness and Security

### 10.1 Randomness

The platform should use secure server-side shuffling.

**Recommendations:**

- Use cryptographically secure random number generation.
- Shuffle server-side only.
- Do not expose undealt cards to clients.
- Log shuffle seed or use provably fair mode only if carefully designed.

### 10.2 Anti-Cheating

**Possible anti-cheating tools:**

- Detect multiple accounts from same device/IP.
- Detect suspicious soft play.
- Detect repeated chip dumping.
- Detect unusually coordinated actions.
- Detect shared hole-card patterns over many hands.
- Flag abnormal VPIP/PFR relationships between pairs.
- Host moderation tools.

### 10.3 Access Control

**Protect:**

- Room configuration.
- Admin actions.
- Hole cards.
- Hand histories.
- Analytics.
- Invite links.
- Session financial/chip ledgers.

**Permissions should be role-based:**

- Host.
- Player.
- Spectator.
- Guest.
- Admin.

---

## 11. Responsible Play and Legal Considerations

If this product uses only play-money chips, the legal risk is lower, but the site should still include:

- Responsible play messaging.
- No real-money gambling disclaimer, if applicable.
- Terms of service.
- Privacy policy.
- Age confirmation if needed.
- Jurisdiction review before enabling real-money play.

If real-money play is ever planned, that should be treated as a separate legal, compliance, payment, licensing, KYC, AML, and geolocation project.

**Recommendation:**

- Start as a private play-money/home-game tracking platform.
- Avoid real-money settlement inside the app during the first version.

---

## 12. MVP Scope

### 12.1 MVP Features

The first version should include:

- Create private room.
- Invite link.
- 6, 9, or 12 seat selection.
- Join as guest.
- Seat selection.
- No-limit Texas Hold’em.
- Fixed blinds.
- Starting stack.
- **Basic actions:**
  - Fold.
  - Check.
  - Call.
  - Bet.
  - Raise.
  - All-in.
- Server-side poker engine.
- WebSocket gameplay.
- Basic chat.
- Hand history.
- Session chip summary.
- Win/loss summary.
- VPIP.
- PFR.
- Export CSV.

### 12.2 Features to Delay Until Later

Should not be in MVP unless absolutely necessary:

- Real-money payments.
- Full tournament system.
- Insurance.
- Voice chat.
- Advanced anti-collusion machine learning.
- Mobile native apps.
- Multi-table support.
- Public matchmaking.
- Club marketplace.
- Complex rake system.

---

## 13. Phase Plan

### Overview

This plan breaks the project into eight focused phases from discovery through scaling. Each phase includes clear deliverables and milestones to keep the scope manageable and verifiable.

### Phase 1 — Discovery & Spec

**Goals:** Finalize product requirements and technical design.

- Page-by-page wireframes and user flows.
- Formal PRD with MVP boundary and acceptance criteria.
- Room configuration schema and game settings spec.
- Poker engine state machine and WebSocket event list.
- Database schema and analytics event model.

#### Phase 1 — Checklist & Next Steps

- **In progress:** Draft PRD and acceptance criteria (this is the current focus).
- **Planned:** Create page-by-page wireframes (low-fidelity) for Landing, Create Room, Lobby, Table, Session Summary, and Profile pages.
- **Planned:** Define room configuration schema (JSON schema) covering seat counts, blinds, buy-in, advanced options.
- **Planned:** Specify poker engine state machine (hand lifecycle, legal action validation, side-pot rules).
- **Planned:** Produce WebSocket event list for realtime messages (join, seat, deal, action, timer, showdown, sync).
- **Planned:** Draft database schema for core entities: User, Room, Session, PlayerSession, Hand, HandAction, PlayerHand.
- **Planned:** Define analytics event model (VPIP, PFR flags, action events) and required fields.
- **Planned:** List risks, assumptions, and acceptance tests for each deliverable.
- **Planned:** Produce a short milestone timeline (2–4 week sprints suggested) and owners for each task.

Next immediate step: finalize the PRD section in this document and add acceptance criteria for the MVP boundary.

## PRD — MVP Specification

**Purpose:** Describe the minimally-shippable product that delivers playable, private, server-authoritative Texas Hold'em for home groups and provides basic session analytics.

**MVP Scope (In‑scope):**
- Create private room with invite link and optional password.
- Join as guest, choose a seat (6/9/12 support).
- No-limit Texas Hold'em gameplay with server-side deck, deal, and full hand lifecycle.
- Basic betting actions: fold, check, call, bet, raise, all-in.
- Blind posting and fixed blind levels; starting stack and buy-in controls.
- WebSocket-based realtime sync and basic chat.
- Persistent hand history and session-level chip summary.
- Basic analytics: per-session VPIP and PFR, stack-over-time graph, CSV/JSON export.

**Out of scope (for MVP):**
- Real-money payments and KYC.
- Full tournament/multi-table system.
- Advanced game modes (run-it-twice, bomb pots) and voice chat.
- Complex anti-cheat ML systems (light heuristics only).

**Acceptance criteria (testable):**
- A host can create a private room and generate an invite that allows peers to join and seat.
- At least 2 seated players can start and complete a hand with correct dealing, legal actions enforcement, pot and side-pot calculation, and correct winner payout recorded in hand history.
- Clients receive personalized state (only their hole cards) and synchronized table state for community cards, bets, pots, and player stacks.
- A disconnected player can reconnect and resume their seat without causing state corruption.
- Hand history exports (JSON/CSV) produce a complete, replayable record for every completed hand.
- VPIP and PFR are calculated correctly from stored action events and visible in session summary.

**Success metrics (initial):**
- Functional: 0 critical bugs for basic hand lifecycle in staged E2E tests.
- UX: average time-to-first-hand < 5 minutes for new users following invite.
- Adoption: first closed-playtest with 3 different friend groups within first month of MVP run.

**Milestone plan (short):**
- Sprint 1 (2 weeks): PRD sign-off, engine state machine, basic DB schema.
- Sprint 2 (2 weeks): Engine implementation with unit tests + basic API/WebSocket.
- Sprint 3 (2 weeks): Frontend MVP (lobby, table, join flow) + E2E gameplay tests.

Owners and detailed task assignments to be added in the Phase 1 checklist.

### Phase 2 — Core Engine & API

**Goals:** Build the server-authoritative poker engine and backend APIs.

- Secure deck shuffle, deal, and hand evaluation.
- Pot and side-pot calculation, odd-chip handling.
- Legal-action validation and state machine implementation.
- Unit tests for engine logic and deterministic simulations.
- REST/WebSocket endpoints for room/session control.

### Phase 3 — MVP Frontend & Realtime

**Goals:** Deliver the playable MVP UI and realtime connectivity.

- Lobby and create-room UI with invite flow.
- Join-as-guest flow and seat selection.
- Responsive poker table UI (6/9/12 layouts).
- WebSocket client integration and basic chat.
- Action controls (fold/check/call/bet/raise/all-in).

### Phase 4 — Gameplay & Resilience

**Goals:** Harden gameplay, persistence, and reconnect behavior.

- Full hand lifecycle in production-like conditions.
- Blind posting, timed increases, and betting rounds.
- Hand history persistence and replay capability.
- Disconnect/reconnect handling and time-bank/auto-action.
- Integration tests and end-to-end gameplay QA.

### Phase 5 — Host Controls & Room Management

**Goals:** Add host tooling and secure invitation semantics.

- Invite token system (expire/revoke/usage limits).
- Host approval, password-protected rooms, and spectator controls.
- Host admin panel: pause/resume, kick, chip adjustments.
- Exports: hand history, session ledger (CSV/JSON/PDF).

### Phase 6 — Analytics & Reports

**Goals:** Implement event-driven analytics and player/session reports.

- Event ingestion pipeline and analytics worker.
- Session and player dashboards (stack graph, VPIP, PFR).
- Aggregations: BB/100, win-rate, positional stats.
- Exportable reports and CSV/JSON endpoints.

### Phase 7 — Advanced Game Modes & Settings

**Goals:** Add optional, advanced poker rules and modes.

- Straddle variants, run-it-twice, bomb pots, rabbit hunting.
- Blind schedules and custom level editors.
- Advanced betting rules and host-configurable presets.

### Phase 8 — Accounts, Clubs & Scaling

**Goals:** Move to persistent users, clubs, and production scaling.

- Registered user profiles and persistent history.
- Club/league features, leaderboards and lifetime stats.
- Anti-cheating tooling and device/account heuristics.
- Performance tuning, autoscaling, and compliance reviews.

---

---

## 14. Recommended MVP Configuration Defaults

Suggested defaults for new rooms:

| Setting        | Value                      |
| -------------- | -------------------------- |
| Game Type      | No-Limit Texas Hold’em     |
| Seats          | 9                          |
| Small Blind    | 5                          |
| Big Blind      | 10                         |
| Starting Stack | 2,000                      |
| Minimum Players| 2                          |
| Action Timer   | 30 seconds                 |
| Time Bank      | 60 seconds per player      |
| Ante           | Off                        |
| Straddle       | Off                        |
| Run It Twice   | Off                        |
| Bomb Pot       | Off                        |
| Spectators     | Off                        |
| Chat           | On                         |
| Host Approval  | Off                        |
| Invite Link    | Enabled                    |
| Analytics      | Enabled                    |

---

## 15. Example User Journey

### Host Journey

1. Host opens website.
2. Clicks Create Room.
3. Chooses 9-max table.
4. Sets blinds to 5/10.
5. Sets starting stack to 2,000.
6. Enables invite-only room.
7. Creates room.
8. Copies invitation link.
9. Sends link to friends.
10. Players join lobby.
11. Host starts game.
12. Game runs in real time.
13. Host ends session.
14. System generates final report.

### Player Journey

1. Player receives invitation link.
2. Opens link.
3. Enters nickname or logs in.
4. Joins lobby.
5. Selects seat.
6. Waits for host to start.
7. Plays hands.
8. Reviews personal stats.
9. Views final session summary after game.

---

## 16. Key Design Principles

### 16.1 Server Authority

The server must be the single source of truth for:

- Deck.
- Cards.
- Pot.
- Legal actions.
- Winners.
- Stack changes.
- Analytics events.

### 16.2 Private by Default

Because this is intended for invite-based games:

- Rooms should be private by default.
- Invite tokens should be secure.
- Spectators should be disabled by default.
- Public listing should be a later feature.

### 16.3 Analytics Built From Events

Do not calculate important analytics only from final stacks.

Instead, store every meaningful event:

- Blind posted.
- Call.
- Raise.
- Fold.
- Bet.
- Check.
- All-in.
- Showdown.
- Pot award.

This allows VPIP, PFR, aggression, showdown stats, and positional stats to be recalculated accurately later.

### 16.4 Mobile-Friendly but Desktop-First

A 12-player poker table is difficult on mobile.

**Recommendation:**

- Optimize MVP for desktop and tablet.
- Support 6-max mobile first.
- Add a dedicated compact mobile layout later.

---

## 17. High-Level Feature Checklist

### Room Features

- Create room.
- 6/9/12 player capacity.
- Invite link.
- Password option.
- Host approval.
- Seat selection.
- Spectator mode.
- Room settings.

### Gameplay Features

- Texas Hold’em.
- Blinds.
- Dealing.
- Betting rounds.
- Fold/check/call/bet/raise/all-in.
- Side pots.
- Showdown.
- Split pots.
- Hand history.
- Reconnect.

### Advanced Settings

- Ante.
- Straddle.
- Run it twice.
- Bomb pot.
- Blind schedule.
- Time bank.
- Auto top-up.
- Rebuy.
- Rabbit hunting.
- Table chat.

### Analytics

- Chip summary.
- Win/loss.
- VPIP.
- PFR.
- BB/100.
- Aggression.
- Showdown stats.
- Position stats.
- Stack graph.
- Session report.
- CSV/JSON export.

---

## 18. Suggested Next Step Before Coding

Before writing code, the best next step is to create a more formal product specification with:

- Page-by-page wireframe descriptions.
- Exact room configuration schema.
- Poker engine state machine.
- WebSocket event list.
- Database schema.
- MVP/non-MVP boundary.
- Analytics formula definitions.
- Host/admin permission rules.

A good next design document could be:

**Online Texas Hold’em Poker Website — MVP Product Requirements Document**

That document would turn this concept into a build-ready specification without yet implementing the code.

---

## Document History

| Version | Description                    |
| ------- | ------------------------------ |
| Draft   | Product design draft (this doc) |

_Source: Codex cloud task design; consolidated into repository markdown._
