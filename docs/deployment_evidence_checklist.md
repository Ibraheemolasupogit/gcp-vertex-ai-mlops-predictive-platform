# Deployment Evidence Checklist

Capture these items in later deployment milestones. Do not add credentials,
secrets, service account keys, or real project IDs to the repository.

## Cloud Run And CI/CD

- R5 `deployment/env.example` used with placeholders replaced locally.
- Artifact Registry repository created.
- Docker image pushed to Artifact Registry.
- Cloud Run service deployed.
- Cloud Run service URL captured.
- `/health` endpoint response screenshot.
- `/predict` endpoint response screenshot.
- Cloud Logging entry screenshot.
- Cleanup evidence if resources are removed after demonstration.
- R6 `cloudbuild.yaml` present.
- Cloud Build manual run submitted.
- Cloud Build build step success.
- Docker image pushed to Artifact Registry by Cloud Build.
- Cloud Run deploy step success.
- Cloud Run service revision updated by CI/CD.
- `/health` endpoint response after CI/CD deployment.
- `/predict` endpoint response after CI/CD deployment.
- R7 GitHub repository connected to Cloud Build.
- Cloud Build trigger configured for the main branch.
- Trigger substitutions captured.
- Commit pushed to GitHub.
- Cloud Build triggered automatically.
- Triggered build logs show Docker build, push, and deploy.
- Artifact Registry image created from trigger.
- Cloud Run revision updated from trigger.
- `/health` endpoint works after triggered deployment.
- `/predict` endpoint works after triggered deployment.
- R8 Cloud Run revisions visible.
- Stable revision identified.
- Candidate revision identified.
- Traffic split configured.
- 90/10 or similar canary split captured.
- `/health` endpoint checked during split.
- `/predict` endpoint checked during split.
- Cloud Logging confirms traffic reaching service.
- Rollback evidence captured.
- Monitoring chart captured if available.
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

- R9 Vertex AI API enabled.
- Staging bucket prepared.
- Custom training job submitted.
- Training job completed.
- Training logs captured.
- Model artifact written to Cloud Storage.
- Vertex AI Model Registry entry created.
- Model version alias captured.
- Model metrics and metadata captured.
- Model approval and lifecycle mapping captured.
- R10 Vertex AI endpoint created.
- Model deployed to endpoint.
- Endpoint ID captured.
- Deployed model details captured.
- Online prediction request captured.
- Online prediction response captured.
- Batch prediction job created.
- Batch prediction completed.
- Batch output Cloud Storage location captured.
- Logs and monitoring evidence captured where available.
- R11 Cloud Run service configured with Vertex endpoint variables.
- Cloud Run service account has Vertex AI predict permission.
- `/health` shows vertex endpoint mode.
- `/predict` request sent to Cloud Run.
- Vertex AI endpoint receives prediction.
- Normalised response returned by Cloud Run.
- Cloud Logging correlation captured.
- Error handling and timeout evidence captured where available.
- Vertex AI custom training job.
- Vertex AI Model Registry entry.
- Vertex AI model version.
- Vertex AI endpoint.
- Online prediction response.
- Batch prediction job and output.

## Orchestration

- R12 Cloud Composer environment created.
- DAG uploaded.
- DAG graph view captured.
- DAG run executed.
- Validation task success.
- Feature engineering task success.
- Vertex AI training task triggered.
- Metrics collection task completed.
- Approval gate task completed.
- Model registration task completed.
- DAG logs captured.
- R13 Vertex AI Pipeline job created.
- Pipeline graph captured.
- Validation component completed.
- Feature engineering component completed.
- Training component completed.
- Evaluation component completed.
- Approval gate component completed.
- Model registration component completed.
- Pipeline artifacts captured.
- Pipeline logs captured.
- Model Registry candidate linked to pipeline.
- Cloud Composer / Airflow DAG design or screenshot if implemented.
- Vertex AI Pipeline / Kubeflow pipeline design or screenshot if implemented.

## Observability And Explainability

- R14 feature importance explainability documented.
- Local monitoring summary generated.
- Model versioning strategy documented.
- Screenshot evidence guide completed.
- Final portfolio architecture documented.
- Cloud Logging entries for serving requests.
- Cloud Monitoring metrics for Cloud Run or endpoint behavior.
- Explainability output.

## Final Portfolio Evidence

- Evidence folder index completed.
- Repository health check documented.
- README polished for portfolio presentation.
- No fake screenshots committed.
- Final architecture diagram.
- README screenshots section.
- Deployment command transcript with project IDs redacted or parameterized.
- Clear note that synthetic data is used for portfolio demonstration.
