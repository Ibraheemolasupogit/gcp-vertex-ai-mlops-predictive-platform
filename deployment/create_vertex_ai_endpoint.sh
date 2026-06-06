#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_CREATE_VERTEX_ENDPOINT=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_ENDPOINT_DISPLAY_NAME
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai_prediction.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

command=(
  gcloud ai endpoints create
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--display-name=${VERTEX_ENDPOINT_DISPLAY_NAME}"
  "--labels=workload=predictive-maintenance,stage=candidate,data-type=synthetic"
)

echo "Vertex AI endpoint creation command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_CREATE_VERTEX_ENDPOINT:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_CREATE_VERTEX_ENDPOINT=true to create the Vertex AI endpoint."
  exit 0
fi

echo "CONFIRM_CREATE_VERTEX_ENDPOINT=true detected. Creating Vertex AI endpoint..."
"${command[@]}"
