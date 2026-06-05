from __future__ import annotations

from pathlib import Path

import pandas as pd

from vertex_mlops_platform.data_generation import generate_all_datasets


def _test_config(tmp_path) -> dict[str, object]:
    return {
        "random_seed": 123,
        "number_of_machines": 8,
        "start_date": "2024-01-01",
        "end_date": "2024-01-10",
        "reading_frequency_hours": 12,
        "failure_rate": 0.45,
        "maintenance_rate": 1.2,
        "output_paths": {
            "machines": str(tmp_path / "machines.csv"),
            "sensor_readings": str(tmp_path / "sensor_readings.csv"),
            "maintenance_events": str(tmp_path / "maintenance_events.csv"),
            "failure_events": str(tmp_path / "failure_events.csv"),
        },
    }


def test_all_synthetic_csv_files_can_be_generated(tmp_path) -> None:
    config = _test_config(tmp_path)
    datasets = generate_all_datasets(config=config, project_root=".")

    for dataset_name, output_path in config["output_paths"].items():
        assert Path(output_path).is_file(), f"Missing generated file for {dataset_name}"
        assert not datasets[dataset_name].empty


def test_generated_datasets_have_required_columns(tmp_path) -> None:
    datasets = generate_all_datasets(config=_test_config(tmp_path), project_root=".")

    assert set(
        [
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
        ]
    ).issubset(datasets["machines"].columns)
    assert set(
        [
            "reading_id",
            "machine_id",
            "timestamp",
            "temperature",
            "vibration",
            "pressure",
            "runtime_hours",
            "energy_consumption",
            "operating_load",
        ]
    ).issubset(datasets["sensor_readings"].columns)
    assert set(
        [
            "maintenance_id",
            "machine_id",
            "maintenance_date",
            "maintenance_type",
            "technician_team",
            "downtime_hours",
            "parts_replaced",
            "maintenance_cost",
            "risk_reduction_score",
        ]
    ).issubset(datasets["maintenance_events"].columns)
    assert set(
        [
            "failure_id",
            "machine_id",
            "failure_date",
            "failure_type",
            "severity",
            "root_cause",
            "downtime_hours",
            "repair_cost",
        ]
    ).issubset(datasets["failure_events"].columns)


def test_machine_relationships_and_timestamps_are_valid(tmp_path) -> None:
    datasets = generate_all_datasets(config=_test_config(tmp_path), project_root=".")
    machine_ids = set(datasets["machines"]["machine_id"])

    assert set(datasets["sensor_readings"]["machine_id"]).issubset(machine_ids)
    assert set(datasets["maintenance_events"]["machine_id"]).issubset(machine_ids)
    assert set(datasets["failure_events"]["machine_id"]).issubset(machine_ids)

    assert pd.to_datetime(datasets["sensor_readings"]["timestamp"], errors="coerce").notna().all()
    maintenance_dates = pd.to_datetime(
        datasets["maintenance_events"]["maintenance_date"],
        errors="coerce",
    )
    assert maintenance_dates.notna().all()
    assert pd.to_datetime(datasets["failure_events"]["failure_date"], errors="coerce").notna().all()


def test_sensor_readings_are_in_plausible_ranges(tmp_path) -> None:
    datasets = generate_all_datasets(config=_test_config(tmp_path), project_root=".")
    readings = datasets["sensor_readings"]

    assert readings["temperature"].between(20, 135).all()
    assert readings["vibration"].between(0.1, 18).all()
    assert readings["pressure"].between(50, 280).all()
    assert readings["energy_consumption"].between(5, 95).all()
    assert readings["operating_load"].between(0.25, 1.0).all()
    assert (readings["runtime_hours"] > 0).all()


def test_generation_is_deterministic_with_same_seed(tmp_path) -> None:
    first = generate_all_datasets(config=_test_config(tmp_path / "first"), project_root=".")
    second = generate_all_datasets(config=_test_config(tmp_path / "second"), project_root=".")

    for dataset_name in first:
        pd.testing.assert_frame_equal(first[dataset_name], second[dataset_name])
