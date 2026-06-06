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
    echo "Tip: source deployment/env.example values from a local, uncommitted file." >&2
    exit 1
  fi
done

image_uri="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

auth_flag="--no-allow-unauthenticated"
if [[ "${ALLOW_UNAUTHENTICATED}" == "true" ]]; then
  auth_flag="--allow-unauthenticated"
fi

echo "Deploying Cloud Run service:"
echo "  service: ${SERVICE_NAME}"
echo "  image: ${image_uri}"
echo "  region: ${REGION}"
echo "  port: ${PORT}"
echo "  unauthenticated: ${ALLOW_UNAUTHENTICATED}"

gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${image_uri}" \
  --port="${PORT}" \
  --platform=managed \
  "${auth_flag}"

service_url="$(
  gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --platform=managed \
    --format='value(status.url)'
)"

echo "Cloud Run service URL: ${service_url}"
