#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  PROJECT_ID
  REGION
  ARTIFACT_REPOSITORY
  IMAGE_NAME
  IMAGE_TAG
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Tip: source deployment/env.example values from a local, uncommitted file." >&2
    exit 1
  fi
done

local_image="${IMAGE_NAME}:${IMAGE_TAG}"
image_uri="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building local Docker image: ${local_image}"
docker build -t "${local_image}" .

echo "Configuring Docker authentication for Artifact Registry host:"
echo "  ${REGION}-docker.pkg.dev"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "Tagging image:"
echo "  ${local_image} -> ${image_uri}"
docker tag "${local_image}" "${image_uri}"

echo "Pushing image to Artifact Registry:"
docker push "${image_uri}"

echo "Pushed image URI: ${image_uri}"
