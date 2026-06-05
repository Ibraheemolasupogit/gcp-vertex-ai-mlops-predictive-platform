from __future__ import annotations

import json
from pathlib import Path

from vertex_mlops_platform.training.approval_gates import (
    build_readiness_result,
    run_approval_gates,
    write_gate_outputs,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_metrics() -> dict[str, object]:
    return {
        "model_type": "RandomForestClassifier",
        "metrics": {
            "accuracy": 0.90,
            "precision": 0.80,
            "recall": 0.82,
            "f1": 0.81,
            "roc_auc": 0.88,
            "training_rows": 100,
            "test_rows": 40,
            "feature_count": 12,
        },
        "confusion_matrix": {
            "true_negative": 30,
            "false_positive": 2,
            "false_negative": 3,
            "true_positive": 5,
        },
    }


def _base_quality() -> dict[str, object]:
    return {
        "overall_status": "passed",
        "issue_counts_by_severity": {},
        "validation_checks": [],
    }


def _config(tmp_path: Path, allow_synthetic_warning: bool = True) -> dict[str, object]:
    return {
        "thresholds": {
            "minimum_f1_score": 0.70,
            "minimum_recall": 0.70,
            "minimum_precision": 0.60,
            "minimum_roc_auc": 0.75,
            "maximum_allowed_high_severity_data_quality_issues": 0,
            "maximum_allowed_critical_data_quality_issues": 0,
        },
        "required_artifacts": {
            "require_model_artifact": True,
            "require_evaluation_report": True,
            "require_metrics_file": True,
            "require_feature_importance_file": True,
            "require_data_quality_summary": True,
        },
        "paths": {
            "model_artifact": str(tmp_path / "model.joblib"),
            "metrics_file": str(tmp_path / "model_metrics.json"),
            "data_quality_summary": str(tmp_path / "data_quality_summary.json"),
            "evaluation_report": str(tmp_path / "evaluation_report.md"),
            "feature_importance_file": str(tmp_path / "feature_importance.csv"),
            "model_training_documentation": str(tmp_path / "model_training.md"),
            "gate_results_output_path": str(tmp_path / "deployment_gate_results.json"),
            "readiness_report_output_path": str(tmp_path / "deployment_readiness_report.md"),
        },
        "governance": {
            "allow_synthetic_data_warning": allow_synthetic_warning,
            "require_model_training_documentation": True,
            "require_synthetic_data_limitation_warning": True,
        },
    }


def _write_valid_artifacts(tmp_path: Path) -> None:
    _write_json(tmp_path / "model_metrics.json", _base_metrics())
    _write_json(tmp_path / "data_quality_summary.json", _base_quality())
    (tmp_path / "model.joblib").write_bytes(b"model")
    (tmp_path / "evaluation_report.md").write_text(
        "Synthetic data limitation noted.",
        encoding="utf-8",
    )
    (tmp_path / "feature_importance.csv").write_text(
        "feature,importance\nx,0.1\n",
        encoding="utf-8",
    )
    (tmp_path / "model_training.md").write_text(
        "Training docs for synthetic data.",
        encoding="utf-8",
    )


def test_approval_gates_run_with_valid_outputs(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    readiness = run_approval_gates(_config(tmp_path), project_root=".")

    assert readiness["overall_status"] in {"Ready", "Review", "Blocked"}
    assert readiness["gate_summary"]["total"] > 0


def test_required_gate_result_fields_exist(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    readiness = run_approval_gates(_config(tmp_path), project_root=".")
    first_result = readiness["gate_results"][0]

    assert {
        "gate_name",
        "category",
        "status",
        "severity",
        "threshold",
        "observed_value",
        "message",
    }.issubset(first_result)


def test_missing_model_artifact_causes_blocked_status(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    (tmp_path / "model.joblib").unlink()

    readiness = run_approval_gates(_config(tmp_path), project_root=".")

    assert readiness["overall_status"] == "Blocked"
    assert any(
        issue["gate_name"] == "model_artifact_exists"
        for issue in readiness["blocking_issues"]
    )


def test_metric_below_threshold_causes_blocked_status(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    metrics = _base_metrics()
    metrics["metrics"]["recall"] = 0.2
    _write_json(tmp_path / "model_metrics.json", metrics)

    readiness = run_approval_gates(_config(tmp_path), project_root=".")

    assert readiness["overall_status"] == "Blocked"
    assert any(result["gate_name"] == "recall_threshold" for result in readiness["blocking_issues"])


def test_critical_data_quality_issue_causes_blocked_status(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    quality = _base_quality()
    quality["issue_counts_by_severity"] = {"critical": 1}
    _write_json(tmp_path / "data_quality_summary.json", quality)

    readiness = run_approval_gates(_config(tmp_path), project_root=".")

    assert readiness["overall_status"] == "Blocked"
    assert any(
        issue["gate_name"] == "critical_data_quality_issue_limit"
        for issue in readiness["blocking_issues"]
    )


def test_warnings_can_produce_review_status(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    readiness = run_approval_gates(
        _config(tmp_path, allow_synthetic_warning=True),
        project_root=".",
    )

    assert readiness["overall_status"] == "Review"
    assert readiness["warnings"]


def test_outputs_can_be_generated(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    config = _config(tmp_path)
    readiness = run_approval_gates(config, project_root=".")

    results_path, report_path = write_gate_outputs(readiness, config, project_root=".")

    assert results_path.is_file()
    assert report_path.is_file()
    assert "Deployment Readiness Report" in report_path.read_text(encoding="utf-8")


def test_overall_status_is_allowed_value(tmp_path) -> None:
    _write_valid_artifacts(tmp_path)
    readiness = run_approval_gates(_config(tmp_path), project_root=".")

    assert readiness["overall_status"] in {"Ready", "Review", "Blocked"}


def test_build_readiness_result_ready_without_warnings_or_failures() -> None:
    readiness = build_readiness_result([])

    assert readiness["overall_status"] == "Ready"
