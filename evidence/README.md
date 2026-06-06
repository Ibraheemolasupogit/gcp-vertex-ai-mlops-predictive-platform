# Deployment Evidence Index

This folder is reserved for real deployment screenshots, command evidence, and
redacted notes captured after running the deployment path in a personal GCP
project. Do not add fake screenshots.

## Evidence Folders

| Folder | Purpose | Example evidence |
| --- | --- | --- |
| `cloud_build_trigger/` | GitHub-triggered Cloud Build deployment path | Trigger configuration, triggered build logs, build steps |
| `cloud_composer_airflow/` | Cloud Composer / Airflow continuous training design | Composer environment, DAG graph, DAG run, task logs |
| `cloud_run_traffic_splitting/` | Cloud Run revisions and traffic splitting | Revision list, 90/10 split, rollback evidence |
| `cloud_run_vertex_proxy/` | Cloud Run API proxying to Vertex AI endpoint | Proxy env vars, `/health`, `/predict`, correlation logs |
| `vertex_ai_endpoint_prediction/` | Vertex AI endpoint, online prediction, batch prediction | Endpoint screen, deployed model, prediction response, batch output |
| `vertex_ai_model_registry/` | Vertex AI custom training and Model Registry | Training job, logs, model entry, version alias, labels |
| `vertex_ai_pipelines/` | Vertex AI Pipelines / Kubeflow design | Pipeline graph, component logs, artifact lineage |

## Redaction Guidance

- Redact sensitive project identifiers if needed.
- Never commit service account keys, tokens, cookies, or private credentials.
- Avoid screenshots that expose billing details or unrelated private resources.
- Prefer concise `.png`, `.md`, or `.txt` files with descriptive names.

## No Fake Evidence

Only add evidence captured from real local or GCP runs. Placeholder README files
are acceptable; fabricated screenshots or fabricated cloud outputs are not.
