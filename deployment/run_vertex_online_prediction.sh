#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_RUN_VERTEX_ONLINE_PREDICTION=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_ENDPOINT_ID
  ONLINE_PREDICTION_INPUT
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai_prediction.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

if [[ ! -f "${ONLINE_PREDICTION_INPUT}" ]]; then
  echo "Prediction input file not found: ${ONLINE_PREDICTION_INPUT}" >&2
  exit 1
fi

command=(
  gcloud ai endpoints predict "${VERTEX_ENDPOINT_ID}"
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--json-request=${ONLINE_PREDICTION_INPUT}"
)

echo "Vertex AI online prediction command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_RUN_VERTEX_ONLINE_PREDICTION:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_RUN_VERTEX_ONLINE_PREDICTION=true to run online prediction."
  exit 0
fi

echo "CONFIRM_RUN_VERTEX_ONLINE_PREDICTION=true detected. Running Vertex AI online prediction..."
"${command[@]}"
