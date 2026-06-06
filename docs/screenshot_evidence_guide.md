# Screenshot Evidence Guide

Real deployment screenshots should be stored under `evidence/` in the folder
that matches the milestone or system being demonstrated. Do not add fake
screenshots.

Do not add fake screenshots.

## Naming Convention

Use clear, lowercase filenames with milestone and service context:

```text
r05-artifact-registry-image.png
r05-cloud-run-health-response.png
r08-cloud-run-traffic-split-90-10.png
r10-vertex-online-prediction-response.png
```

Prefer `.png` for screenshots. If command output is captured, use `.txt` or
`.md` and redact sensitive values.

## Recommended Screenshot Groups

- Cloud Run: service page, service URL, `/health`, `/predict`.
- Artifact Registry: repository and pushed image digest.
- Cloud Build: successful manual build and deploy steps.
- GitHub trigger: trigger configuration and triggered build logs.
- Traffic splitting: revisions, stable/candidate traffic split, rollback.
- Vertex AI training: custom training job and logs.
- Model Registry: model entry, version alias, metadata, labels.
- Vertex AI endpoint: endpoint ID, deployed model, online prediction response.
- Batch prediction: batch job and Cloud Storage output.
- Composer / Airflow: environment page, DAG graph, DAG run, task logs.
- Vertex AI Pipelines: pipeline run, graph, component logs, artifacts.
- Monitoring/logging: Cloud Run logs, Cloud Monitoring charts, Vertex logs.

## Redaction Guidance

Before committing evidence:

- Redact real project IDs if they are not intended for public display.
- Redact service account emails when appropriate.
- Never include service account keys, tokens, cookies, or private credentials.
- Avoid screenshots that expose billing data, private user identities, or
  unrelated cloud resources.

## README References

Reference evidence from the README only after real screenshots are captured.
Use concise links to the relevant `evidence/` folder rather than embedding large
images directly in the main README.
