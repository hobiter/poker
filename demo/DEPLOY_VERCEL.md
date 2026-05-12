# Deploy the Demo UI to Vercel

This guide explains how to publish the static demo site located at [demo/web/index.html](demo/web/index.html) to Vercel and connect it to a public FastAPI backend (HTTP + WebSocket). It covers both the Git import flow and the CLI flow, plus backend notes (CORS, WSS) needed for the demo to work in production.

## Prerequisites

- A GitHub repository containing this project (demo files are under `demo/web`).
- A Vercel account (https://vercel.com).
- A publicly accessible backend URL (HTTPS + WSS) that runs `server.app:app` (FastAPI). See "Backend hosting" below.

## 1. Push the demo to GitHub

From the repository root, commit and push the demo files:

```bash
git add demo/web demo/README.md demo/DEPLOY_VERCEL.md
git commit -m "Add browser demo and Vercel deploy guide"
git push origin main
```

## 2. Deploy with Vercel (Git import)

1. Open https://vercel.com and click **New Project → Import Git Repository**.
2. Select your GitHub repo and on the import options set:
   - **Root Directory**: `demo/web`
   - **Framework Preset**: Other (Static Site)
   - **Build Command**: (leave blank)
   - **Output Directory**: (leave blank)
3. Click **Deploy**. Vercel will serve the static files and give you a URL like `https://<project>.vercel.app`.

## 3. Deploy with Vercel CLI (alternative)

From the repo root (or `demo/web`) you can use the Vercel CLI:

```bash
cd demo/web
npm i -g vercel
vercel login
vercel --prod
```

Follow the prompts and note the production URL returned by Vercel.

## 4. Point the UI at your backend

- The demo UI reads the backend URL from the **Server base URL** input at runtime. After the site is deployed, open the page and set the Server base URL to your backend (for example `https://api.example.com`).
- To bake a default backend URL into the deployed site, edit the input `value` in [demo/web/index.html](demo/web/index.html):

```html
<input id="serverUrl" value="https://api.example.com" style="width:260px">
```

Commit and push the change so the deployed site defaults to your backend.

## 5. Backend hosting (recommended)

The demo requires a publicly reachable FastAPI server that supports WebSocket upgrades. Common options:

- **Render**: Create a Web Service, build with `pip install -r requirements.txt`, start with:
  ```bash
  gunicorn -k uvicorn.workers.UvicornWorker server.app:app
  ```
- **Railway / Fly / Heroku**: Deploy the repo, set the start command to:
  ```bash
  uvicorn server.app:app --host 0.0.0.0 --port $PORT
  ```

Minimal `requirements.txt` example (put this in repo root if you plan to deploy backend):

```
fastapi
uvicorn[standard]
httpx
gunicorn
```

## 6. CORS and WebSocket notes

- Ensure your backend allows the deployed Vercel origin to access HTTP + WebSocket. Example FastAPI CORS middleware (add to `server/app.py`):

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

- If you use `allow_origins=["*"]` this is convenient for testing but not recommended for production.
- When the backend is HTTPS, the demo will use `wss://` automatically for WebSocket connections.

## 7. Verify the demo

1. Open your Vercel URL (e.g. `https://<project>.vercel.app`).
2. Set **Server base URL** to your backend (e.g. `https://api.example.com`).
3. Create a room, join as two players (two browser tabs or different names), open WebSocket(s), and click **Start Hand**.
4. Use the **Send Call** and **Force Timeout** buttons to simulate actions and observe events.

If messages do not appear, check the browser console and the backend logs for CORS or WebSocket handshake errors.

## 8. Troubleshooting

- **CORS errors**: Add the correct origin to `allow_origins` in the FastAPI CORS middleware.
- **WSS handshake failures**: Ensure the backend is served over HTTPS and the proxy supports WebSocket upgrades.
- **Backend unreachable**: Confirm the backend URL is accessible from the internet and not blocked by firewall.

## 9. Optional improvements

- Pre-fill `serverUrl` from an environment variable at build time (requires a build step).
- Add authentication, rate-limiting, and TLS certificates for production readiness.
- Add a tiny serverless function or config endpoint that returns the correct backend URL for the deployed frontend.

---

If you want, I can:

- Prefill the `serverUrl` in [demo/web/index.html](demo/web/index.html) with a placeholder (I will commit that change), and/or
- Add the CORS middleware snippet to `server/app.py` and create a minimal `requirements.txt` to simplify deploying the backend.

Tell me which of those you'd like me to do and I will apply the changes.
