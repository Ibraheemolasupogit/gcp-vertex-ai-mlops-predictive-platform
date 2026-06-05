"""Synthetic predictive maintenance data generation utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from vertex_mlops_platform.data_generation.synthetic_failures import (
    generate_failure_events,
    generate_maintenance_events,
)
from vertex_mlops_platform.data_generation.synthetic_machines import generate_machines
from vertex_mlops_platform.data_generation.synthetic_sensor_readings import generate_sensor_readings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "data_config.yaml"


def load_data_config(config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load data configuration from YAML."""
    with Path(config_path).open() as config_file:
        config = yaml.safe_load(config_file)
    return dict(config["synthetic_generation"])


def generate_all_datasets(
    config: dict[str, Any] | None = None,
    project_root: Path | str = PROJECT_ROOT,
) -> dict[str, pd.DataFrame]:
    """Generate all synthetic predictive maintenance datasets."""
    project_root = Path(project_root)
    config = load_data_config() if config is None else config
    rng = np.random.default_rng(int(config["random_seed"]))

    machines = generate_machines(
        number_of_machines=int(config["number_of_machines"]),
        start_date=str(config["start_date"]),
        rng=rng,
    )
    failures = generate_failure_events(
        machines=machines,
        start_date=str(config["start_date"]),
        end_date=str(config["end_date"]),
        failure_rate=float(config["failure_rate"]),
        rng=rng,
    )
    maintenance = generate_maintenance_events(
        machines=machines,
        failures=failures,
        start_date=str(config["start_date"]),
        end_date=str(config["end_date"]),
        maintenance_rate=float(config["maintenance_rate"]),
        rng=rng,
    )
    readings = generate_sensor_readings(
        machines=machines,
        failures=failures,
        start_date=str(config["start_date"]),
        end_date=str(config["end_date"]),
        reading_frequency_hours=int(config["reading_frequency_hours"]),
        rng=rng,
    )

    datasets = {
        "machines": machines,
        "sensor_readings": readings,
        "maintenance_events": maintenance,
        "failure_events": failures,
    }
    _write_datasets(datasets, config["output_paths"], project_root)
    return datasets


def _write_datasets(
    datasets: dict[str, pd.DataFrame],
    output_paths: dict[str, str],
    project_root: Path,
) -> None:
    for name, dataframe in datasets.items():
        output_path = project_root / output_paths[name]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(output_path, index=False)
