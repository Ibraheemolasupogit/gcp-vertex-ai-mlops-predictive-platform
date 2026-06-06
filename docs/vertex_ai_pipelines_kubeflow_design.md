# Vertex AI Pipelines / Kubeflow Pipeline Design

R13 prepares a Vertex AI Pipelines and Kubeflow design layer for the predictive
maintenance MLOps workflow. It does not compile or submit a real pipeline job,
run Kubeflow, deploy Vertex AI Pipelines, or execute GCP commands.

## Purpose Of Vertex AI Pipelines

Vertex AI Pipelines provide managed orchestration for machine learning workflows.
They make model development steps visible, repeatable, and traceable through a
pipeline graph, component logs, artifacts, metadata, and lineage.

For this project, the pipeline design shows how the local predictive maintenance
workflow can become reusable managed components without changing the current
local-first implementation.

## Kubeflow Pipelines And Vertex AI Pipelines

Kubeflow Pipelines defines a component and pipeline authoring model. Vertex AI
Pipelines can run Kubeflow-style pipeline definitions on managed GCP
infrastructure. In practice, the team authors components using the Kubeflow
Pipelines SDK, compiles a pipeline specification, and submits the job to Vertex
AI Pipelines.

R13 keeps this mapping static and safe. The skeleton at `pipelines/vertex_pipeline.py`
uses optional Kubeflow imports, so tests do not require the SDK.

## Why Pipeline Orchestration Matters

Pipeline orchestration gives the MLOps workflow:

- Repeatable execution across data validation, feature engineering, training,
  evaluation, approval, and registration.
- Component-level logs and retry boundaries.
- Artifact lineage from raw data through model registration.
- Clear handoff points for approval gates and deployment readiness.
- Evidence for reviewers that the model lifecycle is controlled.

## Difference From Cloud Composer / Airflow

Cloud Composer / Airflow is a general workflow orchestrator. It is useful for
schedules, dependencies, operational workflows, and cross-system coordination.

Vertex AI Pipelines is a managed ML pipeline service. It is more focused on ML
components, artifacts, lineage, metadata, and Vertex AI lifecycle integration.
Both can coexist: Composer may trigger or coordinate pipelines, while Vertex AI
Pipelines executes the ML-specific graph.

## Local Workflow To Pipeline Components

| Pipeline component | Existing local workflow mapping |
| --- | --- |
| Data validation | `src/vertex_mlops_platform/ingestion/validate_schema.py` |
| Feature engineering | `src/vertex_mlops_platform/features/` |
| Model training | `src/vertex_mlops_platform/training/train_model.py` |
| Model evaluation | `src/vertex_mlops_platform/training/evaluate_model.py` |
| Deployment approval gates | `src/vertex_mlops_platform/training/approval_gates.py` |
| Model registration | Vertex AI Model Registry metadata templates |
| Batch prediction or endpoint readiness | R10 endpoint and batch prediction templates |

The detailed component mapping is documented in `pipelines/components.md`.

## Artifact Lineage

The future pipeline should track:

- Raw data or validated input data.
- Feature table artifact.
- Model artifact.
- Metrics JSON and evaluation report.
- Approval report.
- Registry metadata.
- Model-card-style evidence artifact.

This lineage lets reviewers follow how a candidate model moved from data to
approval and registry readiness.

## Pipeline Parameters

Expected parameters include:

- Project.
- Region.
- Pipeline root.
- Vertex staging bucket.
- Feature table URI.
- Model output URI.
- Approval thresholds such as F1 and recall.
- Model display name.
- Service account placeholder.

The placeholder environment template is `deployment/vertex_pipeline.env.example`.
The pipeline configuration template is
`pipelines/config/vertex_pipeline_config.example.yaml`.

## Evidence Screenshots

Capture these only after a real Vertex AI Pipelines run:

- Vertex AI Pipeline run page.
- Pipeline graph.
- Component logs.
- Artifacts and metadata.
- Training job linked to the pipeline.
- Model Registry candidate version.
- Approval gate output.
- Pipeline labels and metadata.

## Security Notes

- Do not commit service account keys.
- Use a least privilege pipeline service account.
- Use Secret Manager only if secrets are needed later.
- Keep project IDs, bucket names, and service account identities parameterized or
  redacted in docs and evidence.
- Do not commit `.env` files.

## Limitations

R13 is a design and skeleton milestone only. It uses synthetic data, placeholder
configuration, and safe component bodies. No real pipeline run is submitted, and
no Vertex AI Pipelines, Kubeflow, or GCP command is executed. Final
explainability, monitoring, versioning, screenshots, and README polish are
deferred to R14.
