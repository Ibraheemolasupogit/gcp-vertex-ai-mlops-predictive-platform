# Target Architecture

The target architecture is phased so the repository can show practical GCP MLOps
deployment evidence without pretending everything is already deployed.

## Phase 1: Local Training And Serving Prep

Use the existing local pipeline to generate synthetic data, validate it, build
features, train the model, evaluate it, and run approval gates. Refactor the
model artifact into a serving-ready bundle with schema metadata.

## Phase 2: Containerized Cloud Run Service

Build a FastAPI or Flask serving API locally. Package it with Docker, then
prepare an Artifact Registry and Cloud Run deployment guide. Capture local
container evidence before any cloud deployment evidence.

## Phase 3: Cloud Build CI/CD

Add Cloud Build configuration to build the Docker image, push it to Artifact
Registry, and deploy to Cloud Run. Add a GitHub trigger so commits can start the
build/deploy workflow.

## Phase 4: Cloud Run Revisions And Traffic Splitting

Demonstrate Cloud Run revision history and traffic splitting for A/B testing or
safe rollout evidence. Keep configuration parameterized and avoid hard-coded
project IDs.

## Phase 5: Vertex AI Lifecycle

Map the training workflow to Vertex AI custom training, register the model in
Vertex AI Model Registry, deploy a model version to a Vertex AI endpoint, and
show online and batch prediction evidence.

## Phase 6: Continuous Training Design

Design continuous training using Cloud Composer / Airflow and Vertex AI
Pipelines or Kubeflow. The design should show data preparation, training,
evaluation, approval, registration, and deployment decision points.

## Phase 7: Explainability, Monitoring, And Portfolio Polish

Add explainability outputs, model versioning evidence, Cloud Logging and Cloud
Monitoring screenshots, final architecture diagrams, and a concise README that
links to deployment evidence without making fake production claims.
