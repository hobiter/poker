# Phase 1 — Low-fidelity Wireframes & Component List

Purpose: produce quick, annotated wireframes for the main pages so engineering and design share the same UI expectations. These are low-fi textual wireframes and a component breakdown for the MVP pages.

Pages

- Landing Page
  - Top: product name / short tagline, `Create Room` primary CTA, `Join by invite` secondary CTA.
  - Middle: 3 feature cards (Private rooms, Server-authoritative engine, Session analytics).
  - Footer: responsible play, legal blurb, link to docs.
  - Mobile: single-column stack, CTAs full-width.
  - Acceptance: user can reach Create Room or Join by invite within 2 clicks.

- Create Room Page
  - Left column (form): Room name, Seat count (6/9/12), Game type, Small/Big blind, Starting stack, Buy-in min/max, Action timer, Time bank, checkboxes for advanced options (straddle, run-it-twice, rabbit hunt), Visibility (private/password/approval), Create button.
  - Right column (preview): Table layout preview, example invite link, summary card showing calculated chips in play.
  - Acceptance: required fields validated; Create returns `roomId` and invite link.

- Lobby / Waiting Room
  - Top: Room name, invite link, host controls (start, pause, settings), seat map (graphical oval) with seat components.
  - Left: player list + small chat panel.
  - Right: room settings summary and host actions (kick, approve, export).
  - Mobile: collapsed table view + expandable player list.
  - Acceptance: players can take a seat and host can start game once min players present.

- Poker Table Page (Main gameplay)
  - Center: oval table rendering, seats with avatar, name, stack, current bet; dealer/SB/BB markers.
  - Above table: hand number, blind level, pot display, previous-action strip.
  - Community cards centered; reveal animation placeholders.
  - Bottom: action controls for current player (Fold / Check / Call / Bet / Raise / All-in), bet slider / presets, numeric input.
  - Side: hand history panel (collapsible), stats panel with session VPIP/PFR for players (opt-in visibility).
  - Mobile: compact action bar and stacked info panels; prefer 6-max for mobile screens.
  - Key privacy rule: only the client receives its own hole cards in `personalView`.
  - Acceptance: server-sent `personalView` displays hole cards only to owner; actions trigger `action:post` events.

- Session Summary Page
  - Leaderboard: final stacks and net result.
  - Chip movement table: buy-ins, rebuys, cash-outs, and final stack per player.
  - Charts: stack-over-time sparkline per player, export buttons (CSV/JSON/PDF).
  - Acceptance: exports contain full hand ledger with action sequences.

- Player Profile Page
  - Recent sessions list, aggregate stats (VPIP/PFR/BB100), session filter by club/room.

Component List (short)

- `Header` — global navigation, brand, login state.
- `RoomConfigForm` — reusable form used on Create Room; validates fields and emits `create`.
- `TablePreview` — visual mock of table layout for lobby and create-room preview.
- `Seat` — shows avatar, stack, seat status (sitting out/thinking/all-in/disconnected).
- `ActionControls` — renders allowed actions for active player plus bet controls.
- `BetSlider` — slider + presets + numeric input; emits validated amounts.
- `HandHistory` — ordered action list for current/previous hands with timestamps.
- `InvitePanel` — invite URL, copy button, expiry/regenerate controls (host-only).
- `HostControls` — pause/resume, kick, adjust-chips, export.
- `StatsPanel` — compact per-player VPIP/PFR and stack BB count (privacy-aware).

Wireframe Deliverables

- `design/phase-1/wireframes.md` (this file): low-fi annotated wireframes and component list.
- Next: produce clickable low-fi mockups (Figma/PNG) using these annotations (optional, outside repo).
