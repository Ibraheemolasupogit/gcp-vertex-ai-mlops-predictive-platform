"""Local CSV loading utilities for synthetic predictive maintenance datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "data_config.yaml"


def load_machines(path: Path | str) -> pd.DataFrame:
    """Load machine inventory data and parse installation dates."""
    return _read_csv(path, parse_dates=["installation_date"])


def load_sensor_readings(path: Path | str) -> pd.DataFrame:
    """Load time-series sensor readings and parse timestamps."""
    return _read_csv(path, parse_dates=["timestamp"])


def load_maintenance_events(path: Path | str) -> pd.DataFrame:
    """Load maintenance event data and parse maintenance dates."""
    return _read_csv(path, parse_dates=["maintenance_date"])


def load_failure_events(path: Path | str) -> pd.DataFrame:
    """Load failure event data and parse failure dates."""
    return _read_csv(path, parse_dates=["failure_date"])


def load_all_datasets(config_path: Path | str | None = None) -> dict[str, pd.DataFrame]:
    """Load all configured sample datasets."""
    config = _load_config(config_path or DEFAULT_CONFIG_PATH)
    output_paths = config["synthetic_generation"]["output_paths"]

    return {
        "machines": load_machines(_resolve_path(output_paths["machines"])),
        "sensor_readings": load_sensor_readings(_resolve_path(output_paths["sensor_readings"])),
        "maintenance_events": load_maintenance_events(
            _resolve_path(output_paths["maintenance_events"])
        ),
        "failure_events": load_failure_events(_resolve_path(output_paths["failure_events"])),
    }


def _read_csv(path: Path | str, parse_dates: list[str]) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Required dataset file not found: {path}")
    return pd.read_csv(path, parse_dates=parse_dates)


def _load_config(config_path: Path | str) -> dict[str, Any]:
    config_path = Path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Data config file not found: {config_path}")
    with config_path.open() as config_file:
        return dict(yaml.safe_load(config_file))


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate
