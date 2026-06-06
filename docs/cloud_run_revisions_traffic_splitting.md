# Cloud Run Revisions And Traffic Splitting

R8 prepares a Cloud Run revisions and traffic splitting workflow for the
FastAPI model serving API. It does not run deployment commands, update live
traffic, create screenshots, or add Vertex AI deployment.

## Purpose Of Cloud Run Revisions

Each Cloud Run deployment creates an immutable revision. A revision captures the
container image, environment, service configuration, and runtime settings used
for that deployment. For model serving, revisions make it possible to compare a
stable model-serving container against a candidate model-serving container.

## Why Traffic Splitting Matters

Traffic splitting supports safer MLOps rollout patterns. Instead of sending all
prediction traffic to a new model-serving container immediately, a team can send
a small percentage to a candidate revision, inspect logs and metrics, then
increase or roll back traffic.

## Deployment Patterns

- Normal deployment: a new revision receives all traffic after deployment.
- Revision-based deployment: multiple revisions exist, and traffic can be
  assigned explicitly.
- Blue/green deployment: traffic moves from a stable revision to a candidate
  revision after validation.
- Canary deployment: a small percentage of traffic, such as 10%, goes to the
  candidate revision first.
- A/B-style traffic split: two revisions receive traffic at the same time for
  comparison, for example 90% stable and 10% candidate.

## New Model-Serving Revision

A new model-serving container version becomes a new Cloud Run revision when the
service is deployed with a new image or configuration. The container may contain
an updated model artifact, metadata, code, or runtime dependency set.

## Traffic Split Example

Example allocation:

- 90% stable revision
- 10% candidate revision

The dry-run helper prints a parameterized command:

```bash
bash deployment/update_cloud_run_traffic_split.sh
```

The command uses:

```text
gcloud run services update-traffic SERVICE_NAME --to-revisions=stable=90,candidate=10
```

It only runs when `CONFIRM_UPDATE_TRAFFIC=true` is explicitly set.

## Verify

Capture evidence from:

- Cloud Run revisions page.
- Traffic allocation view.
- Service URL.
- `/health` endpoint.
- `/predict` endpoint.
- Cloud Logging.
- Cloud Monitoring.

Use:

```bash
bash deployment/describe_cloud_run_revisions.sh
```

This helper is dry-run by default and only runs when
`CONFIRM_DESCRIBE_REVISIONS=true` is set.

## Rollback

Rollback can route all traffic back to the stable revision. The dry-run helper
supports rollback planning:

```bash
ROLLBACK_TO_STABLE=true bash deployment/update_cloud_run_traffic_split.sh
```

It prints a command that routes 100% of traffic to `STABLE_REVISION`. It only
executes when `CONFIRM_UPDATE_TRAFFIC=true` is also set.

## Evidence Screenshots

Store real evidence under:

```text
evidence/cloud_run_traffic_splitting/
```

Capture:

- Cloud Run revisions list.
- Stable revision details.
- Candidate revision details.
- 90/10 or similar canary traffic allocation.
- Endpoint checks during the split.
- Cloud Logging entries.
- Rollback confirmation.
- Cloud Monitoring chart if available.

Do not add fake screenshots.

## Troubleshooting

- If a revision name is wrong, inspect revisions before updating traffic.
- If traffic percentages do not sum to 100, fix the env values before running.
- If endpoint checks fail, review Cloud Run logs and confirm the correct image
  is attached to the candidate revision.
- If rollback is needed, route 100% traffic to the stable revision.

## Security Notes

- Do not commit `.env` files.
- Do not commit service account keys or secrets.
- Keep project ID, service name, region, and revision names parameterized.
- Use least-privilege IAM for anyone permitted to update Cloud Run traffic.

## Deferred Work

Vertex AI deployment is deferred to later milestones. R8 only prepares Cloud Run
revision and traffic split evidence planning.
