#!/usr/bin/env bash
set -euo pipefail

cloud_run_url="${CLOUD_RUN_URL:-${1:-}}"
predict_request="${PREDICT_REQUEST:-examples/predict_request.json}"

if [[ -z "${cloud_run_url}" ]]; then
  echo "Missing CLOUD_RUN_URL. Set CLOUD_RUN_URL or pass the URL as the first argument." >&2
  exit 1
fi

cloud_run_url="${cloud_run_url%/}"

echo "Testing Cloud Run service: ${cloud_run_url}"
echo "Authenticated services may require: gcloud auth print-identity-token"

echo "GET /"
curl -fsS "${cloud_run_url}/"
echo

echo "GET /health"
curl -fsS "${cloud_run_url}/health"
echo

echo "POST /predict"
curl -fsS \
  -X POST "${cloud_run_url}/predict" \
  -H "Content-Type: application/json" \
  --data @"${predict_request}"
echo

echo "Cloud Run smoke checks completed."
