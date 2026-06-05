from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from vertex_mlops_platform.data_generation import generate_all_datasets
from vertex_mlops_platform.features.feature_store_simulation import (
    LABEL_COLUMN,
    build_feature_table,
    create_failure_window_label,
    run_feature_engineering,
)
from vertex_mlops_platform.features.maintenance_features import add_maintenance_features

REQUIRED_FEATURE_COLUMNS = {
    "machine_id",
    "timestamp",
    "current_temperature",
    "current_vibration",
    "current_pressure",
    "current_runtime_hours",
    "current_energy_consumption",
    "current_operating_load",
    "temperature_delta_from_machine_baseline",
    "vibration_delta_from_machine_baseline",
    "pressure_delta_from_machine_baseline",
    "temperature_pressure_ratio",
    "vibration_load_ratio",
    "energy_per_runtime_hour",
    "machine_type",
    "manufacturer",
    "site_id",
    "criticality",
    "machine_age_days",
    "expected_lifetime_years",
    "estimated_lifetime_used_ratio",
    "days_since_last_maintenance",
    "last_maintenance_type",
    "cumulative_maintenance_count",
    "cumulative_maintenance_cost",
    "cumulative_downtime_hours",
    "recent_maintenance_flag",
    "average_risk_reduction_score",
    LABEL_COLUMN,
}


def _generation_config(tmp_path: Path) -> dict[str, object]:
    return {
        "random_seed": 321,
        "number_of_machines": 10,
        "start_date": "2024-01-01",
        "end_date": "2024-01-12",
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


def _feature_config(tmp_path: Path) -> dict[str, object]:
    return {
        "rolling_windows_hours": [24, 72],
        "label_window_hours": 168,
        "recent_maintenance_window_days": 30,
        "feature_version": "test-v1",
        "output_feature_table_path": str(tmp_path / "feature_table.csv"),
        "feature_store_metadata_path": str(tmp_path / "feature_store_metadata.json"),
    }


def _feature_table(tmp_path: Path) -> pd.DataFrame:
    datasets = generate_all_datasets(config=_generation_config(tmp_path), project_root=".")
    return build_feature_table(datasets, _feature_config(tmp_path))


def test_feature_table_is_generated_with_required_columns(tmp_path) -> None:
    feature_table = _feature_table(tmp_path)

    assert not feature_table.empty
    assert REQUIRED_FEATURE_COLUMNS.issubset(feature_table.columns)


def test_machine_timestamp_rows_are_unique(tmp_path) -> None:
    feature_table = _feature_table(tmp_path)

    assert not feature_table.duplicated(subset=["machine_id", "timestamp"]).any()


def test_rolling_feature_columns_are_present(tmp_path) -> None:
    feature_table = _feature_table(tmp_path)

    assert "temperature_rolling_mean" in feature_table.columns
    assert "temperature_rolling_max" in feature_table.columns
    assert "vibration_rolling_std" in feature_table.columns
    assert "pressure_rolling_min" in feature_table.columns
    assert "operating_load_rolling_mean" in feature_table.columns
    assert "energy_consumption_rolling_mean" in feature_table.columns
    assert "temperature_rolling_mean_72h" in feature_table.columns


def test_maintenance_features_do_not_use_future_events() -> None:
    readings = pd.DataFrame(
        {
            "machine_id": ["M001", "M001", "M001"],
            "timestamp": pd.to_datetime(
                ["2024-01-01 12:00:00", "2024-01-03 12:00:00", "2024-01-06 12:00:00"]
            ),
        }
    )
    maintenance = pd.DataFrame(
        {
            "machine_id": ["M001", "M001"],
            "maintenance_date": pd.to_datetime(["2024-01-03", "2024-01-06"]),
            "maintenance_type": ["preventive", "emergency"],
            "downtime_hours": [2.0, 8.0],
            "maintenance_cost": [500.0, 5000.0],
            "risk_reduction_score": [0.2, 0.7],
        }
    )

    features = add_maintenance_features(readings, maintenance, recent_maintenance_window_days=30)

    first_row = features.iloc[0]
    second_row = features.iloc[1]
    third_row = features.iloc[2]
    assert first_row["last_maintenance_type"] == "none"
    assert first_row["cumulative_maintenance_count"] == 0
    assert second_row["last_maintenance_type"] == "preventive"
    assert second_row["cumulative_maintenance_count"] == 1
    assert third_row["last_maintenance_type"] == "emergency"
    assert third_row["cumulative_maintenance_count"] == 2


def test_failure_label_is_generated_for_controlled_example() -> None:
    entity_timestamps = pd.DataFrame(
        {
            "machine_id": ["M001", "M001", "M001", "M002"],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01 00:00:00",
                    "2024-01-05 00:00:00",
                    "2024-01-15 00:00:00",
                    "2024-01-01 00:00:00",
                ]
            ),
        }
    )
    failures = pd.DataFrame(
        {
            "machine_id": ["M001"],
            "failure_date": pd.to_datetime(["2024-01-07"]),
        }
    )

    labels = create_failure_window_label(entity_timestamps, failures, label_window_hours=168)

    assert labels.tolist() == [1, 1, 0, 0]


def test_feature_store_metadata_json_can_be_generated(tmp_path) -> None:
    generation_config = _generation_config(tmp_path / "source")
    generate_all_datasets(config=generation_config, project_root=".")
    data_config_path = tmp_path / "data_config.yaml"
    data_config_path.write_text(
        yaml.safe_dump({"synthetic_generation": generation_config}),
        encoding="utf-8",
    )
    feature_config = _feature_config(tmp_path)
    feature_config_path = tmp_path / "feature_config.yaml"
    feature_config_path.write_text(
        yaml.safe_dump({"feature_engineering": feature_config}),
        encoding="utf-8",
    )

    feature_table, metadata = run_feature_engineering(
        data_config_path=data_config_path,
        feature_config_path=feature_config_path,
        project_root=".",
    )

    assert Path(feature_config["output_feature_table_path"]).is_file()
    assert Path(feature_config["feature_store_metadata_path"]).is_file()
    assert metadata["row_count"] == len(feature_table)
    assert metadata["label_column"] == LABEL_COLUMN
    assert metadata["feature_version"] == "test-v1"


def test_feature_engineering_is_deterministic_for_same_input(tmp_path) -> None:
    generation_config = _generation_config(tmp_path)
    datasets = generate_all_datasets(config=generation_config, project_root=".")
    feature_config = _feature_config(tmp_path)

    first = build_feature_table(datasets, feature_config)
    second = build_feature_table(datasets, feature_config)

    pd.testing.assert_frame_equal(first, second)
