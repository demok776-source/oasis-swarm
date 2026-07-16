#!/bin/bash
# GCE VM startup script for the Redis Sync Layer instance (e2-micro, per
# infra/README.md's documented architecture). Runs on first boot via GCE's
# startup-script mechanism, same pattern as qdrant-startup.sh.
set -euo pipefail

apt-get update -y
apt-get install -y docker.io
systemctl enable docker
systemctl start docker

mkdir -p /var/lib/redis-storage

# --appendonly yes: durability across container restarts. This is a
# single-node Sync Layer event bus, not a cache -- losing pub/sub history on
# every crash would silently break the DB-fallback reconciliation path in
# app-tier/src/main.py.
docker run -d \
  --name redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v /var/lib/redis-storage:/data \
  redis:7-alpine \
  redis-server --appendonly yes

echo "Redis container started. Verify with: redis-cli -h localhost ping"
