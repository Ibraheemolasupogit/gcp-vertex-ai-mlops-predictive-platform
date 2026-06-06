#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_RUN_VERTEX_BATCH_PREDICTION=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_MODEL_ID
  BATCH_PREDICTION_INPUT_URI
  BATCH_PREDICTION_OUTPUT_URI
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai_prediction.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

job_display_name="${BATCH_PREDICTION_JOB_NAME:-predictive-maintenance-batch-prediction}"

command=(
  gcloud ai batch-prediction-jobs create
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--display-name=${job_display_name}"
  "--model=${VERTEX_MODEL_ID}"
  "--gcs-source=${BATCH_PREDICTION_INPUT_URI}"
  "--instances-format=jsonl"
  "--gcs-destination-output-uri-prefix=${BATCH_PREDICTION_OUTPUT_URI}"
  "--predictions-format=jsonl"
)

echo "Vertex AI batch prediction command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_RUN_VERTEX_BATCH_PREDICTION:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_RUN_VERTEX_BATCH_PREDICTION=true to run batch prediction."
  exit 0
fi

echo "CONFIRM_RUN_VERTEX_BATCH_PREDICTION=true detected. Creating Vertex AI batch prediction job..."
"${command[@]}"
