# Deployment (Docker)

This app runs as a single Docker image (backend + built frontend) with PostgreSQL.

## Prerequisites

- Docker and Docker Compose
- (Optional) S3-compatible bucket for file uploads

## Quick start

1. **Copy env and configure**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least:

   - `JWT_SECRET_KEY` — use a long random secret in production
   - `GROQ_API_KEY` — for AI recommendations (optional but recommended)
   - For Docker Compose, `POSTGRES_PASSWORD` and `POSTGRES_DB` are used by the Postgres service; `DATABASE_URL` is built automatically for the backend (points to `postgres:5432`).
   - **Production:** Set `DATA_ENCRYPTION_KEY` (base64 32-byte key) for encryption at rest. Generate: `python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"`. See [ENCRYPTION.md](./ENCRYPTION.md).

2. **Start stack**

   ```bash
   docker compose up -d
   ```

3. **Open the app**

   - App (API + frontend): [http://localhost:8000](http://localhost:8000)
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## S3 / database

- **PostgreSQL:** Started by Compose with a persistent volume. No extra setup required.
- **S3:** If you use uploads, create the bucket and set `S3_BUCKET`, `S3_REGION`, and credentials (`S3_ACCESS_KEY` / `S3_SECRET_KEY` or `ACCESS_KEY` / `SECRET_ACCESS_KEY`) in `.env`. Leave them empty to run without S3.

## Build only

```bash
docker compose build
```

## Logs

```bash
docker compose logs -f backend
docker compose logs -f postgres
```

## Shutdown

```bash
docker compose down
```

Add `-v` to remove volumes (database and ChromaDB data).

---

## HTTPS/TLS (production)

Encryption in transit is handled by the deployment environment, not the app itself. The app does not implement TLS.

**For production, use HTTPS:**

1. **Reverse proxy (recommended)** — Run nginx, Caddy, or Traefik in front of the app:
   - Terminate TLS at the proxy (e.g. Let’s Encrypt certificates)
   - Proxy HTTP to `localhost:8000` or the backend container
   - Example (Caddy): `reverse_proxy localhost:8000` with automatic HTTPS

2. **Load balancer** — On AWS/GCP/Azure, use the platform’s load balancer with TLS termination and forward to the backend on HTTP.

3. **TLS on the app** — Optionally configure Uvicorn with SSL certs, but a reverse proxy is usually easier to manage.

See [ENCRYPTION.md](./ENCRYPTION.md) for details.

---

## Production checklist

Before going to production:

- [ ] Set a strong `JWT_SECRET_KEY` (long random string)
- [ ] Set `DATA_ENCRYPTION_KEY` for encryption at rest (see ENCRYPTION.md)
- [ ] Use managed PostgreSQL (RDS, Cloud SQL, etc.) instead of the Postgres container; update `DATABASE_URL`
- [ ] Enable HTTPS/TLS (reverse proxy or load balancer)
- [ ] Set `CORS_ALLOW_ORIGINS` to your production domain(s)
- [ ] Configure S3 credentials if using uploads
- [ ] Use secrets management (e.g. AWS Secrets Manager) instead of `.env` for sensitive values

---

## Cloud deployment

To deploy to a cloud platform:

1. **Build and tag the image**

   ```bash
   docker compose build
   docker tag fin-scenario-map-backend <registry>/fin-scenario-map:latest
   ```

2. **Push to a container registry**

   ```bash
   docker push <registry>/fin-scenario-map:latest
   ```

   Registries: Docker Hub, AWS ECR, Google GCR, Azure ACR.

3. **Deploy the image**

   - **AWS:** ECS, EKS, App Runner, or EC2
   - **GCP:** Cloud Run, GKE, or Compute Engine
   - **Azure:** Container Apps, AKS, or App Service
   - **Railway / Render / Fly.io:** Connect repo or push image

4. **Configure** the service with:
   - `DATABASE_URL` (managed Postgres)
   - `JWT_SECRET_KEY`, `DATA_ENCRYPTION_KEY`
   - `GROQ_API_KEY` (optional)
   - S3 env vars if using uploads

5. **Expose** port 8000 and ensure HTTPS at the edge (load balancer or platform TLS).
