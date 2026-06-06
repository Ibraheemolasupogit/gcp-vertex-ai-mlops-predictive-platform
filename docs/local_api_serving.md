# Local API Serving

R3 adds a local FastAPI service for predictive maintenance model serving. The
API wraps the existing R2 prediction utilities and does not retrain the model or
connect to GCP.

## Run Locally

```bash
python3 scripts/run_api_local.py
```

Default address:

```text
http://127.0.0.1:8000
```

## Endpoints

- `GET /`: service metadata.
- `GET /health`: model and metadata load status.
- `POST /predict`: single-record prediction.
- `POST /predict-batch`: small local batch prediction.

## Example Requests

Single prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  --data @examples/predict_request.json
```

Batch prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict-batch \
  -H "Content-Type: application/json" \
  --data @examples/batch_predict_request.json
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Response Shape

`POST /predict` returns:

```json
{
  "prediction_class": 0,
  "prediction_probability": 0.01,
  "risk_band": "low",
  "model_name": "predictive_maintenance_classifier",
  "model_version": "local-v1",
  "request_id": "generated-request-id",
  "timestamp": "generated-timestamp",
  "local_only_notice": "Local development service only..."
}
```

## Tests

```bash
python3 -m pytest tests/test_serving_api.py
```

## Docker And Cloud Run Preparation

This API keeps model loading, validation, and scoring in reusable package
utilities. R4 can Dockerize the same app without changing prediction logic. Later
Cloud Run deployment can expose the same `/health`, `/predict`, and
`/predict-batch` endpoints.

## Local-Only Limitation

The API uses a model trained on synthetic data and local artifacts. It does not
use credentials, service account keys, Cloud Run settings, Artifact Registry,
Cloud Build, or Vertex AI endpoints.
