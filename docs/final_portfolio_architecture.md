# Final Portfolio Architecture

This repository demonstrates a production-style GCP MLOps deployment evidence
path for predictive maintenance while staying explicit about what is local,
planned, or placeholder-based.

## End-To-End Narrative

Synthetic machine data flows through local validation, feature engineering,
model training, evaluation, and approval gates. The trained model is prepared for
serving through a FastAPI API, Docker container, Cloud Run deployment path, and
Vertex AI lifecycle mapping.

## Local Development Layer

The local layer includes deterministic synthetic data generation, schema
validation, feature engineering, model training, evaluation, approval gates,
prediction utilities, and tests. It proves the workflow can run end to end
without credentials or cloud resources.

## Container Serving Layer

The FastAPI service exposes health, single prediction, and batch prediction
endpoints. Docker configuration prepares the service for container deployment
while keeping local execution available.

## CI/CD Deployment Layer

Manual deployment scripts, Cloud Build configuration, and GitHub-triggered build
templates show how a serving container would move from source code to Artifact
Registry and Cloud Run.

## Cloud Run Release Management Layer

Cloud Run revision and traffic-splitting documentation prepares blue/green,
canary, rollback, and evidence capture workflows.

## Vertex AI Lifecycle Layer

Vertex AI custom training, Model Registry, endpoint, online prediction, and
batch prediction templates map local ML artifacts to managed GCP lifecycle
concepts.

## Orchestration Layer

Cloud Composer / Airflow design covers scheduled or trigger-based continuous
training. Vertex AI Pipelines / Kubeflow design covers reusable ML components,
artifact lineage, and managed pipeline execution.

## Monitoring, Explainability, And Governance Layer

Feature importance, monitoring summaries, data quality output, approval gates,
model versioning, and evidence guidance show how the project would support
reviewable model governance.

## Presentation Boundary

The repository demonstrates production-style MLOps design and local
implementation. It does not claim that the system is deployed to production or
validated against real industrial data.
