# Feature Engineering

Milestone 4 transforms validated synthetic predictive maintenance datasets into
a local model-ready feature table. The implementation stays local-first and does
not train models, publish features to a cloud service, or connect to GCP.

## Input Datasets

- `data/sample/machines.csv`
- `data/sample/sensor_readings.csv`
- `data/sample/maintenance_events.csv`
- `data/sample/failure_events.csv`

## Feature Groups

Sensor features capture current temperature, vibration, pressure, runtime,
energy consumption, operating load, baseline deltas, and simple ratios.

Rolling window features are calculated per machine using timestamp-aware
rolling windows. The default configuration uses 24-hour features as the primary
unsuffixed feature group and 72-hour features with a `_72h` suffix. This keeps
the MVP useful without making the table unnecessarily wide.

Maintenance features use only maintenance events at or before each sensor
reading timestamp. They include days since last maintenance, last maintenance
type, cumulative maintenance count, cumulative maintenance cost, cumulative
downtime, recent maintenance flag, and average risk reduction score.

Machine lifecycle features include machine type, manufacturer, site, criticality,
age, expected lifetime, and estimated lifetime used ratio.

## Failure-Window Label

`failure_within_label_window` indicates whether a machine has a failure within
the configured future label window after a sensor reading. The label is allowed
to look forward because it is the supervised training target. Feature columns do
not use failure events or future maintenance events.

## Outputs

The feature table is written to:

```text
data/processed/feature_table.csv
```

Local feature store metadata is written to:

```text
outputs/feature_store_metadata.json
```

The metadata captures entity keys, timestamp key, label column, feature version,
source datasets, feature groups, row count, and feature count.

## Future GCP Mapping

The local feature table is designed to map conceptually to BigQuery feature
tables and Vertex AI feature management patterns. Later milestones can add cloud
resources or managed feature pipelines, but Milestone 4 intentionally remains
local-only.
