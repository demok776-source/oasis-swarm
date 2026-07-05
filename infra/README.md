# OASIS SYSTEM CORE — GCP Infrastructure

Project: `project-f537c014-8ae2-4195-9f3`  
Region: `europe-west1`  
Domain: `oasis-system-core.com`

## Files

| File | Purpose |
|------|---------|
| `deploy.sh` | Main deploy — runs all 22 steps |
| `qdrant-startup.sh` | Auto-runs on Qdrant VM first boot |
| `redis-startup.sh` | Auto-runs on Redis VM first boot |
| `qdrant-collections.sh` | Creates Memory Fabric collections |
| `ingest.py` | Document → Qdrant ingestion pipeline |
| `validate.sh` | Post-deploy health check |
| `nginx-ws.conf` | WebSocket proxy nginx config |
| `ws-proxy-service.yaml` | Cloud Run WebSocket proxy manifest |
| `monitoring-dashboard.json` | GCP Monitoring dashboard |

---

## Prerequisites

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
gcloud auth login
gcloud auth application-default login

# Install redis-cli (for validation)
apt-get install redis-tools  # or brew install redis
```

---

## Deploy — Step by Step

### 1. Set credentials and secrets
```bash
export DB_USER="oasis_user"
export DB_PASS="your_strong_password_here"
export DB_NAME="oasis_db"
export OPENAI_API_KEY="sk-..."  # for Memory Fabric ingestion
```

### 2. Run main deploy
```bash
chmod +x deploy.sh
bash deploy.sh 2>&1 | tee deploy.log
```

This takes ~10-15 minutes (Cloud SQL creation is the bottleneck).

### 3. Set DNS
After deploy completes, note the Global IP and set:
```
A     oasis-system-core.com     →  <GLOBAL_IP>
A     www.oasis-system-core.com →  <GLOBAL_IP>
```

### 4. Create Qdrant collections (Memory Fabric)
```bash
# Get Qdrant IP from deploy output, then:
bash qdrant-collections.sh <QDRANT_IP>
```

### 5. Ingest documents
```bash
# Ingest your project docs
python3 ingest.py \
  --qdrant http://<QDRANT_IP>:6333 \
  --collection oasis_docs \
  --path ./your-docs/ \
  --module oasis_prime

# Ingest code
python3 ingest.py \
  --qdrant http://<QDRANT_IP>:6333 \
  --collection oasis_code \
  --path ./your-code/ \
  --module jarvis
```

### 6. Deploy real JARVIS image
```bash
# Build and push your image
docker build -t europe-west1-docker.pkg.dev/project-f537c014-8ae2-4195-9f3/app-tier-repo/jarvis:latest .
docker push europe-west1-docker.pkg.dev/project-f537c014-8ae2-4195-9f3/app-tier-repo/jarvis:latest

# Redeploy Cloud Run with real image
gcloud run deploy app-tier \
  --image=europe-west1-docker.pkg.dev/project-f537c014-8ae2-4195-9f3/app-tier-repo/jarvis:latest \
  --region=europe-west1 \
  --project=project-f537c014-8ae2-4195-9f3
```

### 7. Import monitoring dashboard
```bash
gcloud monitoring dashboards create \
  --config-from-file=monitoring-dashboard.json \
  --project=project-f537c014-8ae2-4195-9f3
```

### 8. Validate everything
```bash
bash validate.sh <QDRANT_IP> <REDIS_IP> <CR_URL> oasis-system-core.com
```

---

## Architecture

```
Internet
   │
   ▼
Global LB (oasis-ip) :443
   │   SSL: oasis-cert (managed)
   │   URL Map: oasis-map
   │
   ▼
HTTPS Proxy (oasis-proxy)
   │
   ▼
Backend Service (app-tier-backend)
   │
   ▼
Serverless NEG (app-tier-neg)
   │
   ▼
Cloud Run (app-tier) ──── Cloud SQL Auth Proxy ──── PostgreSQL 15 (primary-db)
   │                                                      europe-west1
   │
   ├── Qdrant VM (e2-medium, 20GB SSD)
   │   └── Memory Fabric: oasis_docs, oasis_code, oasis_notes, oasis_projects
   │
   └── Redis VM (e2-micro, 10GB)
       └── Sync Layer: pub/sub event bus

Storage: gs://assets-bucket-project-f537c014-8ae2-4195-9f3
BigQuery: analytics_warehouse (EU)
Artifact Registry: europe-west1-docker.pkg.dev/project-f537c014-8ae2-4195-9f3/app-tier-repo
```

---

## Monthly Cost Estimate

| Resource | Type | Est. Cost |
|----------|------|-----------|
| Cloud Run | 1-3 replicas | ~$5-20 |
| Cloud SQL | db-f1-micro | ~$7 |
| Qdrant VM | e2-medium | ~$26 |
| Redis VM | e2-micro | ~$6 |
| Load Balancer | Global HTTPS | ~$18 |
| Storage | 20GB Standard | ~$1 |
| BigQuery | Storage only | ~$1 |
| **Total** | | **~$64-80/mo** |

To reduce costs: stop Qdrant/Redis VMs when not in use, or use preemptible instances.
