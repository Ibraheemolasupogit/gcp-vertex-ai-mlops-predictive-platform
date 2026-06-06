# GCP Vertex AI MLOps Predictive Platform

A local-first predictive maintenance MLOps platform that demonstrates the path
from model development to containerised serving, CI/CD readiness, Cloud Run
release management, and Vertex AI lifecycle design.

## Problem Statement

Industrial maintenance teams need earlier warning signals for machine failure so
they can reduce unplanned downtime, prioritise inspections, and make better use
of maintenance resources. This project uses fully synthetic machine telemetry to
model that workflow without exposing real operational data.

## What This Project Demonstrates

- Synthetic predictive maintenance data generation.
- Data ingestion, validation, and quality summaries.
- Feature engineering for sensor, rolling-window, lifecycle, and maintenance
  history features.
- Local model training, evaluation, feature importance, and approval gates.
- FastAPI prediction service with local model serving and future Vertex AI proxy
  mode.
- Docker, Artifact Registry, Cloud Run, Cloud Build, and GitHub-triggered
  deployment readiness.
- Cloud Run revisions, traffic splitting, and rollback evidence planning.
- Vertex AI custom training, Model Registry, endpoint, online prediction, and
  batch prediction mapping.
- Cloud Composer / Airflow and Vertex AI Pipelines / Kubeflow orchestration
  design.
- Explainability, monitoring, model versioning, and evidence organisation docs.

## Architecture Overview

```text
Synthetic data
  -> validation
  -> feature engineering
  -> local training and evaluation
  -> approval gates
  -> model metadata and serving utilities
  -> FastAPI API
  -> Docker / Artifact Registry / Cloud Run readiness
  -> Cloud Build and GitHub trigger readiness
  -> Vertex AI training, registry, endpoint, and pipeline mapping
```

The repository is intentionally local-first. GCP deployment files are
parameterised templates, dry-run helpers, and documentation until a user chooses
to run them in their own GCP project.

## Implemented Capabilities

| Area | Status |
| --- | --- |
| Data generation | Synthetic machine, sensor, maintenance, and failure datasets |
| Data validation | Schema checks, relationship checks, data quality JSON summary |
| Feature engineering | Model-ready feature table and local feature-store metadata |
| Training | RandomForest classifier trained locally |
| Evaluation | Metrics, confusion matrix, baseline comparison, feature importance |
| Governance | Deployment approval gate report with Ready / Review / Blocked logic |
| Serving | Local FastAPI `/health`, `/predict`, and `/predict-batch` endpoints |
| Containerisation | Dockerfile and local Docker helper scripts |
| CI/CD readiness | Cloud Build config and GitHub trigger templates |
| GCP lifecycle mapping | Cloud Run, Vertex AI, Composer, and pipeline design artifacts |

## Local Run Instructions

Run the local workflow end to end:

```bash
scripts/run_all_local.sh
```

Or run stages individually:

```bash
python3 scripts/generate_demo_data.py
python3 scripts/run_data_validation.py
python3 scripts/run_feature_engineering.py
python3 scripts/run_training_pipeline.py
python3 scripts/run_approval_gates.py
python3 scripts/run_local_prediction.py
python3 scripts/generate_monitoring_summary.py
```

Run repository checks:

```bash
python3 -m pytest
python3 -m ruff check .
```

## API Usage Summary

Start the local API:

```bash
python3 scripts/run_api_local.py
```

Key endpoints:

- `GET /`
- `GET /health`
- `POST /predict`
- `POST /predict-batch`

Example request payloads are available in `examples/`.

## Docker Summary

The Docker setup packages the FastAPI service for local container testing and
future Cloud Run deployment:

```bash
bash scripts/docker_build_local.sh
bash scripts/docker_run_local.sh
bash scripts/docker_test_local.sh
```

Docker runtime testing requires Docker to be available locally.

## GCP Deployment Evidence Path

The repository includes parameterised guides and dry-run helpers for:

- Artifact Registry and manual Cloud Run deployment.
- Cloud Build CI/CD.
- GitHub-triggered Cloud Build.
- Cloud Run revisions and traffic splitting.
- Cloud Run API proxy design in front of Vertex AI.

See [docs/deployment_evidence_checklist.md](docs/deployment_evidence_checklist.md)
and [docs/screenshot_evidence_guide.md](docs/screenshot_evidence_guide.md).

## Vertex AI Lifecycle Mapping

The Vertex AI design layer covers:

- Custom training.
- Model Registry metadata and versioning.
- Endpoint deployment readiness.
- Online prediction and batch prediction readiness.
- Cloud Composer / Airflow continuous training design.
- Vertex AI Pipelines / Kubeflow component design.

These are documented as safe templates and design artifacts. They do not submit
real jobs or create cloud resources.

## Evidence

Evidence folders are indexed in [evidence/README.md](evidence/README.md).
Screenshots should be captured only after real deployment runs in a user-owned
GCP project. Fake screenshots, credentials, service account keys, and unredacted
secrets should not be committed.

## Current Status

This project is ready as a local-first GCP MLOps portfolio repository. It
contains working local ML functionality, serving utilities, tests, deployment
readiness templates, orchestration design, and documentation for evidence
capture.

## Limitations

- Data is synthetic.
- Metrics are local workflow evidence, not production performance claims.
- No real GCP resources are created by this repository by default.
- Deployment scripts are parameterised and should be reviewed before use.
- Real screenshots and cloud evidence must be captured manually after running
  the deployment path in a user-owned GCP project.

## Portfolio Positioning

This repository presents a practical MLOps engineering workflow: build locally,
test locally, containerise serving, prepare CI/CD, map the model lifecycle to GCP
services, and organise evidence without overstating production deployment.
