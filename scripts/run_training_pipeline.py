"""Run local model training and evaluation."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.training.evaluate_model import (  # noqa: E402
    evaluate_classifier,
    write_evaluation_report,
    write_feature_importance,
    write_metrics,
)
from vertex_mlops_platform.training.train_model import (  # noqa: E402
    build_model_metadata,
    load_feature_table,
    load_model_config,
    save_model,
    save_model_metadata,
    train_predictive_maintenance_model,
)


def main() -> int:
    """Train and evaluate the local predictive maintenance classifier."""
    config = load_model_config(PROJECT_ROOT / "configs" / "model_config.yaml")
    training_config = config["training"]
    feature_table_path = PROJECT_ROOT / training_config["feature_table_path"]
    feature_table = load_feature_table(feature_table_path)
    artifacts = train_predictive_maintenance_model(feature_table, config)

    model_path = save_model(artifacts["model"], PROJECT_ROOT / training_config["model_output_path"])
    metadata = build_model_metadata(
        artifacts,
        config,
        model_artifact_path=model_path.relative_to(PROJECT_ROOT),
    )
    save_model_metadata(metadata, PROJECT_ROOT / "models" / "model_metadata.json")
    metrics = evaluate_classifier(
        model=artifacts["model"],
        x_train=artifacts["x_train"],
        x_test=artifacts["x_test"],
        y_train=artifacts["y_train"],
        y_test=artifacts["y_test"],
        feature_columns=artifacts["feature_columns"],
        baseline_enabled=bool(training_config["baseline_enabled"]),
    )
    write_metrics(metrics, PROJECT_ROOT / training_config["metrics_output_path"])
    write_feature_importance(
        artifacts["model"],
        artifacts["feature_columns"],
        PROJECT_ROOT / training_config["feature_importance_output_path"],
    )
    write_evaluation_report(
        metrics,
        PROJECT_ROOT / training_config["evaluation_report_path"],
        target_column=training_config["target_column"],
        model_output_path=model_path.relative_to(PROJECT_ROOT),
    )

    model_metrics = metrics["metrics"]
    print("Training and evaluation complete")
    print(f"Model artifact: {model_path.relative_to(PROJECT_ROOT)}")
    print("Model metadata: models/model_metadata.json")
    print(f"Accuracy: {model_metrics['accuracy']:.4f}")
    print(f"Precision: {model_metrics['precision']:.4f}")
    print(f"Recall: {model_metrics['recall']:.4f}")
    print(f"F1: {model_metrics['f1']:.4f}")
    roc_auc = model_metrics["roc_auc"]
    print(f"ROC AUC: {roc_auc:.4f}" if roc_auc else "ROC AUC: n/a")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
