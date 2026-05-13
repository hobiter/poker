# Deploy to Fly.io (single-container backend + built frontend)

This guide shows how to deploy the combined backend (FastAPI) and built frontend
to Fly.io using the repo's multi-stage `Dockerfile`. The Dockerfile builds the
Vite frontend and copies `frontend/dist` into the Python image so a single
container serves both API + static SPA, which keeps the same origin for WebSocket
connections (recommended).

Prerequisites
- A Fly.io account: https://fly.io
- `flyctl` installed (see below) and authenticated
- Docker (optional: local build) or allow Fly to build remotely

Install `flyctl`

macOS / Linux (curl):

```bash
curl -L https://fly.io/install.sh | sh
```

Windows (PowerShell / Scoop / Winget):

See https://fly.io/docs/hands-on/install-flyctl/ for platform-specific options.

Login

```bash
flyctl auth login
```

Create / initialize an app

From the repository root run an initial launch (this creates `fly.toml`).

```bash
flyctl launch --name poker --region ord --dockerfile ./Dockerfile --no-deploy
```

- `--no-deploy` prevents an immediate deploy so you can adjust `fly.toml` first.
- pick `--region` nearest your users (e.g. `ord`, `iad`, `fra`, `lon`, etc.).

Set the frontend backend URL build arg

Because the Dockerfile performs a production Vite build inside the image, the
frontend's `VITE_SERVER_URL` must be available at build time if you want the
SPA to default to your deployed backend host. Two ways to provide this:

1) Add build args to `fly.toml` (recommended for repeated deployments). Edit
   the generated `fly.toml` and add a `build.args` table:

```toml
[build]
  image = ""

[build.args]
  VITE_SERVER_URL = "https://poker.fly.dev"
```

Replace `https://poker.fly.dev` with your chosen app hostname. Then deploy:

```bash
flyctl deploy
```

2) Or pass a build arg directly on deploy (one-off):

```bash
flyctl deploy --build-arg VITE_SERVER_URL="https://poker.fly.dev"
```

Note: initially the app hostname may not exist until the first deploy. You can
use a placeholder like `https://example.com` for the first build, then set the
proper `VITE_SERVER_URL` and redeploy.

Deploy (remote or local build)

- Remote build (Fly builds your image in the cloud):

```bash
flyctl deploy --remote-only
```

- Local build (builds image locally and pushes):

```bash
flyctl deploy
```

Set runtime secrets / env (optional)

If you have runtime secrets (DB credentials, API keys), set them with:

```bash
flyctl secrets set DATABASE_URL=postgres://... OTHER_KEY=value
```

These are available as environment variables at runtime. Note that secrets are
not used for Vite build-time substitution — build args above are used for that.

Verify and watch logs

```bash
flyctl open -a poker
flyctl logs -a poker -t
```

Tips and notes

- WebSocket support: Fly allows long-lived TCP connections and WebSockets. If
  your app serves both SPA + WebSocket API from the same hostname (the
  multi-stage Dockerfile pattern), client code can use same-origin `wss://`
  connections without CORS issues.
- Port handling: Fly provides a `$PORT` env var. The Dockerfile in this repo
  uses `uvicorn ... --port 8000` by default; if you prefer to follow Fly's
  `$PORT` convention, change the `CMD` in `Dockerfile` to:

```dockerfile
CMD sh -lc "uvicorn server.app:app --host 0.0.0.0 --port ${PORT:-8000}"
```

- If you need to change the app hostname, update `VITE_SERVER_URL` and
  re-deploy the image so the built frontend uses the new URL.
- To scale instances:

```bash
flyctl scale count 2 -a poker
```

Rollback / redeploy

```bash
flyctl deploy -a poker
```

Troubleshooting

- If the SPA cannot connect to WebSocket, verify that the `VITE_SERVER_URL`
  uses `https://...` and that the backend is reachable on `wss://` for
  WebSocket upgrades.
- If the frontend still shows `localhost` after deploy, you likely built the
  image without setting the build arg; set `VITE_SERVER_URL` and re-deploy.

Advanced: automatic CI deploy

You can wire `flyctl` into your CI (GitHub Actions) so every merge triggers a
deploy. Use `flyctl deploy --remote-only --config fly.toml` in a workflow and
set `FLY_API_TOKEN` as a secret in your repo (create via `flyctl auth token`).

References
- Fly docs: https://fly.io/docs/
- `flyctl` CLI reference: https://fly.io/docs/reference/cli/
