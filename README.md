# GCP Vertex AI MLOps Predictive Platform

A production-style GCP MLOps predictive maintenance platform showing the journey
from local ML development to containerized serving, CI/CD, Cloud Run deployment
evidence, and Vertex AI lifecycle design.

## Purpose

This project uses a predictive maintenance theme to demonstrate practical MLOps
engineering: synthetic equipment telemetry, local model development, governance
checks, and a planned deployment evidence path aligned with real GCP services.

## Current Status

The repository currently implements a local-first ML workflow:

- Synthetic predictive maintenance datasets
- Data ingestion and validation
- Feature engineering and local feature-store-style metadata
- RandomForest model training and evaluation
- Model artifact, metrics, feature importance, and evaluation report
- Deployment approval gates with readiness status
- Serving-ready model metadata and local prediction utilities
- Local FastAPI serving API with health, single prediction, and batch prediction
- Dockerfile and local Docker helper scripts for the serving API
- Tests for data generation, validation, features, training, and gates

No model is deployed. No GCP resources, credentials, secrets, service account
keys, or real project IDs are included.

R3 status: a local FastAPI serving API has been added with `/health`, `/predict`,
and `/predict-batch` endpoints plus API tests and example requests. No Docker
image, Cloud Run service, Cloud Build configuration, or GCP deployment has been
added yet.

R4 status: the FastAPI API is containerized with a Cloud Run-style port `8080`,
plus local Docker build, run, and smoke-test scripts. No Artifact Registry,
Cloud Run, Cloud Build, GitHub trigger, or GCP deployment has been added yet.

R5 status: a manual Artifact Registry and Cloud Run deployment guide has been
added with parameterized deployment scripts and an evidence folder. No Cloud
Build, GitHub trigger, traffic splitting, Vertex AI deployment, real
credentials, or real project IDs are included.

R6 status: Cloud Build CI/CD configuration has been added for build, push, and
Cloud Run deploy using parameterized substitutions, plus a manual submit helper.
No GitHub trigger, traffic splitting, Vertex AI deployment, credentials, or real
project IDs are included.

R7 status: the GitHub-triggered Cloud Build deployment path is documented with a
trigger template, dry-run trigger helper, and trigger evidence folder. No real
trigger was created, and no traffic splitting, Vertex AI deployment,
credentials, or real project IDs are included.

R8 status: Cloud Run revision and traffic splitting workflow documentation,
dry-run traffic helpers, and traffic-splitting evidence placeholders have been
added. No live traffic split, Vertex AI deployment, credentials, or real project
IDs are included.

## Course-Aligned Objective

The realigned objective is to build a stronger practical GCP deployment evidence
path:

1. Local model artifact and serving-ready package
2. FastAPI or Flask prediction API
3. Dockerized serving container
4. Artifact Registry and manual Cloud Run deployment guide
5. Cloud Build CI/CD and GitHub trigger
6. Cloud Run revisions and traffic splitting evidence
7. Vertex AI custom training, Model Registry, endpoints, online prediction, and
   batch prediction
8. Cloud Composer / Airflow and Vertex AI Pipelines design
9. Explainability, logging, monitoring, screenshots, and final portfolio polish

## Architecture Overview

```text
Synthetic data -> validation -> feature table -> local training
      -> metrics/report -> approval gates -> serving-ready model bundle
      -> API -> Docker -> Artifact Registry -> Cloud Run
      -> Cloud Build/GitHub trigger -> Vertex AI lifecycle design
```

## Repository Structure

```text
configs/                  Local configuration for data, features, models, and gates
data/                     Synthetic sample and processed feature data
docs/                     Architecture, data, training, deployment, and realignment docs
models/                   Local trained model artifact
outputs/                  Metrics, feature metadata, and gate results
reports/                  Evaluation and readiness reports
scripts/                  Local workflow scripts
src/vertex_mlops_platform/ Python package for data, features, training, and future serving
tests/                    Unit tests for implemented workflow stages
```

## Run Local Workflow

```bash
python3 scripts/generate_demo_data.py
python3 scripts/run_data_validation.py
python3 scripts/run_feature_engineering.py
python3 scripts/run_training_pipeline.py
python3 scripts/run_approval_gates.py
```

Or run the implemented local chain:

```bash
scripts/run_all_local.sh
```

## Run Checks

```bash
python3 -m pytest
python3 -m ruff check .
```

## Deployment Evidence Plan

Future milestones will capture Cloud Build runs, Artifact Registry images,
Cloud Run service URLs, `/health` and `/predict` responses, Cloud Run revisions,
traffic splitting, Vertex AI training jobs, Model Registry entries, endpoint
predictions, batch predictions, logs, metrics, explainability outputs, and final
architecture diagrams.

## Safety Note

This repository is intentionally local-first until explicit deployment
milestones. It must not contain credentials, secrets, service account keys, or
hard-coded real GCP project IDs. Synthetic data and local metrics are portfolio
workflow evidence, not production performance claims.
