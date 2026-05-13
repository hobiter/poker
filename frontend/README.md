# Frontend (Phase 3 MVP)

Minimal Vite + React + TypeScript frontend to exercise the server WebSocket and HTTP endpoints.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

Open the app (usually at `http://localhost:5173`), set the backend `Server URL` to `http://localhost:8000`, create/join a room and connect the WebSocket using the generated `roomId` and `clientId`.

WebSocket URL format used by the app: `ws://<host>/ws/<room_id>/<client_id>`

## Testing

See the project `TESTING.md` at the repo root for commands to run unit tests,
the demo harness, frontend build steps, and Docker Compose instructions.

