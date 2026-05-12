# Phase 1 — Milestones, Timeline, and Owners

Status: Completed — 2026-05-12

This document captures the Phase 1 milestone breakdown, owners (roles), and a short retrospective timeline. Replace role placeholders with real assignees as appropriate.

## Completed Deliverables

- PRD and MVP acceptance criteria (`PRODUCT_DESIGN.md` PRD section)
- Room configuration JSON Schema (`design/phase-1/room-configuration.schema.json`)
- Poker engine state machine spec (`design/phase-1/poker-engine-state-machine.md`)
- WebSocket event list (`design/phase-1/websocket-events.md`)
- Database DDL for core entities (`design/phase-1/db-schema.sql`)
- Analytics event schema (`design/phase-1/analytics-events.schema.json`)
- Low-fidelity wireframes and component list (`design/phase-1/wireframes.md`)
- Risk, assumptions and acceptance tests (`design/phase-1/risk-assumptions.md`)
- Engine scaffold with seeded shuffle and deterministic hand replay tests (`engine/`)

## Retrospective timeline (short)

- Discovery & PRD (3 days): scoped MVP, acceptance criteria, and PRD sign-off.
- Design artifacts (4 days): wireframes, room-config schema, event lists.
- Engine spec & tests (5 days): state machine, DB schema, seeded-deck + hand evaluator unit tests.

Total Phase 1 elapsed: ~12 days (iterative review and revisions included).

## Milestones and owners (recommended role mapping)

- Product / PRD sign-off: Product Owner (role: Product)
- UX / Wireframes: Designer (role: Design)
- Engine state machine and deterministic testing: Tech Lead / Backend Engineer (role: Backend)
- DB schema and analytics events: Backend / Data Engineer (role: Data)
- WebSocket contract and API outline: Tech Lead / Backend (role: Backend)
- Acceptance tests and risk mitigation validation: QA Engineer (role: QA)

Suggested quick owners for Phase 2 kickoff

- Tech Lead: Backend (owner: Backend)
- Backend Engineer: implement engine + API (owner: Backend)
- Frontend Engineer: MVP UI (owner: Frontend)
- QA: integration and E2E tests (owner: QA)
- Product: acceptance criteria and playtest coordination (owner: Product)

## Handover notes to Phase 2

- All engine unit tests are in `engine/` and must be extended with additional deterministic scenarios (multiway all-in, odd-chip distribution).
- The WebSocket event list defines expected names/payloads — Phase 2 should convert these into concrete protocol schemas (e.g., JSON Schema or TypeScript types).
- The DB DDL is a starting point; Phase 2 should adapt to ORM of choice and add migrations.
- Acceptance tests listed in `risk-assumptions.md` should be turned into automated E2E tests (use headless client mocks and seeded runs).

## Next immediate steps (Phase 2 kickoff)

1. Create Phase 2 epic with tasks: engine implementation, API contracts, auth model, and integration test harness.
2. Assign named owners and schedule 2-week sprints for Phase 2 deliverables.
3. Add CI job to run `python -m unittest` for `engine/` during PR validation.
