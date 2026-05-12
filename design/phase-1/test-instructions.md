# Phase 1 — Test Instructions

Purpose: provide concise, actionable instructions for running and extending the Phase 1 unit tests (engine scaffold), mapping tests to acceptance criteria, and a minimal CI example.

1) Run tests locally

- Run all engine tests:

```bash
python -m unittest discover -s engine -p "test_*.py" -v
```

- Run a single test case (example):

```bash
python -m unittest engine.test_deck.TestDeck.test_same_seed_reproducible
```

Notes: these commands work on Windows PowerShell and bash. Ensure Python 3.8+ is available on PATH.

2) What tests exist (phase 1)

- `engine/test_deck.py` — deterministic deck behavior and seeded shuffle reproducibility. Verifies dealing counts and uniqueness.
- `engine/test_hand_evaluator.py` — seven-card hand evaluator categories, deterministic replay via `replay_hand_from_seed`, and simple tie scenarios.

3) Deterministic testing guidelines

- Use explicit seeds for RNG when you need reproducibility. The Deck API supports `shuffle(seed)`; the hand replay helper `replay_hand_from_seed(seed, num_players)` is provided for quick deterministic scenarios.
- Keep seeds explicit in tests (small integers) so CI and local runs produce identical outputs.

4) Mapping acceptance tests → automated tests (current coverage)

- Seeded shuffle replay determinism: covered by `engine/test_deck.py` and `engine/test_hand_evaluator.py`.
- Deterministic winner calculation and tie-hand behavior: covered by `engine/test_hand_evaluator.py`.

Not yet automated (recommendations):

- Full hand lifecycle with side-pot & odd-chip distribution (create unit tests using engineered action sequences and the engine state machine).
- Disconnect/reconnect and personalized state privacy tests (requires integration test harness or mocked WebSocket server).

5) How to add tests

- Place new test files under the `engine/` package and name them `test_*.py`.
- Use Python's `unittest` (consistent with current tests) and keep tests small and deterministic.
- For engine-level deterministic scenarios, prefer seeding the deck explicitly and using `replay_hand_from_seed` where helpful.

6) Minimal CI example (GitHub Actions)

Create `.github/workflows/python-tests.yml` with this minimal job to run engine tests on PRs and pushes:

```yaml
name: Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: python -m pip install --upgrade pip
      - name: Run engine tests
        run: python -m unittest discover -s engine -p "test_*.py" -v

```

7) Suggested next automated tests to implement

- Side-pot scenarios with multiple all-ins and non-trivial payouts (unit tests using engineered `hand_actions`).
- Integration test for `state_sync` to assert no opponent hole cards appear in public view.
- Persistent hand history export tests (verify JSON/CSV output shape matches `db-schema.sql` fields).

8) Contact / Maintainer

- Test owner: Backend / Engine team (see `design/phase-1/milestones.md` for suggested owners).
- When adding tests, update the `design/phase-1/milestones.md` and `design/phase-1/README.md` handoff notes if new acceptance tests are automated.

---

This file is a living document — extend it with integration test commands, CI badges, and links to test reports as Phase 2 adds API and WebSocket integration.
