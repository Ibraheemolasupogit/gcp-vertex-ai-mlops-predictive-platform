from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from vertex_mlops_platform.data_generation import generate_all_datasets
from vertex_mlops_platform.ingestion.validate_schema import (
    ValidationResult,
    build_data_quality_summary,
    calculate_overall_status,
    validate_all_datasets,
    validate_and_write_summary,
)


def _config(tmp_path: Path) -> dict[str, object]:
    return {
        "random_seed": 888,
        "number_of_machines": 12,
        "start_date": "2024-01-01",
        "end_date": "2024-01-14",
        "reading_frequency_hours": 12,
        "failure_rate": 0.9,
        "maintenance_rate": 1.4,
        "output_paths": {
            "machines": str(tmp_path / "machines.csv"),
            "sensor_readings": str(tmp_path / "sensor_readings.csv"),
            "maintenance_events": str(tmp_path / "maintenance_events.csv"),
            "failure_events": str(tmp_path / "failure_events.csv"),
        },
    }


def _datasets(tmp_path: Path) -> dict[str, pd.DataFrame]:
    return generate_all_datasets(config=_config(tmp_path), project_root=".")


def _failing_checks(results: list[ValidationResult]) -> list[ValidationResult]:
    return [result for result in results if result.status == "fail"]


def test_valid_generated_datasets_pass_validation(tmp_path) -> None:
    results = validate_all_datasets(_datasets(tmp_path))

    assert _failing_checks(results) == []
    assert calculate_overall_status(results) == "passed"


def test_missing_required_column_fails_validation(tmp_path) -> None:
    datasets = _datasets(tmp_path)
    datasets["machines"] = datasets["machines"].drop(columns=["criticality"])

    results = validate_all_datasets(datasets)

    assert any(
        result.dataset_name == "machines"
        and result.check_name == "required_columns_present"
        and result.status == "fail"
        for result in results
    )


def test_invalid_machine_id_relationship_fails_validation(tmp_path) -> None:
    datasets = _datasets(tmp_path)
    datasets["sensor_readings"].loc[0, "machine_id"] = "MISSING_MACHINE"

    results = validate_all_datasets(datasets)

    assert any(
        result.dataset_name == "sensor_readings"
        and result.check_name == "machine_id_relationship_valid"
        and result.status == "fail"
        for result in results
    )


def test_duplicate_primary_key_fails_validation(tmp_path) -> None:
    datasets = _datasets(tmp_path)
    duplicate_reading_id = datasets["sensor_readings"].loc[0, "reading_id"]
    datasets["sensor_readings"].loc[1, "reading_id"] = duplicate_reading_id

    results = validate_all_datasets(datasets)

    assert any(
        result.dataset_name == "sensor_readings"
        and result.check_name == "reading_id_unique"
        and result.status == "fail"
        for result in results
    )


def test_out_of_range_sensor_value_fails_validation(tmp_path) -> None:
    datasets = _datasets(tmp_path)
    datasets["sensor_readings"].loc[0, "temperature"] = 999

    results = validate_all_datasets(datasets)

    assert any(
        result.dataset_name == "sensor_readings"
        and result.check_name == "temperature_plausible_range"
        and result.status == "fail"
        for result in results
    )


def test_data_quality_summary_json_can_be_generated(tmp_path) -> None:
    generation_config = _config(tmp_path)
    generate_all_datasets(config=generation_config, project_root=".")
    config_path = tmp_path / "data_config.yaml"
    config_path.write_text(
        yaml.safe_dump({"synthetic_generation": generation_config}),
        encoding="utf-8",
    )
    output_path = tmp_path / "data_quality_summary.json"

    summary = validate_and_write_summary(config_path=config_path, output_path=output_path)

    assert output_path.is_file()
    assert summary["overall_status"] == "passed"
    assert "validation_checks" in summary
    assert "dataset_summaries" in summary


def test_overall_status_logic() -> None:
    warning_result = ValidationResult("machines", "warn", "warning", "medium", "warning")
    high_failure = ValidationResult("machines", "bad", "fail", "high", "failed")
    low_failure = ValidationResult("machines", "low", "fail", "low", "low failure")

    assert calculate_overall_status([]) == "passed"
    assert calculate_overall_status([warning_result]) == "warning"
    assert calculate_overall_status([low_failure]) == "warning"
    assert calculate_overall_status([high_failure]) == "failed"


def test_build_data_quality_summary_counts_issues(tmp_path) -> None:
    datasets = _datasets(tmp_path)
    result = ValidationResult("machines", "example_failure", "fail", "critical", "failed")

    summary = build_data_quality_summary(datasets, [result])

    assert summary["overall_status"] == "failed"
    assert summary["issue_counts_by_severity"] == {"critical": 1}
    assert summary["issue_counts_by_dataset"] == {"machines": 1}
