#!/bin/bash
# Creates the OASIS Memory Fabric collections in Qdrant.
# Referenced in infra/README.md step 4 but the script itself was missing.
#
# ingest.py (infra/ingest.py) upserts points directly with no
# create_collection call of its own -- it assumes these collections
# already exist. Run this once, right after the Qdrant VM is up, before
# the first `python3 ingest.py` call.
#
# Usage: bash qdrant-collections.sh <QDRANT_IP>
set -euo pipefail

QDRANT_IP="${1:?Usage: bash qdrant-collections.sh <QDRANT_IP>}"
QDRANT_URL="http://${QDRANT_IP}:6333"
VECTOR_SIZE=1536  # matches EMBED_DIM in infra/ingest.py (OpenAI text-embedding-3-small)

COLLECTIONS=(oasis_docs oasis_code oasis_notes oasis_projects)

echo "Waiting for Qdrant at ${QDRANT_URL} to respond..."
for i in $(seq 1 30); do
  if curl -sf "${QDRANT_URL}/collections" > /dev/null 2>&1; then
    break
  fi
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "Qdrant never came up at ${QDRANT_URL} -- check the VM / firewall rules." >&2
    exit 1
  fi
done

for name in "${COLLECTIONS[@]}"; do
  echo "Creating collection: ${name}"
  curl -sf -X PUT "${QDRANT_URL}/collections/${name}" \
    -H "Content-Type: application/json" \
    -d "{
      \"vectors\": {
        \"size\": ${VECTOR_SIZE},
        \"distance\": \"Cosine\"
      },
      \"hnsw_config\": {
        \"m\": 16,
        \"ef_construct\": 100
      },
      \"quantization_config\": {
        \"scalar\": {
          \"type\": \"int8\",
          \"quantile\": 0.99,
          \"always_ram\": true
        }
      }
    }" && echo "  OK" || echo "  (already exists or failed -- check manually)"
done

echo ""
echo "Verifying collections:"
curl -s "${QDRANT_URL}/collections" | python3 -m json.tool
