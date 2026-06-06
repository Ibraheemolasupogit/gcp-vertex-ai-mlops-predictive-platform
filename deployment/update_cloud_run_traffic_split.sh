#!/usr/bin/env bash
set -euo pipefail

# Dry-run by default. Set CONFIRM_UPDATE_TRAFFIC=true to execute.
# Optional rollback mode: ROLLBACK_TO_STABLE=true routes 100% to STABLE_REVISION.

required_vars=(
  PROJECT_ID
  REGION
  SERVICE_NAME
  STABLE_REVISION
  CANDIDATE_REVISION
  STABLE_TRAFFIC_PERCENT
  CANDIDATE_TRAFFIC_PERCENT
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required environment variable: ${var_name}" >&2
    echo "Use deployment/traffic_split.env.example as a local, uncommitted template." >&2
    exit 1
  fi
done

if [[ "${ROLLBACK_TO_STABLE:-false}" == "true" ]]; then
  traffic_spec="${STABLE_REVISION}=100"
  echo "Rollback mode enabled. Candidate revision will receive 0% traffic."
else
  total=$((STABLE_TRAFFIC_PERCENT + CANDIDATE_TRAFFIC_PERCENT))
  if [[ "${total}" -ne 100 ]]; then
    echo "Traffic percentages must sum to 100. Current sum: ${total}" >&2
    exit 1
  fi
  traffic_spec="${STABLE_REVISION}=${STABLE_TRAFFIC_PERCENT},${CANDIDATE_REVISION}=${CANDIDATE_TRAFFIC_PERCENT}"
fi

command=(
  gcloud run services update-traffic "${SERVICE_NAME}"
  "--project=${PROJECT_ID}"
  "--region=${REGION}"
  "--platform=managed"
  "--to-revisions=${traffic_spec}"
)

echo "Cloud Run traffic update command:"
printf ' %q' "${command[@]}"
echo

if [[ "${CONFIRM_UPDATE_TRAFFIC:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_UPDATE_TRAFFIC=true to update Cloud Run traffic."
  exit 0
fi

echo "CONFIRM_UPDATE_TRAFFIC=true detected. Updating Cloud Run traffic..."
"${command[@]}"
