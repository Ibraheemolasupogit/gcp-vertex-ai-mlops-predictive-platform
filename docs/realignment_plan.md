# Realignment Plan

## Current Repo Assessment

The repository has a strong local-first predictive maintenance MLOps foundation.
It already demonstrates reproducible synthetic data generation, validation,
feature engineering, model training, evaluation, approval gates, local artifacts,
reports, and tests. This work should be preserved because it provides the
training and governance substrate needed for a practical GCP deployment path.

The current gap is deployment evidence. The repository is still framed mostly as
a local MLOps scaffold with conceptual GCP mapping. The next phase should
realign it toward a production-style journey from local model development to
serving, containerization, CI/CD, Cloud Run, and Vertex AI lifecycle design.

## Preserve

- `src/vertex_mlops_platform/data_generation/`: useful synthetic predictive
  maintenance data source for demos and tests.
- `src/vertex_mlops_platform/ingestion/`: useful local loading and validation
  layer.
- `src/vertex_mlops_platform/features/`: useful feature table builder and local
  feature-store-style metadata.
- `src/vertex_mlops_platform/training/train_model.py` and
  `evaluate_model.py`: useful local training and evaluation foundation.
- `src/vertex_mlops_platform/training/approval_gates.py`: useful governance
  control before registry or deployment simulation.
- `configs/`: useful local-first configuration surface.
- `scripts/run_all_local.sh` and milestone scripts: useful reproducible local
  workflow.
- `tests/`: useful regression safety net for later serving and deployment work.
- `models/`, `outputs/`, and `reports/`: useful evidence artifacts, as long as
  they remain clearly local and synthetic.
- Existing documentation: useful background material for architecture, data,
  features, training, and gates.

## Refactor Later

- Model artifact structure should be refactored for serving in R2, likely into a
  cleaner model bundle that includes model path, feature schema, target metadata,
  and prediction input contract.
- `src/vertex_mlops_platform/serving/` is currently empty and should become the
  serving package for FastAPI or Flask.
- Scripts should eventually distinguish local build/test commands from cloud
  deployment guide commands.
- Placeholder packages for `registry`, `prediction`, and `monitoring` should be
  implemented only when their aligned milestones arrive.
- Existing GCP docs should be consolidated or cross-linked to avoid a scattered
  documentation experience.

## Possible Archive Candidates Later

No files should be moved immediately. Potential archive candidates after R2-R5:

- Older generic docs that are superseded by deployment-specific docs.
- Placeholder pipeline files if replaced by concrete Vertex AI Pipeline or
  Kubeflow design artifacts.
- Placeholder dashboard files if the project direction prioritizes API serving
  and deployment evidence over Streamlit.

Archive only when the replacement exists and the old file creates confusion.

## Target Architecture

The target architecture keeps the predictive maintenance theme and grows from a
local ML workflow into a GCP deployment evidence path:

1. Local data, feature engineering, training, evaluation, approval gates, and
   model artifact generation.
2. Local FastAPI or Flask service that loads the trained artifact and exposes
   `/health` and `/predict`.
3. Docker image for the serving API.
4. Artifact Registry image storage and manual Cloud Run deployment guide.
5. Cloud Build CI/CD with GitHub trigger.
6. Cloud Run revisions and traffic splitting for A/B deployment evidence.
7. Vertex AI custom training, Model Registry mapping, endpoint deployment,
   online prediction, and batch prediction.
8. Continuous training design using Cloud Composer / Airflow and Vertex AI
   Pipelines or Kubeflow.
9. Explainability, model versioning, logging, monitoring, screenshots, and final
   portfolio polish.

## Recommended New Milestone Path

- R1: Repo audit and GCP deployment realignment plan.
- R2: Refactor local model package and artifact structure for serving.
- R3: Build local FastAPI model serving API with tests.
- R4: Dockerise the serving API.
- R5: Manual Cloud Run deployment guide using Artifact Registry.
- R6: Cloud Build CI/CD configuration.
- R7: GitHub-triggered Cloud Build deployment.
- R8: Cloud Run revisions and traffic splitting evidence.
- R9: Vertex AI custom training and Model Registry mapping.
- R10: Vertex AI endpoint, online prediction, and batch prediction.
- R11: Cloud Run API in front of Vertex AI endpoint.
- R12: Cloud Composer / Airflow continuous training design.
- R13: Vertex AI Pipelines / Kubeflow pipeline design.
- R14: Explainability, monitoring, versioning, screenshots, and final README
  polish.

## Risks And Assumptions

- Synthetic data is useful for demonstrating workflow structure, but all reports
  must avoid production performance claims.
- Cloud deployment milestones must avoid committing project IDs, credentials,
  service account keys, or secrets.
- Cloud Run and Vertex AI paths should be shown through reproducible commands,
  configs, screenshots, and documentation, not hidden manual steps.
- Serving must align with the trained feature schema; otherwise the API will be
  brittle.
- Container and CI/CD work should remain separate from Vertex AI lifecycle work
  to keep milestones reviewable.

## Next Implementation Milestone

R2 should refactor the local model artifact structure for serving. The expected
output is a clean local model bundle and prediction schema that R3 can load in a
FastAPI or Flask service.
