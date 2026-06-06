# GitHub-Triggered Cloud Build

R7 prepares a GitHub-triggered Cloud Build deployment path. It documents how a
push to the repository can build the Docker image, push it to Artifact Registry,
and deploy the FastAPI service to Cloud Run. This milestone does not create a
real trigger or run GCP commands.

## Purpose

Manual `gcloud builds submit` runs are useful for R6 validation. A GitHub
trigger connects repository activity to Cloud Build so a push to a branch such
as `main` can start the same `cloudbuild.yaml` build/push/deploy workflow.

## Prerequisites

- GitHub repository connected to Google Cloud Build.
- Cloud Build API enabled.
- Artifact Registry API enabled.
- Cloud Run API enabled.
- Artifact Registry repository already created.
- Cloud Build service account with least-privilege access to push images and
  deploy Cloud Run services.

Do not add service account keys or credentials to the repository.

## Trigger Design

Suggested trigger settings:

- Trigger name: `predictive-maintenance-api-main-trigger`
- Branch pattern: `^main$`
- Source repository: this GitHub repository
- Build config file: `cloudbuild.yaml`
- Substitutions:
  - `_PROJECT_ID`
  - `_REGION`
  - `_ARTIFACT_REPOSITORY`
  - `_IMAGE_NAME`
  - `_IMAGE_TAG`
  - `_SERVICE_NAME`
  - `_PORT`
  - `_ALLOW_UNAUTHENTICATED`

Use `deployment/cloud_build_trigger.template.yaml` as a planning template only.

## Console Setup

1. Open Cloud Build in Google Cloud Console.
2. Connect the GitHub repository to Cloud Build.
3. Create a new trigger.
4. Select GitHub as the source.
5. Select the repository.
6. Set branch regex to `^main$`.
7. Set build configuration to `cloudbuild.yaml`.
8. Add substitution values using project-specific values.
9. Select a least-privilege Cloud Build service account if available.
10. Save the trigger.

## Optional gcloud Command

The helper below prints the command by default and only creates the trigger when
`CONFIRM_CREATE_TRIGGER=true` is set:

```bash
bash deployment/create_cloud_build_trigger.sh
```

The command uses placeholders and environment variables only:

```bash
gcloud builds triggers create github \
  --project="${PROJECT_ID}" \
  --name="${TRIGGER_NAME}" \
  --repo-owner="${REPO_OWNER}" \
  --repo-name="${REPO_NAME}" \
  --branch-pattern="${BRANCH_REGEX}" \
  --build-config=cloudbuild.yaml \
  --substitutions="..."
```

## Verify

After creating a real trigger in a real project:

1. Push a commit to GitHub.
2. Confirm the Cloud Build trigger fires automatically.
3. Confirm build logs show Docker build, image push, and Cloud Run deploy.
4. Confirm Artifact Registry has the image from the triggered build.
5. Confirm Cloud Run revision updated.
6. Test `/health`.
7. Test `/predict`.

## Evidence Screenshots

Capture:

- GitHub connection in Cloud Build.
- Trigger configuration.
- Triggered build run from commit.
- Build logs and build steps.
- Artifact Registry pushed image.
- Cloud Run revision created by trigger.
- Endpoint smoke test after trigger.

Store evidence under `evidence/cloud_build_trigger/`.

## Troubleshooting

- If the trigger does not fire, check branch regex and repository connection.
- If substitutions are missing, compare trigger settings with
  `deployment/cloud_build_trigger.template.yaml`.
- If deployment fails, check Cloud Build service account IAM.
- If endpoints fail, inspect Cloud Run logs and verify the model artifacts are
  included in the image.

## Security Notes

- Do not commit `.env` files.
- Do not commit service account keys.
- Use a least-privilege Cloud Build service account.
- Use Secret Manager later if secrets are needed.
- Keep project IDs, repository names, and service accounts parameterized.

## Deferred To R8

Cloud Run revisions and traffic splitting are deferred to R8. R7 only prepares
the GitHub-triggered build/deploy path.
