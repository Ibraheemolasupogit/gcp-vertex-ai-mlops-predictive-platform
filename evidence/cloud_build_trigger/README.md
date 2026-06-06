# Cloud Build Trigger Evidence

Add real screenshots and redacted command evidence here after a GitHub-triggered
Cloud Build deployment is created in a real GCP project.

Suggested R7 evidence:

- Cloud Build GitHub connection.
- Trigger configuration.
- Trigger run from a GitHub commit.
- Build logs.
- Build steps for Docker build, image push, and Cloud Run deploy.
- Artifact Registry image pushed by the trigger.
- Cloud Run revision created by the trigger.
- `/health` endpoint response after triggered deployment.
- `/predict` endpoint response after triggered deployment.

Do not add fake screenshots, credentials, service account keys, or unredacted
project-sensitive values.
