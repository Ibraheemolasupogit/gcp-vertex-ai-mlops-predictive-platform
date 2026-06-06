# Course Alignment

This document maps the repository to the practical GCP MLOps workflow from the
course and identifies the evidence that should be captured later.

| Course concept | Planned repo implementation | Current repo status | Evidence to capture | Future milestone |
| --- | --- | --- | --- | --- |
| Local model training and evaluation | Keep local feature table, sklearn training, metrics, reports | Implemented | Training script output, metrics JSON, evaluation report | Current / R2 polish |
| FastAPI or Flask serving API | Local API loading model bundle with `/health` and `/predict` | Not implemented | Local endpoint responses, API tests | R3 |
| Docker image | Dockerfile for serving API | Not implemented | Local image build, container health response | R4 |
| Artifact Registry | Push serving image to Artifact Registry | Not implemented | Artifact Registry image screenshot, image digest | R5 |
| Cloud Build | `cloudbuild.yaml` for build and deploy | Not implemented | Successful Cloud Build run | R6 |
| GitHub trigger | Cloud Build trigger from GitHub commits | Not implemented | Trigger config and triggered run | R7 |
| Cloud Run service | Deploy containerized API to Cloud Run | Not implemented | Service URL, deployed revision, `/health`, `/predict` | R5-R7 |
| Cloud Run revisions and traffic splitting | Demonstrate revision management and split traffic | Not implemented | Revision list, traffic split screenshot | R8 |
| Vertex AI custom training | Package training job for Vertex AI custom training | Conceptual docs only | Training job screenshot/logs | R9 |
| Vertex AI Model Registry | Register trained model/version metadata | Placeholder package only | Registry entry, version metadata | R9 |
| Vertex AI Endpoint | Deploy registered model to endpoint | Not implemented | Endpoint details screenshot | R10 |
| Online prediction | Send request to Vertex AI endpoint | Not implemented | Online prediction request/response | R10 |
| Batch prediction | Run batch prediction job on sample input | Placeholder script only | Batch job, output files | R10 |
| Cloud Composer / Airflow continuous training design | DAG design for retraining workflow | Conceptual only | DAG code or design screenshot | R12 |
| Kubeflow / Vertex AI Pipelines design | Pipeline design for training/evaluation/registration | Placeholder pipeline docs | Pipeline graph/design screenshot | R13 |
| Feature Store or BigQuery feature table pattern | Use local feature table and SQL docs as BigQuery mapping | Partially implemented locally | BigQuery schema/query docs, feature table mapping | R9-R13 |
| Explainability | Add explainability output for model predictions | Not implemented | Feature attribution output/report | R14 |
| Model versioning | Track versions across local bundle and registry simulation | Not implemented | Version manifest, registry metadata | R7-R10 |
| Cloud Logging and Cloud Monitoring | Capture API logs and service metrics | Not implemented | Logs, latency/error metrics | R14 |

## Alignment Notes

The existing local workflow should remain the base for course-aligned
deployment evidence. The next implementation work should not jump straight to
GCP. It should first make the model artifact easy to serve locally, then add the
API, Docker image, and deployment documentation in separate milestones.
