"""Schema and data quality validation for local predictive maintenance datasets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import pandas as pd

from vertex_mlops_platform.ingestion.load_data import load_all_datasets

ValidationStatus = Literal["pass", "warning", "fail"]
ValidationSeverity = Literal["low", "medium", "high", "critical"]

REQUIRED_COLUMNS = {
    "machines": [
        "machine_id",
        "machine_type",
        "installation_date",
        "site_id",
        "manufacturer",
        "expected_lifetime_years",
        "criticality",
        "baseline_temperature",
        "baseline_vibration",
        "baseline_pressure",
    ],
    "sensor_readings": [
        "reading_id",
        "machine_id",
        "timestamp",
        "temperature",
        "vibration",
        "pressure",
        "runtime_hours",
        "energy_consumption",
        "operating_load",
    ],
    "maintenance_events": [
        "maintenance_id",
        "machine_id",
        "maintenance_date",
        "maintenance_type",
        "technician_team",
        "downtime_hours",
        "parts_replaced",
        "maintenance_cost",
        "risk_reduction_score",
    ],
    "failure_events": [
        "failure_id",
        "machine_id",
        "failure_date",
        "failure_type",
        "severity",
        "root_cause",
        "downtime_hours",
        "repair_cost",
    ],
}

PRIMARY_KEYS = {
    "machines": "machine_id",
    "sensor_readings": "reading_id",
    "maintenance_events": "maintenance_id",
    "failure_events": "failure_id",
}

DATE_COLUMNS = {
    "machines": ["installation_date"],
    "sensor_readings": ["timestamp"],
    "maintenance_events": ["maintenance_date"],
    "failure_events": ["failure_date"],
}

EXPECTED_VALUES = {
    "criticality": {"low", "medium", "high", "critical"},
    "maintenance_type": {"preventive", "corrective", "inspection", "emergency"},
    "severity": {"minor", "moderate", "major", "critical"},
    "failure_type": {
        "overheating",
        "bearing_wear",
        "pressure_system_failure",
        "electrical_fault",
        "vibration_related_failure",
    },
}


@dataclass(frozen=True)
class ValidationResult:
    """Single validation check result."""

    dataset_name: str
    check_name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    affected_rows: int | None = None


def validate_all_datasets(datasets: dict[str, pd.DataFrame]) -> list[ValidationResult]:
    """Run all schema and quality checks across the four datasets."""
    results: list[ValidationResult] = []
    machines = datasets.get("machines", pd.DataFrame())
    machine_ids = set(machines["machine_id"]) if "machine_id" in machines.columns else set()

    for dataset_name, dataframe in datasets.items():
        results.extend(_validate_common(dataset_name, dataframe))

    if "machines" in datasets:
        results.extend(_validate_machines(datasets["machines"]))
    if "sensor_readings" in datasets:
        results.extend(_validate_sensor_readings(datasets["sensor_readings"], machine_ids))
    if "maintenance_events" in datasets:
        results.extend(_validate_maintenance_events(datasets["maintenance_events"], machine_ids))
    if "failure_events" in datasets:
        results.extend(_validate_failure_events(datasets["failure_events"], machine_ids))

    return results


def validate_and_write_summary(
    config_path: Path | str | None = None,
    output_path: Path | str = Path("outputs/data_quality_summary.json"),
) -> dict[str, object]:
    """Load configured datasets, validate them, and write a JSON summary."""
    datasets = load_all_datasets(config_path=config_path)
    results = validate_all_datasets(datasets)
    summary = build_data_quality_summary(datasets, results)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def build_data_quality_summary(
    datasets: dict[str, pd.DataFrame],
    results: list[ValidationResult],
) -> dict[str, object]:
    """Build a serializable data quality summary."""
    validation_checks = [asdict(result) for result in results]
    return {
        "overall_status": calculate_overall_status(results),
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_summaries": {
            name: {"row_count": int(len(dataframe)), "column_count": int(len(dataframe.columns))}
            for name, dataframe in datasets.items()
        },
        "validation_checks": validation_checks,
        "issue_counts_by_severity": _issue_counts_by(results, "severity"),
        "issue_counts_by_dataset": _issue_counts_by(results, "dataset_name"),
    }


def calculate_overall_status(results: list[ValidationResult]) -> str:
    """Calculate the overall validation status from check results."""
    high_failure_exists = any(
        result.status == "fail" and result.severity in {"critical", "high"} for result in results
    )
    if high_failure_exists:
        return "failed"
    if any(result.status == "warning" for result in results):
        return "warning"
    if any(result.status == "fail" for result in results):
        return "warning"
    return "passed"


def _validate_common(dataset_name: str, dataframe: pd.DataFrame) -> list[ValidationResult]:
    results = [
        _result(
            dataset_name,
            "row_count_positive",
            len(dataframe) > 0,
            "critical",
            f"{dataset_name} contains rows.",
            f"{dataset_name} is empty.",
            affected_rows=0 if len(dataframe) > 0 else len(dataframe),
        )
    ]

    required_columns = REQUIRED_COLUMNS[dataset_name]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    results.append(
        ValidationResult(
            dataset_name=dataset_name,
            check_name="required_columns_present",
            status="pass" if not missing_columns else "fail",
            severity="critical",
            message=(
                "All required columns are present."
                if not missing_columns
                else f"Missing required columns: {', '.join(missing_columns)}."
            ),
            affected_rows=None,
        )
    )
    if missing_columns:
        return results

    for column in required_columns:
        fully_empty = dataframe[column].isna().all()
        results.append(
            _result(
                dataset_name,
                f"{column}_not_fully_empty",
                not fully_empty,
                "high",
                f"{column} is not fully empty.",
                f"{column} is fully empty.",
                affected_rows=int(dataframe[column].isna().sum()),
            )
        )

    primary_key = PRIMARY_KEYS[dataset_name]
    duplicate_key_count = int(dataframe[primary_key].duplicated().sum())
    results.append(
        _result(
            dataset_name,
            f"{primary_key}_unique",
            duplicate_key_count == 0,
            "critical",
            f"{primary_key} is unique.",
            f"{primary_key} has duplicate values.",
            affected_rows=duplicate_key_count,
        )
    )

    duplicate_row_count = int(dataframe.duplicated().sum())
    results.append(
        _result(
            dataset_name,
            "no_duplicate_rows",
            duplicate_row_count == 0,
            "medium",
            "No duplicate rows found.",
            "Duplicate rows found.",
            affected_rows=duplicate_row_count,
        )
    )

    for date_column in DATE_COLUMNS[dataset_name]:
        invalid_dates = _invalid_date_count(dataframe[date_column])
        results.append(
            _result(
                dataset_name,
                f"{date_column}_valid",
                invalid_dates == 0,
                "high",
                f"{date_column} contains valid dates.",
                f"{date_column} contains invalid dates.",
                affected_rows=invalid_dates,
            )
        )

    return results


def _validate_machines(dataframe: pd.DataFrame) -> list[ValidationResult]:
    if _missing_any(dataframe, REQUIRED_COLUMNS["machines"]):
        return []
    return [
        _positive_check(dataframe, "machines", "expected_lifetime_years", "high"),
        _range_check(dataframe, "machines", "baseline_temperature", 20, 135, "high"),
        _range_check(dataframe, "machines", "baseline_vibration", 0.1, 18, "high"),
        _range_check(dataframe, "machines", "baseline_pressure", 50, 280, "high"),
        _expected_values_check(
            dataframe,
            "machines",
            "criticality",
            EXPECTED_VALUES["criticality"],
        ),
    ]


def _validate_sensor_readings(
    dataframe: pd.DataFrame,
    machine_ids: set[object],
) -> list[ValidationResult]:
    if _missing_any(dataframe, REQUIRED_COLUMNS["sensor_readings"]):
        return []
    return [
        _relationship_check(dataframe, "sensor_readings", machine_ids),
        _range_check(dataframe, "sensor_readings", "temperature", 20, 135, "high"),
        _range_check(dataframe, "sensor_readings", "vibration", 0.1, 18, "high"),
        _range_check(dataframe, "sensor_readings", "pressure", 50, 280, "high"),
        _non_negative_check(dataframe, "sensor_readings", "runtime_hours", "high"),
        _non_negative_check(dataframe, "sensor_readings", "energy_consumption", "high"),
        _range_check(dataframe, "sensor_readings", "operating_load", 0.25, 1.0, "high"),
    ]


def _validate_maintenance_events(
    dataframe: pd.DataFrame,
    machine_ids: set[object],
) -> list[ValidationResult]:
    if _missing_any(dataframe, REQUIRED_COLUMNS["maintenance_events"]):
        return []
    return [
        _relationship_check(dataframe, "maintenance_events", machine_ids),
        _non_negative_check(dataframe, "maintenance_events", "downtime_hours", "high"),
        _non_negative_check(dataframe, "maintenance_events", "maintenance_cost", "high"),
        _range_check(dataframe, "maintenance_events", "risk_reduction_score", 0.0, 1.0, "high"),
        _expected_values_check(
            dataframe,
            "maintenance_events",
            "maintenance_type",
            EXPECTED_VALUES["maintenance_type"],
        ),
    ]


def _validate_failure_events(
    dataframe: pd.DataFrame,
    machine_ids: set[object],
) -> list[ValidationResult]:
    if _missing_any(dataframe, REQUIRED_COLUMNS["failure_events"]):
        return []
    return [
        _relationship_check(dataframe, "failure_events", machine_ids),
        _non_negative_check(dataframe, "failure_events", "downtime_hours", "high"),
        _non_negative_check(dataframe, "failure_events", "repair_cost", "high"),
        _expected_values_check(
            dataframe,
            "failure_events",
            "severity",
            EXPECTED_VALUES["severity"],
        ),
        _expected_values_check(
            dataframe,
            "failure_events",
            "failure_type",
            EXPECTED_VALUES["failure_type"],
        ),
    ]


def _relationship_check(
    dataframe: pd.DataFrame,
    dataset_name: str,
    machine_ids: set[object],
) -> ValidationResult:
    invalid_count = int((~dataframe["machine_id"].isin(machine_ids)).sum())
    return _result(
        dataset_name,
        "machine_id_relationship_valid",
        invalid_count == 0,
        "critical",
        "All machine_id values exist in machines.",
        "Found machine_id values that do not exist in machines.",
        affected_rows=invalid_count,
    )


def _range_check(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    minimum: float,
    maximum: float,
    severity: ValidationSeverity,
) -> ValidationResult:
    invalid_values = ~dataframe[column].between(minimum, maximum) | dataframe[column].isna()
    invalid_count = int(invalid_values.sum())
    return _result(
        dataset_name,
        f"{column}_plausible_range",
        invalid_count == 0,
        severity,
        f"{column} values are within {minimum} and {maximum}.",
        f"{column} has values outside {minimum} and {maximum}.",
        affected_rows=invalid_count,
    )


def _positive_check(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    severity: ValidationSeverity,
) -> ValidationResult:
    invalid_count = int(((dataframe[column] <= 0) | dataframe[column].isna()).sum())
    return _result(
        dataset_name,
        f"{column}_positive",
        invalid_count == 0,
        severity,
        f"{column} values are positive.",
        f"{column} has non-positive values.",
        affected_rows=invalid_count,
    )


def _non_negative_check(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    severity: ValidationSeverity,
) -> ValidationResult:
    invalid_count = int(((dataframe[column] < 0) | dataframe[column].isna()).sum())
    return _result(
        dataset_name,
        f"{column}_non_negative",
        invalid_count == 0,
        severity,
        f"{column} values are non-negative.",
        f"{column} has negative values.",
        affected_rows=invalid_count,
    )


def _expected_values_check(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    expected_values: set[str],
) -> ValidationResult:
    invalid_count = int((~dataframe[column].isin(expected_values) | dataframe[column].isna()).sum())
    return _result(
        dataset_name,
        f"{column}_expected_values",
        invalid_count == 0,
        "high",
        f"{column} contains expected values.",
        f"{column} contains unexpected values.",
        affected_rows=invalid_count,
    )


def _result(
    dataset_name: str,
    check_name: str,
    condition: bool,
    severity: ValidationSeverity,
    pass_message: str,
    fail_message: str,
    affected_rows: int | None,
) -> ValidationResult:
    return ValidationResult(
        dataset_name=dataset_name,
        check_name=check_name,
        status="pass" if condition else "fail",
        severity=severity,
        message=pass_message if condition else fail_message,
        affected_rows=affected_rows,
    )


def _missing_any(dataframe: pd.DataFrame, columns: list[str]) -> bool:
    return any(column not in dataframe.columns for column in columns)


def _invalid_date_count(series: pd.Series) -> int:
    parsed = pd.to_datetime(series, errors="coerce")
    return int(parsed.isna().sum())


def _issue_counts_by(results: list[ValidationResult], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        if result.status == "pass":
            continue
        key = str(getattr(result, field_name))
        counts[key] = counts.get(key, 0) + 1
    return counts
