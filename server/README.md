# Server (Phase 2 scaffold)

This folder contains a minimal FastAPI-based scaffold for Phase 2:

- `app.py` — FastAPI application with HTTP endpoints and a WebSocket endpoint.
- `models.py` — Pydantic request models.
- `storage.py` — Simple in-memory store for rooms and players (dev-only).
- `ws_manager.py` — Basic WebSocket connection manager for broadcasting.
- `tests/` — unit tests for HTTP API and WebSocket behavior.

Run server tests locally (after installing dependencies):

```bash
python -m unittest discover -s server -p "test_*.py" -v
```

To run the app locally for manual testing:

```bash
# install requirements (fastapi, uvicorn)
uvicorn server.app:app --reload
```

Useful endpoints:

- `GET /healthz` — lightweight health check for Render or another web service host.
- `GET /rooms/{room_id}/state?client_id={player_id}` — JSON-safe room snapshot for reconnects, including public table state plus the requesting player's private hole cards when available.
- `GET /rooms/{room_id}/session/{player_id}/legal_actions` — legal actions for the active player.
- `POST /rooms/{room_id}/force_timeout` — test-only timeout simulation.
