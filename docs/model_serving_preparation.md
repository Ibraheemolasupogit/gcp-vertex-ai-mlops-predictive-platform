# Model Serving Preparation

R2 prepares the local model artifact for the serving API that will be built in
R3. It does not create a FastAPI or Flask application, Docker image, Cloud Run
service, or GCP deployment.

## Model Artifact Structure

```text
models/
  predictive_maintenance_model.joblib
  model_metadata.json
  README.md
```

`predictive_maintenance_model.joblib` is the fitted sklearn pipeline containing
preprocessing and the classifier. `model_metadata.json` describes the serving
contract and artifact context.

## Metadata Structure

The metadata captures:

- `model_name`
- `model_version`
- `model_type`
- `target_column`
- `feature_columns`
- `categorical_features`
- `numeric_features`
- `model_artifact_path`
- `trained_at`
- `training_data_path`
- `metrics_path`
- `feature_table_path`
- `approval_status`
- `local_only_notice`

## Prediction Utility Design

The prediction layer is framework-independent:

- `prediction/model_loader.py` loads the joblib model and metadata.
- `prediction/schemas.py` validates single-record and DataFrame inputs.
- `prediction/predictor.py` runs single and batch predictions and maps failure
  probability to a risk band.

Risk bands are:

- `critical`: probability >= 0.75
- `high`: probability >= 0.50
- `medium`: probability >= 0.25
- `low`: probability < 0.25

## Expected Serving Input Shape

Serving inputs must include all model feature columns from metadata and must not
include the target label. A local sample request is available at:

```text
data/sample/prediction_request.json
```

## Local Prediction Flow

Run:

```bash
python3 scripts/run_local_prediction.py
```

The script loads the local model bundle, scores the sample request, and prints
`prediction_class`, `prediction_probability`, and `risk_band`.

## R3 Preparation

R3 can build a FastAPI or Flask service around these utilities without
duplicating model loading, validation, or prediction logic.

## Future Cloud Mapping

The same serving contract can support a Cloud Run containerized API and can also
map conceptually to Vertex AI Endpoint prediction requests. R2 remains local
only and does not connect to GCP.

## Limitations

The model is trained on synthetic data. The artifact and prediction utilities
are suitable for local serving development and portfolio evidence, not
production performance claims.
