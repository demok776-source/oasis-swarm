#!/bin/bash
# OASIS SYSTEM CORE -- GCP deploy script.
#
# This provisions everything infra/terraform/main.tf does NOT manage: API
# enablement, Artifact Registry, the GCS asset bucket, the BigQuery
# analytics dataset, and the full Global HTTPS Load Balancer chain in front
# of Cloud Run (reserved IP -> managed SSL cert -> serverless NEG ->
# backend service -> URL map -> target HTTPS proxy -> forwarding rule).
# Terraform-managed resources (Cloud SQL, the Cloud Run app-tier service,
# the Qdrant VM, the Redis VM) are applied via `terraform apply` as step 4.
#
# Required env vars (see infra/README.md step 1):
#   DB_USER, DB_PASS, DB_NAME, OPENAI_API_KEY
#
# Usage: bash deploy.sh 2>&1 | tee deploy.log
set -euo pipefail

: "${DB_USER:?Set DB_USER first (see infra/README.md step 1)}"
: "${DB_PASS:?Set DB_PASS first}"
: "${DB_NAME:?Set DB_NAME first}"
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY first}"

PROJECT_ID="project-f537c014-8ae2-4195-9f3"
REGION="europe-west1"
ZONE="europe-west1-b"
DOMAIN="oasis-system-core.com"
REPO_NAME="app-tier-repo"
BUCKET_NAME="assets-bucket-${PROJECT_ID}"
BQ_DATASET="analytics_warehouse"

echo "=== [1/22] Setting gcloud project ==="
gcloud config set project "${PROJECT_ID}"

echo "=== [2/22] Enabling required APIs ==="
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  monitoring.googleapis.com

echo "=== [3/22] Storing DB credentials in Secret Manager ==="
printf '%s' "${DB_PASS}" | gcloud secrets create oasis-db-password --data-file=- 2>/dev/null \
  || printf '%s' "${DB_PASS}" | gcloud secrets versions add oasis-db-password --data-file=-
printf '%s' "${OPENAI_API_KEY}" | gcloud secrets create oasis-openai-key --data-file=- 2>/dev/null \
  || printf '%s' "${OPENAI_API_KEY}" | gcloud secrets versions add oasis-openai-key --data-file=-

echo "=== [4/22] Terraform apply (Cloud SQL, Cloud Run app-tier, Qdrant VM, Redis VM) ==="
(cd "$(dirname "$0")/terraform" && terraform init && terraform apply -auto-approve \
    -var="db_user=${DB_USER}" -var="db_name=${DB_NAME}" 2>/dev/null || terraform apply -auto-approve)

echo "=== [5/22] Creating Artifact Registry repo ==="
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="OASIS SYSTEM CORE container images" 2>/dev/null || echo "  (already exists)"

echo "=== [6/22] Creating GCS asset bucket ==="
gcloud storage buckets create "gs://${BUCKET_NAME}" \
  --project="${PROJECT_ID}" --location="${REGION}" --uniform-bucket-level-access 2>/dev/null \
  || echo "  (already exists)"

echo "=== [7/22] Creating BigQuery analytics dataset ==="
bq mk --project_id="${PROJECT_ID}" --location=EU "${BQ_DATASET}" 2>/dev/null || echo "  (already exists)"

echo "=== [8/22] Reserving global static IP ==="
gcloud compute addresses create oasis-ip --global 2>/dev/null || echo "  (already exists)"
GLOBAL_IP=$(gcloud compute addresses describe oasis-ip --global --format="value(address)")
echo "  Global IP: ${GLOBAL_IP}"

echo "=== [9/22] Requesting managed SSL certificate ==="
gcloud compute ssl-certificates create oasis-cert \
  --domains="${DOMAIN},www.${DOMAIN}" --global 2>/dev/null || echo "  (already exists)"

echo "=== [10/22] Getting Cloud Run service URL ==="
CR_URL=$(gcloud run services describe app-tier --region="${REGION}" --format="value(status.url)")
echo "  Cloud Run URL: ${CR_URL}"

echo "=== [11/22] Creating Serverless NEG for app-tier ==="
gcloud compute network-endpoint-groups create app-tier-neg \
  --region="${REGION}" --network-endpoint-type=serverless \
  --cloud-run-service=app-tier 2>/dev/null || echo "  (already exists)"

echo "=== [12/22] Creating backend service ==="
gcloud compute backend-services create app-tier-backend \
  --global --load-balancing-scheme=EXTERNAL_MANAGED 2>/dev/null || echo "  (already exists)"
gcloud compute backend-services add-backend app-tier-backend \
  --global --network-endpoint-group=app-tier-neg \
  --network-endpoint-group-region="${REGION}" 2>/dev/null || echo "  (backend already attached)"

echo "=== [13/22] Creating URL map ==="
gcloud compute url-maps create oasis-map \
  --default-service=app-tier-backend 2>/dev/null || echo "  (already exists)"

echo "=== [14/22] Creating target HTTPS proxy ==="
gcloud compute target-https-proxies create oasis-proxy \
  --url-map=oasis-map --ssl-certificates=oasis-cert 2>/dev/null || echo "  (already exists)"

echo "=== [15/22] Creating global forwarding rule ==="
gcloud compute forwarding-rules create oasis-https-rule \
  --address=oasis-ip --global \
  --target-https-proxy=oasis-proxy --ports=443 2>/dev/null || echo "  (already exists)"

echo "=== [16/22] Reading Qdrant VM external IP ==="
QDRANT_IP=$(gcloud compute instances describe qdrant-memory-fabric --zone="${ZONE}" \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
echo "  Qdrant VM IP: ${QDRANT_IP}"

echo "=== [17/22] Reading Redis VM external IP ==="
REDIS_IP=$(gcloud compute instances describe redis-sync-layer --zone="${ZONE}" \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
echo "  Redis VM IP: ${REDIS_IP}"

echo "=== [18/22] Building ws-proxy image ==="
docker build -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/ws-proxy:latest" "$(dirname "$0")/ws-proxy/"
docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/ws-proxy:latest"

echo "=== [19/22] Deploying ws-proxy Cloud Run service ==="
sed "s/PROJECT_ID/${PROJECT_ID}/g" "$(dirname "$0")/ws-proxy-service.yaml" > /tmp/ws-proxy-service.rendered.yaml
gcloud run services replace /tmp/ws-proxy-service.rendered.yaml --region="${REGION}"

echo "=== [20/22] Importing monitoring dashboard ==="
gcloud monitoring dashboards create \
  --config-from-file="$(dirname "$0")/monitoring-dashboard.json" \
  --project="${PROJECT_ID}" 2>/dev/null || echo "  (already exists -- update manually if changed)"

echo "=== [21/22] Writing deploy manifest (IPs/URLs for later steps) ==="
cat > "$(dirname "$0")/.deploy-manifest.env" <<MANIFEST
GLOBAL_IP=${GLOBAL_IP}
QDRANT_IP=${QDRANT_IP}
REDIS_IP=${REDIS_IP}
CR_URL=${CR_URL}
MANIFEST
echo "  Wrote $(dirname "$0")/.deploy-manifest.env"

echo "=== [22/22] Done ==="
echo ""
echo "Next steps:"
echo "  1. Point DNS: A ${DOMAIN} -> ${GLOBAL_IP}  (and www.${DOMAIN})"
echo "  2. bash qdrant-collections.sh ${QDRANT_IP}"
echo "  3. bash validate.sh ${QDRANT_IP} ${REDIS_IP} ${CR_URL} ${DOMAIN}"
