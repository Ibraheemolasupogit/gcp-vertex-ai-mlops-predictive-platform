# Vertex AI Custom Training And Model Registry Mapping

R9 prepares the local predictive maintenance training workflow for a future
Vertex AI custom training and Model Registry demonstration. It does not submit
jobs, upload models, deploy endpoints, or run GCP commands.

## Purpose

Vertex AI custom training provides a managed execution environment for training
code that has already been developed locally. In this repository, the local
training stage builds a RandomForest predictive maintenance classifier from the
engineered feature table. The Vertex AI mapping shows how that same workflow
would later run as a managed job with Cloud Storage inputs and outputs.

Model Registry provides a governed inventory of trained model versions. It is
where the future Vertex-trained model artifact, serving container image, labels,
metrics, and lifecycle metadata would be recorded before endpoint deployment.

## Local Training Versus Vertex AI Training

Local training currently runs from `scripts/run_training_pipeline.py` using
`data/processed/feature_table.csv`, local configs, and local output paths. This
is appropriate for development, tests, and portfolio workflow validation.

Vertex AI custom training would run similar training code in a managed GCP
worker pool. The feature table would be staged in Cloud Storage, the training
container or Python package would be referenced by the job, and outputs would be
written back to Cloud Storage for registration and later deployment.

## Local-To-Vertex Mapping

| Local asset | Vertex AI mapping |
| --- | --- |
| `scripts/run_training_pipeline.py` | Custom training entrypoint |
| `configs/model_config.yaml` | Training configuration passed as file or arguments |
| `data/processed/feature_table.csv` | Cloud Storage feature table input |
| `models/predictive_maintenance_model.joblib` | Model artifact output in Cloud Storage |
| `outputs/model_metrics.json` | Training metrics attached to registry metadata |
| `reports/evaluation_report.md` | Evaluation evidence or model card input |
| `models/model_metadata.json` | Registry metadata source |
| Cloud Run serving image | Future Vertex serving container image URI |

## Required GCP Services

- Vertex AI API for custom training and Model Registry.
- Cloud Storage for feature table inputs, staging files, and model outputs.
- Artifact Registry if custom training or serving containers are used.
- IAM with least privilege for the Vertex AI service account and any build or
  deployment service accounts.

## Expected Training Inputs

- Feature table staged in Cloud Storage.
- Model configuration such as target column, test split, random state, and model
  hyperparameters.
- Training container image or Python package containing the local training code.
- Optional labels that identify workload, lifecycle stage, and synthetic data
  status.

## Expected Training Outputs

- Trained model artifact written to Cloud Storage.
- Metrics JSON equivalent to `outputs/model_metrics.json`.
- Evaluation report equivalent to `reports/evaluation_report.md`.
- Model metadata equivalent to `models/model_metadata.json`.
- Training logs visible in Vertex AI and Cloud Logging.

## Model Registry Mapping

The future Model Registry entry should capture:

- Model display name, such as `predictive-maintenance-model`.
- Model version alias, such as `candidate`.
- Artifact URI pointing to the Cloud Storage model output.
- Serving container image URI for prediction.
- Labels for workload, stage, and synthetic data status.
- Metrics from local or Vertex AI evaluation output.
- Approval status from the deployment approval gate layer.
- Lifecycle stage, such as candidate, reviewed, approved, or archived.
- Dataset and feature versions.

The template at `deployment/vertex_ai_model_registry_metadata.template.json`
documents the intended metadata shape.

## Evidence Screenshots

Capture these only after a real GCP run:

- Vertex AI custom training job page.
- Training logs and worker status.
- Cloud Storage model artifact output.
- Vertex AI Model Registry entry.
- Model version details and alias.
- Metadata, labels, and metrics.
- Approval or lifecycle status mapping.

## Security Notes

- Do not commit service account keys.
- Use a least privilege service account for Vertex AI jobs.
- Keep project IDs, bucket names, and resource URIs parameterized or redacted in
  documentation.
- Use Secret Manager later only if secrets are actually required.
- Do not commit `.env` files.

## Limitations

R9 is a readiness and mapping milestone only. It uses synthetic data and does not
submit a Vertex AI custom training job, upload a model to Model Registry, deploy
an endpoint, or run online or batch prediction. Vertex AI endpoint deployment is deferred to R10.
