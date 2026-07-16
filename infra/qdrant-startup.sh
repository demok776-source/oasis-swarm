#!/bin/bash
# GCE VM startup script for the Qdrant Memory Fabric instance.
# Referenced by infra/terraform/main.tf (google_compute_instance.qdrant_vm
# metadata_startup_script). This file was missing entirely -- `terraform
# apply` would fail immediately with a "no such file" error trying to read
# it via the file() function. Runs automatically on first boot (and every
# reboot) via GCE's startup-script mechanism.
set -euo pipefail

apt-get update -y
apt-get install -y docker.io
systemctl enable docker
systemctl start docker

# Persistent storage for Qdrant's data dir lives on the boot disk under
# /var/lib/qdrant-storage; survives container restarts (not VM re-creation --
# for that, use a separate persistent disk + gcloud compute disks attach).
mkdir -p /var/lib/qdrant-storage

docker run -d \
  --name qdrant \
  --restart unless-stopped \
  -p 6333:6333 \
  -p 6334:6334 \
  -v /var/lib/qdrant-storage:/qdrant/storage \
  qdrant/qdrant:latest

echo "Qdrant container started. Verify with: curl http://localhost:6333/collections"
