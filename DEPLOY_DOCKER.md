# Deploy with Docker Compose

This project includes a `Dockerfile` for the backend, a `Dockerfile` for the frontend, and `docker-compose.yml` to run both locally or in a container host.

Build and run locally:

```bash
# from repo root
docker compose build
docker compose up
```

- Backend will be available at `http://localhost:8000`.
- Frontend (static site served by nginx) will be available at `http://localhost:5173`.

To publish, build the images and push to your container registry and deploy to your cloud provider (Render, Fly.io, Docker Cloud, etc.).
