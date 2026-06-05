from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from vertex_mlops_platform.data_generation import generate_all_datasets
from vertex_mlops_platform.ingestion.load_data import (
    load_all_datasets,
    load_failure_events,
    load_machines,
    load_maintenance_events,
    load_sensor_readings,
)


def _config(tmp_path: Path) -> dict[str, object]:
    return {
        "random_seed": 777,
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


def _write_config(tmp_path: Path, generation_config: dict[str, object]) -> Path:
    config_path = tmp_path / "data_config.yaml"
    config_path.write_text(
        yaml.safe_dump({"synthetic_generation": generation_config}),
        encoding="utf-8",
    )
    return config_path


def test_each_dataset_loads_successfully(tmp_path) -> None:
    generation_config = _config(tmp_path)
    generate_all_datasets(config=generation_config, project_root=".")

    machines = load_machines(generation_config["output_paths"]["machines"])
    readings = load_sensor_readings(generation_config["output_paths"]["sensor_readings"])
    maintenance = load_maintenance_events(generation_config["output_paths"]["maintenance_events"])
    failures = load_failure_events(generation_config["output_paths"]["failure_events"])

    assert not machines.empty
    assert not readings.empty
    assert not maintenance.empty
    assert not failures.empty


def test_load_all_datasets_uses_configured_paths(tmp_path) -> None:
    generation_config = _config(tmp_path)
    generate_all_datasets(config=generation_config, project_root=".")
    config_path = _write_config(tmp_path, generation_config)

    datasets = load_all_datasets(config_path=config_path)

    assert set(datasets) == {
        "machines",
        "sensor_readings",
        "maintenance_events",
        "failure_events",
    }
    assert all(not dataframe.empty for dataframe in datasets.values())


def test_date_and_timestamp_columns_are_parsed(tmp_path) -> None:
    generation_config = _config(tmp_path)
    generate_all_datasets(config=generation_config, project_root=".")

    assert pd.api.types.is_datetime64_any_dtype(
        load_machines(generation_config["output_paths"]["machines"])["installation_date"]
    )
    assert pd.api.types.is_datetime64_any_dtype(
        load_sensor_readings(generation_config["output_paths"]["sensor_readings"])["timestamp"]
    )
    assert pd.api.types.is_datetime64_any_dtype(
        load_maintenance_events(generation_config["output_paths"]["maintenance_events"])[
            "maintenance_date"
        ]
    )
    assert pd.api.types.is_datetime64_any_dtype(
        load_failure_events(generation_config["output_paths"]["failure_events"])["failure_date"]
    )


def test_missing_file_raises_clear_error(tmp_path) -> None:
    missing_path = tmp_path / "missing_machines.csv"

    with pytest.raises(FileNotFoundError, match="Required dataset file not found"):
        load_machines(missing_path)
