# GCP Vertex AI MLOps Predictive Platform

A local-first MLOps scaffold for a predictive maintenance platform designed to map cleanly to GCP Vertex AI services in later milestones.

## Problem Statement

Industrial equipment failures are costly, disruptive, and often preventable when telemetry, maintenance history, and model feedback are managed through a reliable ML lifecycle. This project is structured around a predictive maintenance use case where future milestones will generate equipment telemetry, train failure-risk models, register candidate models, run batch predictions, monitor model quality, and recommend retraining when drift or performance degradation is detected.

## Why This Project Matters

Predictive maintenance is a practical business theme for demonstrating end-to-end MLOps. It connects measurable operational outcomes, such as downtime reduction and maintenance planning, with engineering concerns like reproducible pipelines, model governance, monitoring, and deployment gates.

## Local-First Approach

Milestone 1 keeps the repository runnable without GCP credentials, cloud resources, secrets, or deployment steps. The scaffold is organized so local scripts and tests can evolve into cloud-backed workflows while preserving clear boundaries between data generation, ingestion, feature engineering, training, registry, prediction, monitoring, serving, and reporting.

## Planned GCP Mapping

The future architecture is intended to map local components to managed GCP services:

- Cloud Storage for raw, processed, and model artifact storage
- BigQuery for feature tables, training views, monitoring queries, and analytics
- Pub/Sub for event-driven data and monitoring notifications
- Dataflow for scalable ingestion and transformation workloads
- Vertex AI Pipelines for orchestrated ML workflows
- Vertex AI Training for managed model training jobs
- Vertex AI Model Registry for model versioning and approval metadata
- Vertex AI Batch Prediction for scheduled scoring jobs
- Vertex AI Endpoint or Cloud Run for serving selected model versions
- Vertex AI Model Monitoring for drift and skew detection
- Cloud Logging and Cloud Monitoring for operational telemetry

## Repository Structure

```text
configs/                 Configuration placeholders for pipeline, data, features, models, monitoring, and deployment gates
dashboard/               Placeholder Streamlit dashboard entrypoint
data/                    Local raw, processed, and sample data directories
diagrams/                Mermaid diagrams for architecture and lifecycle workflows
docs/                    Concise design notes for architecture, lifecycle, registry, monitoring, deployment, and limitations
outputs/                 Local output artifacts from future runs
pipelines/               Local and Vertex AI pipeline design placeholders
reports/                 Local report artifacts from future analysis
scripts/                 Safe placeholder automation scripts
sql/                     BigQuery-oriented SQL placeholders
src/vertex_mlops_platform/ Python package skeleton
tests/                   Scaffold and import tests
```

## Milestone Roadmap

1. Repo setup and professional project scaffold
2. Synthetic predictive maintenance data generation
3. Data ingestion and validation
4. Feature engineering workflow
5. Baseline model training and evaluation
6. Local model registry and deployment gates
7. Batch prediction and reporting workflow
8. Monitoring, drift checks, and retraining recommendations
9. Vertex AI pipeline design and cloud mapping
10. Dashboard polish and portfolio-ready documentation

## Current Status

Milestone 5 is complete with local model training and evaluation. A RandomForest
predictive maintenance classifier is trained locally, with metrics, feature
importance, and an evaluation report generated from synthetic data. No
deployment, model registry, real GCP resources, real equipment data,
benchmarking suite, or credentials are included.

## Run Tests

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest
```

You can also run the configured checks with:

```bash
make test
make lint
```

## Portfolio Positioning

This repository is intended to show structured MLOps engineering judgment: clean project boundaries, local reproducibility, responsible configuration placeholders, and a clear path from local workflows to managed GCP services. It avoids fake production claims and leaves implementation details for the appropriate milestones.
