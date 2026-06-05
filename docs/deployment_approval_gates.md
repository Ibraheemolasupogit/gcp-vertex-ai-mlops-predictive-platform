# Deployment Approval Gates

Milestone 6 adds a local governance layer that decides whether a trained model
is ready to proceed to the next lifecycle stage, needs review, or should be
blocked.

Training success alone is not enough. A model may train successfully while
missing required artifacts, failing quality checks, producing weak recall, or
lacking documentation. Approval gates make those controls explicit before a
future registry or deployment workflow is introduced.

## Gate Categories

- Model metric gates: F1, recall, precision, and ROC AUC thresholds.
- Data quality gates: data quality summary availability, acceptable status, and
  high or critical issue limits.
- Artifact gates: trained model, metrics JSON, data quality summary, evaluation
  report, and feature importance output.
- Governance gates: model training documentation and synthetic-data limitation
  disclosure.

## Readiness Statuses

- `Ready`: all required gates pass with no warnings.
- `Review`: no blocking failures exist, but warnings require human review.
- `Blocked`: required artifacts are missing, critical data quality failures
  exist, or required model metrics fall below thresholds.

Because this project uses synthetic data, the default local result is expected
to require review even when metrics pass.

## Outputs

- `outputs/deployment_gate_results.json`
- `reports/deployment_readiness_report.md`

## Future GCP Mapping

These local gates map conceptually to Vertex AI Pipeline quality checks, Vertex
AI Model Registry approval metadata, and CI/CD promotion controls. Milestone 6
does not connect to GCP, register models, deploy endpoints, or create cloud
resources.

## Limitations

The gate decision is based on synthetic data and local artifacts. It is useful
for demonstrating governance structure, not for claiming production readiness.
