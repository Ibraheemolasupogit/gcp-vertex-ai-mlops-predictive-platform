#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-gcp-vertex-ai-mlops-predictive-platform:local}"
CONTAINER_NAME="${CONTAINER_NAME:-gcp-vertex-ai-mlops-api-local}"
HOST_PORT="${HOST_PORT:-8080}"
CONTAINER_PORT="${PORT:-8080}"

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
container_id="$(
  docker run \
  --detach \
  --name "${CONTAINER_NAME}" \
  -e PORT="${CONTAINER_PORT}" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  "${IMAGE_NAME}"
)"

echo "Started container: ${CONTAINER_NAME} (${container_id})"
echo "Local API URL: http://127.0.0.1:${HOST_PORT}"
