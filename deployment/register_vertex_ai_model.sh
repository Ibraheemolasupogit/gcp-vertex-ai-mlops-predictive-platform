#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_REGISTER_VERTEX_MODEL=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  VERTEX_MODEL_DISPLAY_NAME
  VERTEX_MODEL_VERSION_ALIAS
  MODEL_ARTIFACT_GCS_URI
  SERVING_CONTAINER_IMAGE_URI
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/vertex_ai.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

command=(
  gcloud ai models upload
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--display-name=${VERTEX_MODEL_DISPLAY_NAME}"
  "--artifact-uri=${MODEL_ARTIFACT_GCS_URI}"
  "--container-image-uri=${SERVING_CONTAINER_IMAGE_URI}"
  "--version-aliases=${VERTEX_MODEL_VERSION_ALIAS}"
  "--labels=workload=predictive-maintenance,stage=candidate,data-type=synthetic"
)

echo "Vertex AI Model Registry upload command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_REGISTER_VERTEX_MODEL:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_REGISTER_VERTEX_MODEL=true to upload the model to Vertex AI Model Registry."
  exit 0
fi

echo "CONFIRM_REGISTER_VERTEX_MODEL=true detected. Uploading model to Vertex AI Model Registry..."
"${command[@]}"
