from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from vertex_mlops_platform.data_generation import generate_all_datasets
from vertex_mlops_platform.features.feature_store_simulation import build_feature_table
from vertex_mlops_platform.training.evaluate_model import (
    evaluate_classifier,
    write_evaluation_report,
    write_feature_importance,
    write_metrics,
)
from vertex_mlops_platform.training.train_model import (
    load_feature_table,
    save_model,
    train_predictive_maintenance_model,
)


def _generation_config(tmp_path: Path) -> dict[str, object]:
    return {
        "random_seed": 909,
        "number_of_machines": 14,
        "start_date": "2024-01-01",
        "end_date": "2024-01-18",
        "reading_frequency_hours": 12,
        "failure_rate": 0.95,
        "maintenance_rate": 1.5,
        "output_paths": {
            "machines": str(tmp_path / "machines.csv"),
            "sensor_readings": str(tmp_path / "sensor_readings.csv"),
            "maintenance_events": str(tmp_path / "maintenance_events.csv"),
            "failure_events": str(tmp_path / "failure_events.csv"),
        },
    }


def _feature_config(tmp_path: Path) -> dict[str, object]:
    return {
        "rolling_windows_hours": [24, 72],
        "label_window_hours": 168,
        "recent_maintenance_window_days": 30,
        "feature_version": "test-v1",
        "output_feature_table_path": str(tmp_path / "feature_table.csv"),
        "feature_store_metadata_path": str(tmp_path / "feature_store_metadata.json"),
    }


def _model_config(tmp_path: Path) -> dict[str, object]:
    return {
        "training": {
            "random_state": 123,
            "test_size": 0.25,
            "target_column": "failure_within_label_window",
            "feature_table_path": str(tmp_path / "feature_table.csv"),
            "model_type": "RandomForestClassifier",
            "model_output_path": str(tmp_path / "model.joblib"),
            "metrics_output_path": str(tmp_path / "model_metrics.json"),
            "feature_importance_output_path": str(tmp_path / "feature_importance.csv"),
            "evaluation_report_path": str(tmp_path / "evaluation_report.md"),
            "baseline_enabled": True,
            "excluded_columns": [
                "reading_id",
                "machine_id",
                "timestamp",
                "failure_within_label_window",
            ],
        },
        "classifier": {
            "n_estimators": 30,
            "max_depth": 8,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
        },
    }


def _write_feature_table(tmp_path: Path) -> pd.DataFrame:
    datasets = generate_all_datasets(
        config=_generation_config(tmp_path / "source"),
        project_root=".",
    )
    feature_table = build_feature_table(datasets, _feature_config(tmp_path))
    feature_table_path = tmp_path / "feature_table.csv"
    feature_table.to_csv(feature_table_path, index=False)
    return feature_table


def _training_artifacts(tmp_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    feature_table = _write_feature_table(tmp_path)
    config = _model_config(tmp_path)
    artifacts = train_predictive_maintenance_model(feature_table, config)
    return artifacts, config


def test_feature_table_can_be_loaded_for_training(tmp_path) -> None:
    _write_feature_table(tmp_path)

    feature_table = load_feature_table(tmp_path / "feature_table.csv")

    assert not feature_table.empty
    assert "failure_within_label_window" in feature_table.columns


def test_training_pipeline_returns_fitted_model(tmp_path) -> None:
    artifacts, _ = _training_artifacts(tmp_path)

    assert hasattr(artifacts["model"], "predict")
    predictions = artifacts["model"].predict(artifacts["x_test"])
    assert len(predictions) == len(artifacts["y_test"])


def test_model_artifact_can_be_saved(tmp_path) -> None:
    artifacts, config = _training_artifacts(tmp_path)
    model_path = save_model(artifacts["model"], config["training"]["model_output_path"])

    assert model_path.is_file()
    loaded_model = joblib.load(model_path)
    assert hasattr(loaded_model, "predict")


def test_metrics_json_and_required_metrics_can_be_generated(tmp_path) -> None:
    artifacts, config = _training_artifacts(tmp_path)
    metrics = evaluate_classifier(
        artifacts["model"],
        artifacts["x_train"],
        artifacts["x_test"],
        artifacts["y_train"],
        artifacts["y_test"],
        artifacts["feature_columns"],
        baseline_enabled=True,
    )
    output_path = write_metrics(metrics, config["training"]["metrics_output_path"])

    assert output_path.is_file()
    for metric_name in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        assert metric_name in metrics["metrics"]
    assert "confusion_matrix" in metrics


def test_evaluation_report_can_be_generated(tmp_path) -> None:
    artifacts, config = _training_artifacts(tmp_path)
    metrics = evaluate_classifier(
        artifacts["model"],
        artifacts["x_train"],
        artifacts["x_test"],
        artifacts["y_train"],
        artifacts["y_test"],
        artifacts["feature_columns"],
        baseline_enabled=True,
    )
    report_path = write_evaluation_report(
        metrics,
        config["training"]["evaluation_report_path"],
        target_column=config["training"]["target_column"],
        model_output_path=config["training"]["model_output_path"],
    )

    assert report_path.is_file()
    assert "Model Evaluation Report" in report_path.read_text(encoding="utf-8")


def test_baseline_metrics_exist_when_enabled(tmp_path) -> None:
    artifacts, _ = _training_artifacts(tmp_path)
    metrics = evaluate_classifier(
        artifacts["model"],
        artifacts["x_train"],
        artifacts["x_test"],
        artifacts["y_train"],
        artifacts["y_test"],
        artifacts["feature_columns"],
        baseline_enabled=True,
    )

    assert "baseline" in metrics
    assert "accuracy" in metrics["baseline"]["metrics"]


def test_feature_importance_output_is_generated_or_safely_skipped(tmp_path) -> None:
    artifacts, config = _training_artifacts(tmp_path)
    output_path = write_feature_importance(
        artifacts["model"],
        artifacts["feature_columns"],
        config["training"]["feature_importance_output_path"],
    )

    assert output_path is None or output_path.is_file()


def test_training_predictions_are_deterministic_for_same_input(tmp_path) -> None:
    feature_table = _write_feature_table(tmp_path)
    config = _model_config(tmp_path)

    first = train_predictive_maintenance_model(feature_table, config)
    second = train_predictive_maintenance_model(feature_table, config)

    first_predictions = first["model"].predict(first["x_test"])
    second_predictions = second["model"].predict(second["x_test"])
    assert first_predictions.tolist() == second_predictions.tolist()
