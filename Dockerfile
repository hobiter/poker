### Multi-stage image: build frontend with Node, then run backend with Python
FROM node:20-alpine AS frontend-builder
WORKDIR /tmp/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Copy the python app
COPY . .
# Copy built frontend into the Python image so FastAPI can serve it
COPY --from=frontend-builder /tmp/frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
