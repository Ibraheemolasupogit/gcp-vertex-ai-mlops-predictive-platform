#!/usr/bin/env bash
set -euo pipefail

# Dry-run helper only. This script does not call Cloud Run or Vertex AI.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_PROJECT_ID
  VERTEX_ENDPOINT_REGION
  VERTEX_ENDPOINT_ID
  SERVICE_NAME
  PORT
  PREDICTION_MODE
  ENABLE_VERTEX_PROXY
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/cloud_run_vertex_proxy.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

service_url="${CLOUD_RUN_URL:-https://SERVICE_URL_PLACEHOLDER}"

echo "Cloud Run to Vertex AI proxy dry run."
echo "Expected Cloud Run service: ${SERVICE_NAME}"
echo "Expected serving mode: ${PREDICTION_MODE}"
echo "Vertex proxy enabled flag: ${ENABLE_VERTEX_PROXY}"
echo
echo "Expected runtime environment variables:"
echo "  PREDICTION_MODE=vertex_endpoint"
echo "  ENABLE_VERTEX_PROXY=true"
echo "  VERTEX_PROJECT_ID=${VERTEX_PROJECT_ID}"
echo "  VERTEX_ENDPOINT_REGION=${VERTEX_ENDPOINT_REGION}"
echo "  VERTEX_ENDPOINT_ID=${VERTEX_ENDPOINT_ID}"
echo "  REQUEST_TIMEOUT_SECONDS=${REQUEST_TIMEOUT_SECONDS:-30}"
echo
echo "Example Cloud Run /predict curl command:"
echo "curl -X POST ${service_url}/predict \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  --data @examples/predict_request.json"
echo
echo "Dry run only. No Cloud Run or Vertex AI request was made."
