#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-gcp-vertex-ai-mlops-predictive-platform:local}"

docker build -t "${IMAGE_NAME}" .
echo "Built Docker image: ${IMAGE_NAME}"
