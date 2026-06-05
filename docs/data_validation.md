# Data Validation

Milestone 3 adds a local ingestion and validation layer for the synthetic
predictive maintenance datasets. The goal is to catch obvious schema,
relationship, timestamp, range, and duplicate issues before later milestones
build feature engineering or model workflows on top of the data.

## Datasets Validated

- `data/sample/machines.csv`
- `data/sample/sensor_readings.csv`
- `data/sample/maintenance_events.csv`
- `data/sample/failure_events.csv`

## Validation Checks

All datasets are checked for required columns, non-empty required fields,
primary key uniqueness, duplicate rows, valid dates or timestamps, and positive
row counts.

Dataset-specific checks include plausible machine baseline ranges, valid
criticality values, valid machine relationships, sensor value ranges,
non-negative runtime and cost fields, valid maintenance types, expected failure
severities, and expected failure types.

## Severity Model

Validation results use three statuses: `pass`, `warning`, and `fail`.
Severities are `low`, `medium`, `high`, and `critical`. Critical and high
failures make the overall validation status `failed`. Warnings, or lower
severity failures, produce an overall `warning` status.

## Data Quality Summary

Running the validation script writes:

```text
outputs/data_quality_summary.json
```

The summary includes overall status, generation timestamp, dataset row and
column counts, individual validation checks, issue counts by severity, and
issue counts by dataset.

## Future GCP Mapping

The local checks are designed to map conceptually to production data quality
patterns such as BigQuery validation queries, Dataflow pipeline checks, and
Vertex AI Pipeline quality gates. Milestone 3 does not connect to GCP, provision
resources, or enforce deployment gates.
