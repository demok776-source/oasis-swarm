#!/bin/bash
# Post-deploy health check across every component in the documented
# architecture (infra/README.md). Referenced in step 8 but the script
# itself was missing from the repo.
#
# Usage: bash validate.sh <QDRANT_IP> <REDIS_IP> <CR_URL> <DOMAIN>
set -uo pipefail  # deliberately NOT -e: we want to run every check and
                  # report a full summary even if one component is down.

QDRANT_IP="${1:?Usage: bash validate.sh <QDRANT_IP> <REDIS_IP> <CR_URL> <DOMAIN>}"
REDIS_IP="${2:?Missing REDIS_IP}"
CR_URL="${3:?Missing CR_URL}"
DOMAIN="${4:?Missing DOMAIN}"

PASS=0
FAIL=0

check() {
  local name="$1"
  local result="$2"
  if [ "$result" = "0" ]; then
    echo "  [OK]   ${name}"
    PASS=$((PASS + 1))
  else
    echo "  [FAIL] ${name}"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== 1. Qdrant (${QDRANT_IP}:6333) ==="
curl -sf -m 5 "http://${QDRANT_IP}:6333/collections" > /tmp/qdrant_check.json
check "Qdrant /collections responds" "$?"
if [ -f /tmp/qdrant_check.json ]; then
  COUNT=$(python3 -c "import json; print(len(json.load(open('/tmp/qdrant_check.json'))['result']['collections']))" 2>/dev/null || echo "?")
  echo "  -> ${COUNT} collections present (expect 4: oasis_docs, oasis_code, oasis_notes, oasis_projects)"
fi

echo "=== 2. Redis (${REDIS_IP}:6379) ==="
if command -v redis-cli > /dev/null 2>&1; then
  PING_RESULT=$(redis-cli -h "${REDIS_IP}" -p 6379 --no-raw ping 2>/dev/null)
  if [ "$PING_RESULT" = "PONG" ]; then
    check "Redis PING -> PONG" 0
  else
    check "Redis PING -> PONG" 1
  fi
else
  echo "  redis-cli not installed (apt-get install redis-tools) -- skipping"
fi

echo "=== 3. Cloud Run app-tier (${CR_URL}) ==="
curl -sf -m 10 "${CR_URL}/health" > /tmp/health_check.json
check "GET /health returns 2xx" "$?"
cat /tmp/health_check.json 2>/dev/null

echo "=== 4. Cloud Run app-tier telemetry (${CR_URL}/health/telemetry) ==="
curl -sf -m 10 "${CR_URL}/health/telemetry" > /tmp/telemetry_check.json
check "GET /health/telemetry returns 2xx" "$?"
cat /tmp/telemetry_check.json 2>/dev/null

echo "=== 5. Public domain over HTTPS (https://${DOMAIN}) ==="
curl -sf -m 10 -o /dev/null -w "  HTTP status: %{http_code}\n" "https://${DOMAIN}/health"
check "https://${DOMAIN}/health reachable" "$?"

echo ""
echo "=== Summary: ${PASS} passed, ${FAIL} failed ==="
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
