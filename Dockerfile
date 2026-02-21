# Multi-stage: Option A — backend serves frontend static files (PRD deployment)
# Stage 1: build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci 2>/dev/null || npm install
COPY frontend/ .
# Same-origin API when served from backend
ENV VITE_API_BASE_URL=
RUN npm run build

# Stage 2: backend + serve frontend
FROM python:3.11-slim
WORKDIR /app

# Non-root user
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --shell /bin/false app

# Backend deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY backend/ backend/

# Frontend static (from stage 1)
COPY --from=frontend-build /app/frontend/dist frontend/dist

# Ensure backend can write to data dirs if needed
RUN mkdir -p backend/logs backend/data && chown -R app:app /app

USER app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
