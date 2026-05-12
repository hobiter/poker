# Phase 1 — Design artifacts

This folder contains Phase 1 design artifacts for the project:

- `room-configuration.schema.json` — JSON Schema for room configuration and game settings.
- `poker-engine-state-machine.md` — concise state machine and implementation notes for the server-authoritative engine.
- `websocket-events.md` — WebSocket event list and payload guidance (client↔server).
- `db-schema.sql` — PostgreSQL DDL for core entities (users, rooms, sessions, hands, actions).
- `analytics-events.schema.json` — JSON Schema for analytics event ingestion.

Next recommended steps:

1. Review and sign off schemas and state-machine details.
2. Start implementation of deterministic unit tests for the engine (seeded shuffle + replay tests).
3. Produce low-fidelity wireframes for the main pages (landing, create room, lobby, table).

Phase 1 status: Completed (2026-05-12).

Files to review for handoff:

- `milestones.md` — Phase 1 milestones, owners, and handover notes.
- `room-configuration.schema.json` — canonical room config schema.
- `poker-engine-state-machine.md` — authoritative state transitions and test notes.

