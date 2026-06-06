# Deployment Evidence Checklist

Capture these items in later deployment milestones. Do not add credentials,
secrets, service account keys, or real project IDs to the repository.

## Cloud Run And CI/CD

- Cloud Build successful run.
- Artifact Registry image and digest.
- Cloud Run service.
- Cloud Run live service URL.
- `/health` endpoint response.
- `/predict` endpoint response.
- Cloud Run revisions.
- Cloud Run traffic split.
- GitHub-triggered Cloud Build run.

## Vertex AI Lifecycle

- Vertex AI custom training job.
- Vertex AI Model Registry entry.
- Vertex AI model version.
- Vertex AI endpoint.
- Online prediction response.
- Batch prediction job and output.

## Orchestration

- Cloud Composer / Airflow DAG design or screenshot if implemented.
- Vertex AI Pipeline / Kubeflow pipeline design or screenshot if implemented.

## Observability And Explainability

- Cloud Logging entries for serving requests.
- Cloud Monitoring metrics for Cloud Run or endpoint behavior.
- Explainability output.

## Final Portfolio Evidence

- Final architecture diagram.
- README screenshots section.
- Deployment command transcript with project IDs redacted or parameterized.
- Clear note that synthetic data is used for portfolio demonstration.
