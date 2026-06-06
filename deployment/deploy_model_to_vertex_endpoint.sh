#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_DEPLOY_VERTEX_MODEL=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_ENDPOINT_ID
  VERTEX_MODEL_ID
  DEPLOYED_MODEL_DISPLAY_NAME
  MACHINE_TYPE
  MIN_REPLICA_COUNT
  MAX_REPLICA_COUNT
  TRAFFIC_SPLIT_PERCENT
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai_prediction.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

command=(
  gcloud ai endpoints deploy-model "${VERTEX_ENDPOINT_ID}"
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--model=${VERTEX_MODEL_ID}"
  "--display-name=${DEPLOYED_MODEL_DISPLAY_NAME}"
  "--machine-type=${MACHINE_TYPE}"
  "--min-replica-count=${MIN_REPLICA_COUNT}"
  "--max-replica-count=${MAX_REPLICA_COUNT}"
  "--traffic-split=0=${TRAFFIC_SPLIT_PERCENT}"
)

echo "Vertex AI endpoint model deployment command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_DEPLOY_VERTEX_MODEL:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_DEPLOY_VERTEX_MODEL=true to deploy the model to the Vertex AI endpoint."
  exit 0
fi

echo "CONFIRM_DEPLOY_VERTEX_MODEL=true detected. Deploying model to Vertex AI endpoint..."
"${command[@]}"
