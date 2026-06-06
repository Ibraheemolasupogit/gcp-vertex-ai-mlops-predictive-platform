# Docker Serving

R4 containerizes the local FastAPI prediction service so it can be tested as a
standalone runtime and prepared for a later Cloud Run deployment milestone.

## Purpose

The Docker image packages the API source code and trained local model bundle.
It does not generate data, train the model, run approval gates, connect to GCP,
or deploy anything.

## Runtime Artifacts

The container includes:

- `models/predictive_maintenance_model.joblib`
- `models/model_metadata.json`
- `models/README.md`
- `src/vertex_mlops_platform/`

These artifacts allow the API to serve `GET /`, `GET /health`, `POST /predict`,
and `POST /predict-batch` without needing any local pipeline stage at startup.

## Build

```bash
bash scripts/docker_build_local.sh
```

Default image name:

```text
gcp-vertex-ai-mlops-predictive-platform:local
```

## Run

```bash
bash scripts/docker_run_local.sh
```

The container listens on `0.0.0.0` and uses the `PORT` environment variable,
defaulting to `8080`. The local helper maps host port `8080` to container port
`8080`.

## Test

In another terminal while the container is running:

```bash
bash scripts/docker_test_local.sh
```

Equivalent manual checks:

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/predict \
  -H "Content-Type: application/json" \
  --data @examples/predict_request.json
```

## Cloud Run Preparation

The Dockerfile uses port `8080`, reads the runtime port from `PORT`, and starts
Uvicorn with host `0.0.0.0`. This mirrors the container runtime pattern expected
by Cloud Run, while R4 remains local-only.

## Local-Only Note

No credentials, service account keys, project IDs, Artifact Registry pushes,
Cloud Build configuration, or Cloud Run deployment steps are included in R4.
