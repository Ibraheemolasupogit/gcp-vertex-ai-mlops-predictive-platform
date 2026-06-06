#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
PREDICT_REQUEST="${PREDICT_REQUEST:-examples/predict_request.json}"

echo "Checking ${BASE_URL}/health"
health_response="$(curl -fsS "${BASE_URL}/health")"
echo "${health_response}"

echo "Checking ${BASE_URL}/predict"
prediction_response="$(
  curl -fsS \
    -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    --data @"${PREDICT_REQUEST}"
)"
echo "${prediction_response}"

echo "Dockerized API smoke checks passed."
