# Model Evaluation Report

## Summary

- Model type: RandomForestClassifier
- Target column: `failure_within_label_window`
- Model artifact: `models/predictive_maintenance_model.joblib`
- Training rows: 13500
- Test rows: 4500
- Feature count: 50

## Key Metrics

| Metric | Model | Majority Baseline |
| --- | ---: | ---: |
| Accuracy | 0.9971 | 0.9689 |
| Precision | 0.9568 | 0.0000 |
| Recall | 0.9500 | 0.0000 |
| F1 | 0.9534 | 0.0000 |
| ROC AUC | 0.9998 | n/a |

## Confusion Matrix

|  | Predicted 0 | Predicted 1 |
| --- | ---: | ---: |
| Actual 0 | 4354 | 6 |
| Actual 1 | 7 | 133 |

## Predictive Maintenance Interpretation

Recall indicates how many future failure-window examples the model catches.
Higher recall is valuable when missed failures can create downtime or safety
risk. Precision indicates how many alerts are likely to be useful; low precision
can create unnecessary maintenance work.

## Baseline Comparison

The baseline predicts the majority class from the training set. It is included
only as a simple sanity check, not as a benchmarking exercise.

## Limitations

The data is synthetic and local-only. Metrics should be interpreted as workflow
validation, not as evidence of production performance. No deployment gates,
model registry, batch prediction, serving, drift monitoring, or GCP resources
are included in this milestone.

## Next Step

Milestone 6 should add deployment approval gates.
