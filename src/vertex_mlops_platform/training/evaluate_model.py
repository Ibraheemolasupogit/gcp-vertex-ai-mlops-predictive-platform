"""Local model evaluation utilities for predictive maintenance classification."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline


def evaluate_classifier(
    model: Pipeline,
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    feature_columns: list[str],
    baseline_enabled: bool = True,
) -> dict[str, Any]:
    """Evaluate the classifier and optional majority-class baseline."""
    predictions = model.predict(x_test)
    probabilities = _predict_positive_probability(model, x_test)
    metrics = _classification_metrics(y_test, predictions, probabilities)
    metrics.update(
        {
            "positive_class_rate": float(y_test.mean()),
            "prediction_positive_rate": float(np.mean(predictions)),
            "training_rows": int(len(x_train)),
            "test_rows": int(len(x_test)),
            "feature_count": len(feature_columns),
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )

    payload: dict[str, Any] = {
        "model_type": "RandomForestClassifier",
        "metrics": metrics,
        "confusion_matrix": _confusion_matrix_payload(y_test, predictions),
    }
    if baseline_enabled:
        baseline_predictions = np.full(shape=len(y_test), fill_value=int(y_train.mode().iloc[0]))
        payload["baseline"] = {
            "name": "majority_class",
            "metrics": _classification_metrics(y_test, baseline_predictions, None),
            "prediction_positive_rate": float(np.mean(baseline_predictions)),
        }
    return payload


def write_metrics(metrics: dict[str, Any], output_path: Path | str) -> Path:
    """Write model metrics JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return output_path


def write_feature_importance(
    model: Pipeline,
    feature_columns: list[str],
    output_path: Path | str,
) -> Path | None:
    """Write feature importance if the classifier exposes importances."""
    classifier = model.named_steps.get("classifier")
    if classifier is None or not hasattr(classifier, "feature_importances_"):
        return None

    names = _transformed_feature_names(model, feature_columns)
    importances = classifier.feature_importances_
    if len(names) != len(importances):
        names = [f"feature_{index}" for index in range(len(importances))]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    importance = pd.DataFrame(
        {"feature": names, "importance": importances}
    ).sort_values("importance", ascending=False)
    importance.to_csv(output_path, index=False)
    return output_path


def write_evaluation_report(
    metrics: dict[str, Any],
    output_path: Path | str,
    target_column: str,
    model_output_path: Path | str,
) -> Path:
    """Write a concise Markdown evaluation report."""
    model_metrics = metrics["metrics"]
    baseline = metrics.get("baseline", {})
    baseline_metrics = baseline.get("metrics", {})
    matrix = metrics["confusion_matrix"]
    model_roc_auc = _optional_metric(model_metrics, "roc_auc")
    baseline_roc_auc = _optional_metric(baseline_metrics, "roc_auc")
    report = f"""# Model Evaluation Report

## Summary

- Model type: {metrics["model_type"]}
- Target column: `{target_column}`
- Model artifact: `{model_output_path}`
- Training rows: {model_metrics["training_rows"]}
- Test rows: {model_metrics["test_rows"]}
- Feature count: {model_metrics["feature_count"]}

## Key Metrics

| Metric | Model | Majority Baseline |
| --- | ---: | ---: |
| Accuracy | {model_metrics["accuracy"]:.4f} | {_optional_metric(baseline_metrics, "accuracy")} |
| Precision | {model_metrics["precision"]:.4f} | {_optional_metric(baseline_metrics, "precision")} |
| Recall | {model_metrics["recall"]:.4f} | {_optional_metric(baseline_metrics, "recall")} |
| F1 | {model_metrics["f1"]:.4f} | {_optional_metric(baseline_metrics, "f1")} |
| ROC AUC | {model_roc_auc} | {baseline_roc_auc} |

## Confusion Matrix

|  | Predicted 0 | Predicted 1 |
| --- | ---: | ---: |
| Actual 0 | {matrix["true_negative"]} | {matrix["false_positive"]} |
| Actual 1 | {matrix["false_negative"]} | {matrix["true_positive"]} |

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
"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def _classification_metrics(
    y_true: pd.Series,
    predictions: np.ndarray,
    probabilities: np.ndarray | None,
) -> dict[str, float | None]:
    metrics: dict[str, float | None] = {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "roc_auc": None,
    }
    if probabilities is not None and y_true.nunique() > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, probabilities))
    return metrics


def _predict_positive_probability(model: Pipeline, x_test: pd.DataFrame) -> np.ndarray | None:
    if not hasattr(model, "predict_proba"):
        return None
    probabilities = model.predict_proba(x_test)
    if probabilities.shape[1] < 2:
        return None
    return probabilities[:, 1]


def _confusion_matrix_payload(y_true: pd.Series, predictions: np.ndarray) -> dict[str, int]:
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    return {
        "true_negative": int(matrix[0, 0]),
        "false_positive": int(matrix[0, 1]),
        "false_negative": int(matrix[1, 0]),
        "true_positive": int(matrix[1, 1]),
    }


def _transformed_feature_names(model: Pipeline, feature_columns: list[str]) -> list[str]:
    preprocessor = model.named_steps.get("preprocessor")
    if preprocessor is None or not hasattr(preprocessor, "get_feature_names_out"):
        return feature_columns
    return [str(name) for name in preprocessor.get_feature_names_out()]


def _optional_metric(metrics: dict[str, Any], key: str) -> str:
    value = metrics.get(key)
    return "n/a" if value is None else f"{value:.4f}"
