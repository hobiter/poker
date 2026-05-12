# Demo: Browser client for Poker Phase 2

This demo shows a minimal browser-based client that talks to the local FastAPI server via HTTP and WebSocket.

Files:
- `demo/web/index.html` — single-page demo UI (Create room, Join, Open WS, Start hand, Send action, Force timeout)
- `demo/web/app.js` — client logic

Quick start (Windows):

1. Activate your virtualenv and run the FastAPI server:

```powershell
.venv\Scripts\python.exe -m uvicorn server.app:app --reload --port 8000
```

2. Serve the demo static files (from repo root):

```powershell
# Using Python's simple HTTP server
python -m http.server 5500 --directory demo/web
# then open http://localhost:5500 in your browser
```

3. Open the page, ensure the Server base URL is `http://localhost:8000`, then:
- Create a room
- Join as two players (open two browser tabs or use different display names)
- Open WebSocket(s) and Start Hand
- Use the Send Call and Force Timeout buttons to see WS events

Notes:
- The demo is intentionally minimal and intended for local testing only.
- If you run the server on a different host/port, update the Server base URL in the UI.