# Cloud Build CI/CD

R6 adds a parameterized Cloud Build configuration for building the FastAPI
serving image, pushing it to Artifact Registry, and deploying it to Cloud Run.
It does not create GitHub triggers, traffic splitting, Vertex AI deployment, or
real GCP resources.

## How Cloud Build Fits

R5 documented the manual Artifact Registry and Cloud Run path. R6 converts that
manual build/push/deploy sequence into a Cloud Build pipeline that can be
submitted manually. R7 will add GitHub-triggered builds.

## Required APIs

- Cloud Build API
- Artifact Registry API
- Cloud Run API

## IAM Permissions

At a conceptual level, the Cloud Build service account needs permission to:

- read source submitted to Cloud Build
- build Docker images
- push images to Artifact Registry
- deploy services to Cloud Run
- read/update Cloud Run service metadata

Use least-privilege IAM in real projects. Do not add service account keys to the
repository.

## Configuration

`cloudbuild.yaml` contains three main steps:

1. Build the Docker image.
2. Push the image to Artifact Registry.
3. Deploy the image to Cloud Run with `gcloud run deploy`.

The image URI is parameterized:

```text
${_REGION}-docker.pkg.dev/${_PROJECT_ID}/${_ARTIFACT_REPOSITORY}/${_IMAGE_NAME}:${_IMAGE_TAG}
```

## Substitutions

Required substitutions:

- `_PROJECT_ID`
- `_REGION`
- `_ARTIFACT_REPOSITORY`
- `_IMAGE_NAME`
- `_IMAGE_TAG`
- `_SERVICE_NAME`
- `_PORT`
- `_ALLOW_UNAUTHENTICATED`

See:

```text
deployment/cloudbuild.substitutions.example.yaml
```

## Manual Submit

Use local, uncommitted environment variables based on `deployment/env.example`,
then run:

```bash
bash deployment/submit_cloud_build.sh
```

The helper validates required variables and submits:

```bash
gcloud builds submit . --config=cloudbuild.yaml --substitutions=...
```

## Verify

After a real manual submission, capture:

- Cloud Build successful run.
- Build step success.
- Docker image pushed to Artifact Registry.
- Cloud Run deploy step success.
- Cloud Run service revision updated.
- `/health` endpoint response.
- `/predict` endpoint response.

## Troubleshooting

- If image push fails, check Artifact Registry repository name and region.
- If deploy fails, check Cloud Run permissions for the Cloud Build service
  account.
- If `/predict` fails after deployment, confirm the container includes
  `models/predictive_maintenance_model.joblib` and `models/model_metadata.json`.
- If unauthenticated access is disabled, use an identity token for endpoint
  tests.

## Security Notes

- Do not commit `.env` files.
- Do not commit credentials or service account keys.
- Use the Cloud Build service account with least-privilege IAM.
- Use Secret Manager later if secrets are needed.
- Keep project IDs and resource names parameterized.

## Deferred To R7

GitHub triggers are intentionally deferred. R6 only prepares manual Cloud Build
submission.
