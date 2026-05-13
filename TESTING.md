# Testing and Running

This document describes how to run unit tests, the demo harness, start the
backend and frontend for development, build the frontend, and run the project
with Docker Compose.

Prerequisites
- Python 3.11+ (3.14 tested locally)
- Node.js 18+ (Node 20 recommended)
- npm
- Docker & docker-compose (optional, for containerized run)

Quick setup (recommended)

```bash
# create venv
python -m venv .venv
# activate (POSIX)
source .venv/bin/activate
# activate (PowerShell)
.venv\Scripts\Activate.ps1

# install Python deps
pip install -r requirements.txt

# install frontend deps
cd frontend
npm install
cd ..
```

Run backend unit tests

```bash
# run all Python unit tests (from repo root)
python -m unittest discover -v

# run a single test module
python -m unittest engine.test_deck -v
```

Demo harness (integration via FastAPI TestClient)

The demo harness uses FastAPI's TestClient to run an end-to-end flow
without network access. It creates a room, opens two websocket clients,
starts a hand, posts actions and forces a timeout.

```bash
# run the demo harness using the active venv Python
.venv\Scripts\python.exe demo/demo_run.py
```

Run the servers locally (development)

Start the backend (defaults to port 8000):

```bash
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend dev server (Vite, usually at http://localhost:5173):

```bash
cd frontend
npm run dev
```

Build the frontend for production

```bash
cd frontend
npm run build
# built files are in frontend/dist
```

Run the stack via Docker Compose

```bash
docker compose build
docker compose up
# backend: http://localhost:8000
# frontend (nginx): http://localhost:5173
```

Useful test-only endpoints

- `POST /rooms/{room_id}/force_timeout` — forces the current player to timeout (auto-fold). Useful to simulate timeout-based flows in tests and demos.
- `GET /rooms/{room_id}/session/{player_id}/legal_actions` — returns the legal actions for `player_id` in the active session. Used by the frontend to render allowed buttons.

CI

Continuous integration is configured in `.github/workflows/ci.yml`. It runs the
Python unit tests and builds the frontend.

Troubleshooting

- If you see `ModuleNotFoundError: httpx` while running tests, install the HTTPX package: `pip install httpx` or `pip install -r requirements.txt`.
- If Vite build fails, ensure Node.js version matches the recommended version (Node 20 in CI).

If you want, I can also add a script or Makefile that runs the common test/build commands.
