#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  PROJECT_ID
  REGION
  ARTIFACT_REPOSITORY
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Tip: copy deployment/env.example to a local .env file outside git, then source it." >&2
    exit 1
  fi
done

echo "Ensuring Artifact Registry repository exists:"
echo "  project: ${PROJECT_ID}"
echo "  region: ${REGION}"
echo "  repository: ${ARTIFACT_REPOSITORY}"

if gcloud artifacts repositories describe "${ARTIFACT_REPOSITORY}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" >/dev/null 2>&1; then
  echo "Artifact Registry repository already exists."
else
  gcloud artifacts repositories create "${ARTIFACT_REPOSITORY}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --repository-format=docker \
    --description="Docker images for predictive maintenance model serving"
  echo "Artifact Registry repository created."
fi

image_uri="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME:-predictive-maintenance-api}:${IMAGE_TAG:-local}"
echo "Future image URI: ${image_uri}"
