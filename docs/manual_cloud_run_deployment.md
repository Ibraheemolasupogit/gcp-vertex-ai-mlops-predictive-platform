# Manual Cloud Run Deployment

R5 prepares a manual deployment path for the Dockerized FastAPI serving API
using Artifact Registry and Cloud Run. This milestone does not deploy anything
automatically and does not add Cloud Build, GitHub triggers, traffic splitting,
or Vertex AI deployment.

## Prerequisites

Required local tools:

- Google Cloud CLI: `gcloud`
- Docker with a running Docker daemon

Required GCP APIs:

- Artifact Registry API
- Cloud Run API
- Cloud Build API if your local Docker or gcloud workflow uses Google-managed
  builds later. R5 does not configure CI/CD.

Authenticate locally with:

```bash
gcloud auth login
gcloud auth application-default login
```

Do not commit credentials, service account keys, or `.env` files.

## Environment Variables

Use the template:

```bash
cp deployment/env.example .env.local
```

Edit `.env.local` locally, then source it:

```bash
set -a
source .env.local
set +a
```

Required variables include `PROJECT_ID`, `REGION`, `ARTIFACT_REPOSITORY`,
`IMAGE_NAME`, `IMAGE_TAG`, `SERVICE_NAME`, `PORT`, and
`ALLOW_UNAUTHENTICATED`.

## Create Artifact Registry Repository

```bash
bash deployment/create_artifact_registry_repo.sh
```

The script checks whether the Docker repository exists and creates it if
needed.

## Build, Tag, And Push Image

```bash
bash deployment/build_tag_push_image.sh
```

The image URI has this form:

```text
${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}
```

## Deploy To Cloud Run

```bash
bash deployment/deploy_cloud_run.sh
```

The script deploys the pushed image with `gcloud run deploy`, sets the container
port to `8080`, and prints the Cloud Run service URL.

## Test The Service

If the service is public:

```bash
export CLOUD_RUN_URL="https://replace-with-service-url"
bash deployment/test_cloud_run_service.sh
```

The script checks:

- `GET /`
- `GET /health`
- `POST /predict`

For authenticated services, add an identity token header manually, for example:

```bash
TOKEN="$(gcloud auth print-identity-token)"
curl -H "Authorization: Bearer ${TOKEN}" "${CLOUD_RUN_URL}/health"
```

## Expected Endpoints

- `/`
- `/health`
- `/predict`
- `/predict-batch`

## Evidence Checklist

Capture later:

- Artifact Registry repository.
- Pushed Docker image and digest.
- Cloud Run service details.
- Cloud Run URL.
- `/health` response.
- `/predict` response.
- Cloud Logging entry.
- Cloud Monitoring chart.

Store real screenshots or redacted command evidence in `evidence/`.

## Cleanup

Use cleanup only when you are done collecting evidence:

```bash
gcloud run services delete "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --platform=managed

gcloud artifacts repositories delete "${ARTIFACT_REPOSITORY}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}"
```

Review prompts carefully before deleting resources.

## Troubleshooting

- If Docker push fails, rerun `gcloud auth configure-docker
  "${REGION}-docker.pkg.dev"`.
- If Cloud Run cannot pull the image, confirm the image URI and repository
  region.
- If `/predict` returns validation errors, confirm the request matches
  `examples/predict_request.json`.
- If the service is private, use an identity token or set
  `ALLOW_UNAUTHENTICATED=true` for demo-only public access.

## Security Notes

- Do not commit `.env.local`, credentials, service account keys, or secrets.
- Prefer local `gcloud auth` for manual deployment.
- Use a least-privilege deployment service account in later production-style
  milestones.
- Keep project IDs parameterized in scripts and docs.
