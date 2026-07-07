# PreStocks Deployment Guide

## Phase 2: GCP Cloud Run Deployment

### Architecture (Production)

```
                    ┌─────────────┐
                    │  Cloud CDN  │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ Cloud Load  │
                    │  Balancer   │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────┴────┐  ┌─────┴─────┐  ┌────┴────────┐
    │  Frontend  │  │    API    │  │   Celery    │
    │ Cloud Run  │  │ Cloud Run │  │  Cloud Run  │
    │ (Next.js)  │  │ (FastAPI) │  │  (Workers)  │
    └────────────┘  └─────┬─────┘  └──────┬──────┘
                          │                │
                ┌─────────┴────┐    ┌──────┴──────┐
                │  CloudSQL    │    │  Memorystore│
                │ (PostgreSQL) │    │   (Redis)   │
                └──────────────┘    └─────────────┘
```

### Prerequisites

1. GCP Project created
2. `gcloud` CLI installed and authenticated
3. Docker images pushed to Artifact Registry
4. Domain name configured

### Step 1: Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Create CloudSQL Instance

```bash
gcloud sql instances create prestocks-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-size=10GB \
  --storage-auto-increase

gcloud sql databases create prestocks --instance=prestocks-db

gcloud sql users create prestocks \
  --instance=prestocks-db \
  --password="$(openssl rand -base64 32)"
```

### Step 3: Create Memorystore (Redis)

```bash
gcloud redis instances create prestocks-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Step 4: Push Docker Images

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/prestocks/api:latest ./backend
docker push us-central1-docker.pkg.dev/PROJECT_ID/prestocks/api:latest

docker build -t us-central1-docker.pkg.dev/PROJECT_ID/prestocks/frontend:latest ./frontend
docker push us-central1-docker.pkg.dev/PROJECT_ID/prestocks/frontend:latest
```

### Step 5: Deploy API to Cloud Run

```bash
gcloud run deploy prestocks-api \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/prestocks/api:latest \
  --region=us-central1 \
  --platform=managed \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=10 \
  --port=8000 \
  --set-env-vars="DEBUG=false" \
  --set-secrets="DATABASE_URL=prestocks-db-url:latest,JWT_SECRET_KEY=jwt-secret:latest,ANTHROPIC_API_KEY=anthropic-key:latest" \
  --add-cloudsql-instances=PROJECT_ID:us-central1:prestocks-db \
  --allow-unauthenticated
```

### Step 6: Deploy Frontend to Cloud Run

```bash
gcloud run deploy prestocks-frontend \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/prestocks/frontend:latest \
  --region=us-central1 \
  --platform=managed \
  --memory=256Mi \
  --min-instances=1 \
  --max-instances=5 \
  --port=3000 \
  --set-env-vars="NEXT_PUBLIC_API_BASE_URL=https://prestocks-api-xxxxx.run.app" \
  --allow-unauthenticated
```

### Step 7: Deploy Celery Workers

```bash
gcloud run jobs create prestocks-celery-worker \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/prestocks/api:latest \
  --region=us-central1 \
  --command="celery,-A,app.celery_app,worker,--loglevel=warning" \
  --memory=512Mi \
  --set-secrets="DATABASE_URL=prestocks-db-url:latest"
```

### Step 8: Set Up Cloud Scheduler (replaces Celery Beat)

```bash
# Price updates every minute
gcloud scheduler jobs create http update-prices \
  --schedule="* * * * *" \
  --uri="https://prestocks-api-xxxxx.run.app/internal/tasks/update-prices" \
  --http-method=POST

# Flag calculations every 5 minutes
gcloud scheduler jobs create http calculate-flags \
  --schedule="*/5 * * * *" \
  --uri="https://prestocks-api-xxxxx.run.app/internal/tasks/calculate-flags" \
  --http-method=POST

# News ingestion hourly
gcloud scheduler jobs create http ingest-news \
  --schedule="0 * * * *" \
  --uri="https://prestocks-api-xxxxx.run.app/internal/tasks/ingest-news" \
  --http-method=POST
```

### Step 9: Custom Domain

```bash
gcloud run domain-mappings create \
  --service=prestocks-frontend \
  --domain=prestocks.app \
  --region=us-central1
```

### Monitoring & Observability

- **Cloud Logging**: Automatically captures stdout/stderr from Cloud Run
- **Cloud Monitoring**: Set up alerts for:
  - API latency > 500ms
  - Error rate > 5%
  - Memory utilization > 80%
- **Uptime Checks**: Monitor `/health` endpoint every 60s

### Cost Estimate (Development/Low Traffic)

| Service | Estimate/Month |
|---------|---------------|
| Cloud Run (API) | $15-30 |
| Cloud Run (Frontend) | $10-20 |
| CloudSQL (micro) | $25 |
| Memorystore (1GB) | $35 |
| Cloud Scheduler | $1 |
| **Total** | **~$90-110/mo** |

### Security Checklist

- [ ] JWT secret stored in Secret Manager
- [ ] Database password in Secret Manager
- [ ] API keys (Anthropic, Finnhub) in Secret Manager
- [ ] CloudSQL only accessible from Cloud Run (VPC)
- [ ] Redis only accessible from Cloud Run (VPC)
- [ ] CORS configured for production domain only
- [ ] Rate limiting on auth endpoints
- [ ] HTTPS enforced on all endpoints
