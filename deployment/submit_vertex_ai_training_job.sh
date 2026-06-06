#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_SUBMIT_VERTEX_TRAINING=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_STAGING_BUCKET
  VERTEX_TRAINING_JOB_NAME
  TRAINING_CONTAINER_IMAGE_URI
  TRAINING_MACHINE_TYPE
  MODEL_ARTIFACT_GCS_URI
  FEATURE_TABLE_GCS_URI
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

worker_pool_spec="machine-type=${TRAINING_MACHINE_TYPE},replica-count=1,container-image-uri=${TRAINING_CONTAINER_IMAGE_URI}"

command=(
  gcloud ai custom-jobs create
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--display-name=${VERTEX_TRAINING_JOB_NAME}"
  "--staging-bucket=${VERTEX_STAGING_BUCKET}"
  "--worker-pool-spec=${worker_pool_spec}"
  "--args=--feature-table-uri=${FEATURE_TABLE_GCS_URI},--model-output-uri=${MODEL_ARTIFACT_GCS_URI}"
  "--labels=workload=predictive-maintenance,stage=candidate,data-type=synthetic"
)

echo "Vertex AI custom training command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_SUBMIT_VERTEX_TRAINING:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_SUBMIT_VERTEX_TRAINING=true to submit the Vertex AI custom training job."
  exit 0
fi

echo "CONFIRM_SUBMIT_VERTEX_TRAINING=true detected. Submitting Vertex AI custom training job..."
"${command[@]}"
