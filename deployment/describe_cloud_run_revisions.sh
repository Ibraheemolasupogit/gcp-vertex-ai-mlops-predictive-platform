#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_DESCRIBE_REVISIONS=true to run the commands.

required_vars=(
  PROJECT_ID
  REGION
  SERVICE_NAME
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/traffic_split.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

revisions_command=(
  gcloud run revisions list
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--service=${SERVICE_NAME}"
  "--platform=managed"
)

service_command=(
  gcloud run services describe "${SERVICE_NAME}"
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--platform=managed"
)

echo "Cloud Run revisions command:"
printf ' %q' "${revisions_command[@]}"
echo
echo "Cloud Run service describe command:"
printf ' %q' "${service_command[@]}"
echo

if [[ "${CONFIRM_DESCRIBE_REVISIONS:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_DESCRIBE_REVISIONS=true to inspect revisions."
  exit 0
fi

"${revisions_command[@]}"
"${service_command[@]}"
