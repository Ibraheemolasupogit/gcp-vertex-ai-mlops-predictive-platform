"""Local deployment approval gates for model lifecycle governance."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GATE_CONFIG_PATH = PROJECT_ROOT / "configs" / "deployment_gates.yaml"

GateStatus = Literal["pass", "warning", "fail"]
GateSeverity = Literal["low", "medium", "high", "critical"]


@dataclass(frozen=True)
class GateResult:
    """Structured result for a single deployment approval gate."""

    gate_name: str
    category: str
    status: GateStatus
    severity: GateSeverity
    message: str
    threshold: float | int | str | None = None
    observed_value: float | int | str | None = None


def load_gate_config(config_path: Path | str = DEFAULT_GATE_CONFIG_PATH) -> dict[str, Any]:
    """Load deployment gate configuration."""
    config_path = Path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Deployment gate config not found: {config_path}")
    with config_path.open() as config_file:
        return dict(yaml.safe_load(config_file))


def run_approval_gates(
    config: dict[str, Any],
    project_root: Path | str = PROJECT_ROOT,
) -> dict[str, Any]:
    """Run all local approval gates and return deployment readiness."""
    project_root = Path(project_root)
    paths = _resolve_paths(config["paths"], project_root)
    metrics = _read_json_if_exists(paths["metrics_file"])
    data_quality = _read_json_if_exists(paths["data_quality_summary"])

    gate_results: list[GateResult] = []
    gate_results.extend(_artifact_gates(config, paths))
    gate_results.extend(_metric_gates(config, metrics))
    gate_results.extend(_data_quality_gates(config, data_quality))
    gate_results.extend(_governance_gates(config, paths))

    return build_readiness_result(gate_results)


def write_gate_outputs(
    readiness_result: dict[str, Any],
    config: dict[str, Any],
    project_root: Path | str = PROJECT_ROOT,
) -> tuple[Path, Path]:
    """Write JSON gate results and Markdown readiness report."""
    project_root = Path(project_root)
    paths = _resolve_paths(config["paths"], project_root)
    results_path = paths["gate_results_output_path"]
    report_path = paths["readiness_report_output_path"]
    results_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    results_path.write_text(json.dumps(readiness_result, indent=2), encoding="utf-8")
    report_path.write_text(render_readiness_report(readiness_result), encoding="utf-8")
    return results_path, report_path


def build_readiness_result(gate_results: list[GateResult]) -> dict[str, Any]:
    """Build the overall deployment readiness result."""
    blocking_issues = [
        result
        for result in gate_results
        if result.status == "fail" and result.severity in {"high", "critical"}
    ]
    warnings = [result for result in gate_results if result.status == "warning"]

    if blocking_issues:
        overall_status = "Blocked"
        recommended_next_action = "Resolve blocking gate failures before model registry promotion."
    elif warnings:
        overall_status = "Review"
        recommended_next_action = "Review warnings before proceeding to model registry simulation."
    else:
        overall_status = "Ready"
        recommended_next_action = "Proceed to model registry simulation in the next milestone."

    return {
        "overall_status": overall_status,
        "generated_at": datetime.now(UTC).isoformat(),
        "gate_summary": _gate_summary(gate_results),
        "gate_results": [asdict(result) for result in gate_results],
        "blocking_issues": [asdict(result) for result in blocking_issues],
        "warnings": [asdict(result) for result in warnings],
        "recommended_next_action": recommended_next_action,
    }


def render_readiness_report(readiness_result: dict[str, Any]) -> str:
    """Render the deployment readiness report as Markdown."""
    sections = [
        "# Deployment Readiness Report",
        "",
        f"Overall readiness status: **{readiness_result['overall_status']}**",
        "",
        "This is a local-first approval gate report using synthetic data. It does not deploy, "
        "register, or promote a model to GCP.",
        "",
        "## Gate Summary",
        "",
        _summary_table(readiness_result["gate_summary"]),
        "",
    ]

    for category in ["model_metrics", "data_quality", "artifacts", "governance"]:
        category_results = [
            result for result in readiness_result["gate_results"] if result["category"] == category
        ]
        sections.extend(
            [
                f"## {category.replace('_', ' ').title()} Gates",
                "",
                _results_table(category_results),
                "",
            ]
        )

    sections.extend(
        [
            "## Blocking Issues",
            "",
            _issue_list(readiness_result["blocking_issues"], empty_message="No blocking issues."),
            "",
            "## Warnings",
            "",
            _issue_list(readiness_result["warnings"], empty_message="No warnings."),
            "",
            "## Recommended Next Action",
            "",
            readiness_result["recommended_next_action"],
            "",
            "## Conceptual GCP Mapping",
            "",
            "These local gates map conceptually to Vertex AI Pipeline quality checks, "
            "Vertex AI Model Registry approval metadata, and CI/CD promotion controls. "
            "Milestone 6 intentionally does not connect to GCP or perform deployment.",
            "",
        ]
    )
    return "\n".join(sections)


def _artifact_gates(config: dict[str, Any], paths: dict[str, Path]) -> list[GateResult]:
    requirements = config["required_artifacts"]
    checks = [
        ("model_artifact_exists", "require_model_artifact", "model_artifact"),
        ("metrics_file_exists", "require_metrics_file", "metrics_file"),
        ("data_quality_summary_exists", "require_data_quality_summary", "data_quality_summary"),
        ("evaluation_report_exists", "require_evaluation_report", "evaluation_report"),
        ("feature_importance_exists", "require_feature_importance_file", "feature_importance_file"),
    ]
    results = []
    for gate_name, requirement_key, path_key in checks:
        required = bool(requirements[requirement_key])
        exists = paths[path_key].is_file()
        results.append(
            GateResult(
                gate_name=gate_name,
                category="artifacts",
                status="pass" if exists else ("fail" if required else "warning"),
                severity="critical" if required else "medium",
                threshold="required" if required else "optional",
                observed_value=str(paths[path_key]),
                message=(
                    f"Required artifact exists: {paths[path_key]}"
                    if exists
                    else f"Required artifact is missing: {paths[path_key]}"
                ),
            )
        )
    return results


def _metric_gates(
    config: dict[str, Any],
    metrics_payload: dict[str, Any] | None,
) -> list[GateResult]:
    thresholds = config["thresholds"]
    if metrics_payload is None:
        return [
            GateResult(
                "metrics_available",
                "model_metrics",
                "fail",
                "critical",
                "Model metrics JSON is missing or unreadable.",
            )
        ]

    metrics = metrics_payload.get("metrics", {})
    checks = [
        ("f1_score_threshold", "f1", thresholds["minimum_f1_score"]),
        ("recall_threshold", "recall", thresholds["minimum_recall"]),
        ("precision_threshold", "precision", thresholds["minimum_precision"]),
        ("roc_auc_threshold", "roc_auc", thresholds["minimum_roc_auc"]),
    ]
    results = []
    for gate_name, metric_name, threshold in checks:
        observed = metrics.get(metric_name)
        if observed is None:
            results.append(
                GateResult(
                    gate_name,
                    "model_metrics",
                    "warning",
                    "medium",
                    f"{metric_name} is unavailable; review before promotion.",
                    threshold=threshold,
                    observed_value="unavailable",
                )
            )
            continue
        results.append(
            GateResult(
                gate_name,
                "model_metrics",
                "pass" if observed >= threshold else "fail",
                "high",
                f"{metric_name}={observed:.4f} meets threshold {threshold:.4f}."
                if observed >= threshold
                else f"{metric_name}={observed:.4f} is below threshold {threshold:.4f}.",
                threshold=float(threshold),
                observed_value=float(observed),
            )
        )
    return results


def _data_quality_gates(
    config: dict[str, Any],
    data_quality: dict[str, Any] | None,
) -> list[GateResult]:
    thresholds = config["thresholds"]
    if data_quality is None:
        return [
            GateResult(
                "data_quality_summary_available",
                "data_quality",
                "fail",
                "critical",
                "Data quality summary is missing or unreadable.",
            )
        ]

    severity_counts = data_quality.get("issue_counts_by_severity", {})
    critical_count = int(severity_counts.get("critical", 0))
    high_count = int(severity_counts.get("high", 0))
    acceptable_status = data_quality.get("overall_status") in {"passed", "warning"}
    return [
        GateResult(
            "data_quality_overall_status",
            "data_quality",
            "pass" if acceptable_status else "fail",
            "critical",
            "Data quality overall status is acceptable."
            if acceptable_status
            else "Data quality overall status is not acceptable.",
            threshold="passed or warning",
            observed_value=str(data_quality.get("overall_status")),
        ),
        _count_gate(
            "critical_data_quality_issue_limit",
            "data_quality",
            critical_count,
            int(thresholds["maximum_allowed_critical_data_quality_issues"]),
            "critical",
        ),
        _count_gate(
            "high_data_quality_issue_limit",
            "data_quality",
            high_count,
            int(thresholds["maximum_allowed_high_severity_data_quality_issues"]),
            "high",
        ),
    ]


def _governance_gates(config: dict[str, Any], paths: dict[str, Path]) -> list[GateResult]:
    governance = config["governance"]
    results = []
    docs_exist = paths["model_training_documentation"].is_file()
    if governance["require_model_training_documentation"]:
        results.append(
            GateResult(
                "model_training_documentation_exists",
                "governance",
                "pass" if docs_exist else "fail",
                "high",
                "Model training documentation exists."
                if docs_exist
                else "Model training documentation is missing.",
                threshold="required",
                observed_value=str(paths["model_training_documentation"]),
            )
        )

    report_text = _read_text_if_exists(paths["evaluation_report"])
    limitation_present = "synthetic" in report_text.lower() if report_text else False
    if governance["require_synthetic_data_limitation_warning"]:
        results.append(
            GateResult(
                "synthetic_data_limitation_documented",
                "governance",
                "pass" if limitation_present else "warning",
                "medium",
                "Synthetic-data limitation is documented."
                if limitation_present
                else "Synthetic-data limitation should be documented.",
                threshold="synthetic limitation note",
                observed_value="present" if limitation_present else "missing",
            )
        )

    if governance["allow_synthetic_data_warning"]:
        results.append(
            GateResult(
                "synthetic_data_review_warning",
                "governance",
                "warning",
                "low",
                "Model uses synthetic data; review before treating readiness as "
                "production evidence.",
                threshold="human review",
                observed_value="synthetic local MVP",
            )
        )
    return results


def _count_gate(
    gate_name: str,
    category: str,
    observed_count: int,
    maximum_allowed: int,
    severity: GateSeverity,
) -> GateResult:
    passed = observed_count <= maximum_allowed
    return GateResult(
        gate_name=gate_name,
        category=category,
        status="pass" if passed else "fail",
        severity=severity,
        threshold=maximum_allowed,
        observed_value=observed_count,
        message=(
            f"{observed_count} issues are within allowed limit {maximum_allowed}."
            if passed
            else f"{observed_count} issues exceed allowed limit {maximum_allowed}."
        ),
    )


def _resolve_paths(paths: dict[str, str], project_root: Path) -> dict[str, Path]:
    resolved = {}
    for key, value in paths.items():
        candidate = Path(value)
        resolved[key] = candidate if candidate.is_absolute() else project_root / candidate
    return resolved


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _gate_summary(gate_results: list[GateResult]) -> dict[str, int]:
    return {
        "total": len(gate_results),
        "passed": sum(result.status == "pass" for result in gate_results),
        "warnings": sum(result.status == "warning" for result in gate_results),
        "failed": sum(result.status == "fail" for result in gate_results),
    }


def _summary_table(summary: dict[str, int]) -> str:
    values = (
        f"| {summary['total']} | {summary['passed']} | "
        f"{summary['warnings']} | {summary['failed']} |"
    )
    return (
        "| Total | Passed | Warnings | Failed |\n"
        "| ---: | ---: | ---: | ---: |\n"
        f"{values}"
    )


def _results_table(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No gates in this category."
    rows = [
        "| Gate | Status | Severity | Threshold | Observed | Message |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        row_template = (
            "| {gate_name} | {status} | {severity} | {threshold} | "
            "{observed_value} | {message} |"
        )
        rows.append(row_template.format(**result))
    return "\n".join(rows)


def _issue_list(issues: list[dict[str, Any]], empty_message: str) -> str:
    if not issues:
        return empty_message
    return "\n".join(f"- {issue['gate_name']}: {issue['message']}" for issue in issues)
