# Deploy the Frontend to Vercel (updated)

This guide shows how to deploy the Vite + React frontend in `frontend/` to Vercel, how
to set a backend URL via environment variables, and notes about hosting the FastAPI
backend (HTTP + WebSocket) separately.

> Note: this repo also contains a legacy static demo at `demo/web/`. The preferred
> modern frontend is the Vite app in `frontend/` (used by the development workflow).

## Prerequisites

- A GitHub repository containing this project.
- A Vercel account (https://vercel.com) connected to the repo.
- A publicly reachable backend URL (HTTPS + WSS) running the FastAPI app.

## Overview

- Deploy the static frontend to Vercel (serves `frontend/dist`).
- Host the backend (separately) on a platform that supports WebSocket upgrades (Render, Fly, Railway, etc.).
- Configure an environment variable (`VITE_SERVER_URL`) in the Vercel project so the deployed frontend knows which backend to use.

## A — Deploy via Vercel (Git import)

1. Go to https://vercel.com, click **New Project → Import Git Repository**, and choose your repo.
2. In the import settings:
  - **Root Directory**: `frontend`
  - **Framework Preset**: `Vite` (or `Other`)
  - **Build Command**: `npm ci && npm run build`
  - **Output Directory**: `dist`
3. In the **Environment Variables** section add:
  - `VITE_SERVER_URL` = `https://api.example.com` (replace with your backend URL)
  - (Optional) any other runtime keys your app needs.
4. Click **Deploy**. Vercel will build the Vite app and serve the files from `/dist`.

If you prefer to keep the project root as the Vercel root, set:

  - **Root Directory**: (empty)
  - **Build Command**: `cd frontend && npm ci && npm run build`
  - **Output Directory**: `frontend/dist`

## B — Deploy with Vercel CLI

From the `frontend` folder, use the CLI (no global install required):

```bash
cd frontend
npx vercel --prod
```

Follow the prompts and set the same build/output configuration and `VITE_SERVER_URL` environment variable in the dashboard or during the CLI prompts.

## Using `VITE_SERVER_URL` in the frontend

To have the frontend use an environment-provided backend URL at build time, use Vite's
`import.meta.env` variables. For example, update the initial `serverUrl` in
`frontend/src/App.tsx` (replace the existing hard-coded default):

```ts
const defaultServerUrl = import.meta.env.VITE_SERVER_URL ?? 'http://localhost:8000'
const [serverUrl, setServerUrl] = useState(defaultServerUrl)
```

This lets Vercel inject `VITE_SERVER_URL` at build time while keeping a sensible local
default for development. If you want runtime configuration (no rebuild required), you'll need
to implement a tiny JSON config endpoint or serverless function — but note that Vercel
serverless functions do not support raw WebSocket upgrades.

## Backend hosting recommendations

The backend must be reachable over HTTPS and support WebSocket upgrades (wss://):

- **Render**: Create a Web Service. Build with `pip install -r requirements.txt` and run with either:

```bash
# using gunicorn + uvicorn workers (common)
gunicorn -k uvicorn.workers.UvicornWorker server.app:app

# or directly with uvicorn
uvicorn server.app:app --host 0.0.0.0 --port $PORT
```

- **Fly / Railway / DigitalOcean App Platform**: similar commands; ensure WebSocket support is enabled.

Minimal `requirements.txt` for deployment:

```
fastapi
uvicorn[standard]
httpx
gunicorn
```

## CORS and WebSocket notes

- Configure CORS to allow your Vercel origin. Example in `server/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
   CORSMiddleware,
   allow_origins=["https://<your-vercel-domain>.vercel.app"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)
```

- For quick testing you can use `allow_origins=["*"]`, but this is not recommended for production.
- Vercel serves the frontend over HTTPS, so your backend must speak HTTPS too; otherwise browsers will block mixed content and WebSocket upgrades will fail.
- Vercel's static hosting cannot proxy raw WebSocket upgrades to another host via a simple rewrite; therefore the backend must directly expose a `wss://` endpoint.

## Verify the deployment

1. Open the Vercel URL (e.g. `https://<project>.vercel.app`).
2. If you set `VITE_SERVER_URL`, the frontend should default to that backend. Otherwise, set the Server URL input in the UI.
3. Create/join a room and open two browser tabs to exercise WebSocket messages and hand flow.

## Troubleshooting

- **CORS errors**: Confirm the origin in `allow_origins` matches the Vercel domain (including scheme).
- **WSS handshake failures**: Ensure the backend is HTTPS and the domain supports WebSocket upgrades.
- **Backend unreachable**: Check that firewall and platform settings allow inbound connections on port 443 or the assigned host port.

## Notes & alternatives

- If you need the frontend and backend to be deployed together under one hostname, consider deploying the backend to a platform that supports HTTP + WebSocket and then use the frontend to call that backend directly (recommended).
- Vercel serverless functions are not suitable for long-lived WebSocket connections; use a dedicated host for the FastAPI server.

---

If you'd like, I can:

- Update `frontend/src/App.tsx` to read `VITE_SERVER_URL` by default and commit that change, or
- Add a sample `vercel.json` if you prefer explicit build and route settings.

Tell me which and I'll apply it.

## Example `vercel.json` (proxying API)

To keep frontend on Vercel and route API calls to a separate backend, add a `vercel.json` at the repo root like this:

```json
{
  "version": 2,
  "builds": [
    { "src": "frontend/package.json", "use": "@vercel/static-build", "config": { "distDir": "dist" } }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "https://YOUR_BACKEND_URL/$1" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

Replace `https://YOUR_BACKEND_URL` with your backend URL. Note: Vercel rewrites can proxy HTTP endpoints, but they do not proxy raw WebSocket upgrades — your backend must be directly reachable at `wss://` for real-time WebSocket connections.

