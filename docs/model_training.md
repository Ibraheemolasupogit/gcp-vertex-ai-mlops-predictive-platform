# Model Training

Milestone 5 trains and evaluates a local predictive maintenance classifier using
the model-ready feature table from Milestone 4.

## Input Feature Table

The training stage reads:

```text
data/processed/feature_table.csv
```

The target label is `failure_within_label_window`, which indicates whether a
machine fails inside the configured future label window.

## Train/Test Strategy

The feature table is split into train and test partitions using a deterministic
random state from `configs/model_config.yaml`. The split is stratified when both
target classes are available.

Identifier, timestamp, and target columns are excluded from model features to
avoid obvious leakage.

## Model Choice

The initial model is a `RandomForestClassifier`. It is a practical baseline for
mixed numeric and categorical tabular data, works well with nonlinear patterns,
and exposes feature importances for inspection.

The sklearn pipeline uses median imputation for numeric features, most-frequent
imputation plus one-hot encoding for categorical features, and class weighting
to reduce the effect of imbalanced failure labels.

## Evaluation Metrics

Evaluation writes accuracy, precision, recall, F1, ROC AUC when available,
confusion matrix, positive class rate, prediction positive rate, train/test row
counts, and feature count.

A majority-class baseline is included as a simple sanity check. It is not a
benchmarking suite.

## Outputs

- `models/predictive_maintenance_model.joblib`
- `outputs/model_metrics.json`
- `outputs/feature_importance.csv`
- `reports/evaluation_report.md`

## Future GCP Mapping

This local training stage maps conceptually to Vertex AI Training jobs and
Vertex AI Experiments-style metric tracking. Milestone 5 does not connect to
GCP, create experiments, register models, deploy services, or add approval
gates.

## Limitations

The data is fully synthetic. Metrics are useful for validating the workflow and
showing model-development structure, not for claiming production performance.
