# Model Versioning Strategy

Model versioning matters because model behavior changes as data, features,
training code, approval thresholds, and deployment targets change. A
professional MLOps workflow needs to trace which model artifact was trained,
evaluated, approved, registered, and served.

## Local Versioning Approach

The local workflow tracks versioning through:

- Model artifact: `models/predictive_maintenance_model.joblib`.
- Model metadata: `models/model_metadata.json`.
- Metrics: `outputs/model_metrics.json`.
- Feature importance: `outputs/feature_importance.csv`.
- Approval gates: `outputs/deployment_gate_results.json`.
- Feature metadata: `outputs/feature_store_metadata.json`.

Together, these artifacts form a local model record that can later be mapped to
Vertex AI Model Registry.

## Lifecycle Stages

Suggested lifecycle stages:

- Candidate: a trained model with metrics and metadata.
- Review: a model that passes blocking checks but still needs human review,
  often because synthetic data or warnings are present.
- Approved: a model accepted for deployment or promotion.
- Archived: an older model version retained for traceability.

## Relationship To Registry And Deployment

The local model registry simulation and metadata templates show what should be
recorded before model promotion. In Vertex AI Model Registry, the same concepts
map to model display names, version aliases, labels, metadata, metrics, and
approval status.

Cloud Run revisions represent serving container versions. They may include a
specific model artifact or proxy configuration. Vertex AI Model Registry
versions represent model lifecycle versions. In a complete deployment, both
should be linked through release notes, labels, or evidence documentation.

## No Production Claim

This repository demonstrates versioning design and local workflow evidence. It
does not claim that any model is production deployed or validated on real
equipment data.
