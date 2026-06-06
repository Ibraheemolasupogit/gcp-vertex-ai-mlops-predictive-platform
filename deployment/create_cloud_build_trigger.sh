#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_CREATE_TRIGGER=true to execute.

required_vars=(
  PROJECT_ID
  REGION
  TRIGGER_NAME
  REPO_OWNER
  REPO_NAME
  BRANCH_REGEX
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
    echo "This helper is dry-run by default. Use local, uncommitted env values." >&2
    exit 1
  fi
done

substitutions="_PROJECT_ID=${PROJECT_ID},_REGION=${REGION},_ARTIFACT_REPOSITORY=${ARTIFACT_REPOSITORY},_IMAGE_NAME=${IMAGE_NAME},_IMAGE_TAG=${IMAGE_TAG},_SERVICE_NAME=${SERVICE_NAME},_PORT=${PORT},_ALLOW_UNAUTHENTICATED=${ALLOW_UNAUTHENTICATED}"

command=(
  gcloud builds triggers create github
  "--project=${PROJECT_ID}"
  "--name=${TRIGGER_NAME}"
  "--repo-owner=${REPO_OWNER}"
  "--repo-name=${REPO_NAME}"
  "--branch-pattern=${BRANCH_REGEX}"
  "--build-config=cloudbuild.yaml"
  "--substitutions=${substitutions}"
  "--region=global"
)

echo "Cloud Build GitHub trigger command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_CREATE_TRIGGER:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_CREATE_TRIGGER=true to create the trigger."
  exit 0
fi

echo "CONFIRM_CREATE_TRIGGER=true detected. Creating trigger..."
"${command[@]}"
