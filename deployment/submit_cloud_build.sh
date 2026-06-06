#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  PROJECT_ID
  REGION
  ARTIFACT_REPOSITORY
  IMAGE_NAME
  IMAGE_TAG
  SERVICE_NAME
  PORT
  ALLOW_UNAUTHENTICATED
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Tip: source a local, uncommitted env file based on deployment/env.example." >&2
    exit 1
  fi
done

image_uri="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Submitting Cloud Build with parameterized substitutions."
echo "  project: ${PROJECT_ID}"
echo "  region: ${REGION}"
echo "  image: ${image_uri}"
echo "  service: ${SERVICE_NAME}"

gcloud builds submit . \
  --project="${PROJECT_ID}" \
  --config=cloudbuild.yaml \
  --substitutions="_PROJECT_ID=${PROJECT_ID},_REGION=${REGION},_ARTIFACT_REPOSITORY=${ARTIFACT_REPOSITORY},_IMAGE_NAME=${IMAGE_NAME},_IMAGE_TAG=${IMAGE_TAG},_SERVICE_NAME=${SERVICE_NAME},_PORT=${PORT},_ALLOW_UNAUTHENTICATED=${ALLOW_UNAUTHENTICATED}"

echo "Expected image URI: ${image_uri}"
echo "Expected Cloud Run service: ${SERVICE_NAME}"
