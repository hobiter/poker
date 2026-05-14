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

## Deploying on Vercel

The frontend can be hosted on Vercel, but the poker server should be hosted
separately on a platform that supports long-running FastAPI WebSocket
connections.

Recommended backend hosts:

- Render Web Service: easiest Fly.io alternative for this project, with direct
  WebSocket support and GitHub/Docker deployment.
- Railway: quick Python/Docker deployments; test WebSocket reconnect behavior
  before relying on multiple instances.
- Google Cloud Run: production-ready container hosting with WebSocket support,
  but WebSocket requests are still subject to the service request timeout, so
  clients need reconnect logic.
- Koyeb: supports container/web services and WebSocket apps.
- DigitalOcean App Platform: possible with a web service/container, though less
  clearly documented for this exact FastAPI WebSocket setup.

Avoid hosting the poker backend itself on Vercel Functions. Vercel is a good
fit for the Vite frontend, but Vercel Functions do not support acting as a
WebSocket server.

### Deploying the backend to Render Web Service

1. Push the repository to GitHub.
2. In Render, create a new **Web Service**.
3. Connect the GitHub repository.
4. Select the backend service settings:

```text
Runtime: Python 3
Root Directory: leave blank
Build Command: pip install -r requirements.txt
Start Command: uvicorn server.app:app --host 0.0.0.0 --port $PORT
```

5. Deploy the service.
6. After Render finishes deploying, copy the service URL, for example:

```text
https://poker-server.onrender.com
```

7. In the Vercel frontend project, add this environment variable:

```text
VITE_SERVER_URL=https://poker-server.onrender.com
```

8. Redeploy the Vercel frontend so the Vite build includes the backend URL.

The frontend will call the Render backend over HTTPS and connect to WebSockets
at:

```text
wss://poker-server.onrender.com/ws/<room_id>/<client_id>
```

Render may spin down free web services after inactivity. If the first request
after a quiet period feels slow, that is usually the service waking up. For
better multiplayer reliability, use a paid Render instance and keep the backend
at one instance while the app uses the current in-memory room/session store.

Render advanced settings:

```text
Secret Files: leave empty
Health Check Path: leave empty for now
Registry Credential: No credential
Docker Build Context Directory: .
Dockerfile Path: ./Dockerfile
Docker Command: uvicorn server.app:app --host 0.0.0.0 --port $PORT
Pre-Deploy Command: leave empty
Auto-Deploy: On Commit
Build Filters: leave empty
```

Do not set `Health Check Path` to `/healthz` unless the backend has a matching
route. To add one, put this in `server/app.py`:

```python
@app.get("/healthz")
def healthz():
    return {"ok": True}
```

Then Render can use:

```text
Health Check Path: /healthz
```

If deploying as a Python service instead of a Docker service, ignore the Docker
fields and use:

```text
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn server.app:app --host 0.0.0.0 --port $PORT
```

After deploying the backend, set the Vercel frontend environment variable:

```text
VITE_SERVER_URL=https://your-backend.example.com
```

The app will connect to the backend API over HTTPS and to the WebSocket endpoint
as `wss://your-backend.example.com/ws/<room_id>/<client_id>`.

For the current in-memory backend store, run only one backend instance at first.
If the backend is scaled to multiple instances, room state and WebSocket
connections can be split across instances unless shared state such as Redis or a
database is added.

Once the Vercel URL is known, tighten the backend CORS settings in
`server/app.py` from `["*"]` to the deployed Vercel origin.

## Testing

See the project `TESTING.md` at the repo root for commands to run unit tests,
the demo harness, frontend build steps, and Docker Compose instructions.

