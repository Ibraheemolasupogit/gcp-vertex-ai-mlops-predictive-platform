"""Local feature table builder and feature store metadata simulation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from vertex_mlops_platform.features.maintenance_features import add_maintenance_features
from vertex_mlops_platform.features.rolling_window_features import add_rolling_window_features
from vertex_mlops_platform.features.sensor_features import build_sensor_features
from vertex_mlops_platform.ingestion.load_data import load_all_datasets

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FEATURE_CONFIG_PATH = PROJECT_ROOT / "configs" / "feature_config.yaml"
LABEL_COLUMN = "failure_within_label_window"


def load_feature_config(config_path: Path | str = DEFAULT_FEATURE_CONFIG_PATH) -> dict[str, Any]:
    """Load feature engineering configuration."""
    with Path(config_path).open() as config_file:
        config = yaml.safe_load(config_file)
    return dict(config["feature_engineering"])


def build_feature_table(
    datasets: dict[str, pd.DataFrame],
    feature_config: dict[str, Any],
) -> pd.DataFrame:
    """Build the model-ready feature table from source datasets."""
    features = build_sensor_features(datasets["sensor_readings"], datasets["machines"])
    features = add_rolling_window_features(
        features,
        rolling_windows_hours=list(feature_config["rolling_windows_hours"]),
    )
    features = add_maintenance_features(
        features,
        datasets["maintenance_events"],
        recent_maintenance_window_days=int(feature_config["recent_maintenance_window_days"]),
    )
    features[LABEL_COLUMN] = create_failure_window_label(
        features[["machine_id", "timestamp"]],
        datasets["failure_events"],
        label_window_hours=int(feature_config["label_window_hours"]),
    )

    features = features.sort_values(["machine_id", "timestamp"]).drop_duplicates(
        subset=["machine_id", "timestamp"],
        keep="first",
    )
    return features.reset_index(drop=True)


def create_failure_window_label(
    entity_timestamps: pd.DataFrame,
    failure_events: pd.DataFrame,
    label_window_hours: int,
) -> pd.Series:
    """Label whether a future failure occurs within the configured window.

    This is the only intentional look-forward step: labels represent the future
    training target. All feature engineering functions use only information at
    or before each sensor reading timestamp.
    """
    failures = failure_events.copy()
    failures["failure_timestamp"] = pd.to_datetime(failures["failure_date"], errors="coerce")
    failure_lookup = {
        machine_id: group["failure_timestamp"].sort_values().to_numpy(dtype="datetime64[ns]")
        for machine_id, group in failures.groupby("machine_id")
    }

    labels: list[int] = []
    label_window = np.timedelta64(label_window_hours, "h")
    for row in entity_timestamps.itertuples(index=False):
        timestamp = np.datetime64(pd.Timestamp(row.timestamp).to_datetime64())
        machine_failures = failure_lookup.get(row.machine_id)
        if machine_failures is None or len(machine_failures) == 0:
            labels.append(0)
            continue
        start_index = np.searchsorted(machine_failures, timestamp, side="right")
        has_failure = (
            start_index < len(machine_failures)
            and machine_failures[start_index] <= timestamp + label_window
        )
        labels.append(int(has_failure))

    return pd.Series(labels, index=entity_timestamps.index, name=LABEL_COLUMN)


def run_feature_engineering(
    data_config_path: Path | str | None = None,
    feature_config_path: Path | str = DEFAULT_FEATURE_CONFIG_PATH,
    project_root: Path | str = PROJECT_ROOT,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load source data, generate features, and write local artifacts."""
    project_root = Path(project_root)
    feature_config = load_feature_config(feature_config_path)
    datasets = load_all_datasets(config_path=data_config_path)
    feature_table = build_feature_table(datasets, feature_config)

    feature_table_path = project_root / feature_config["output_feature_table_path"]
    metadata_path = project_root / feature_config["feature_store_metadata_path"]
    feature_table_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    feature_table.to_csv(feature_table_path, index=False)
    metadata = build_feature_store_metadata(feature_table, feature_config, feature_table_path)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return feature_table, metadata


def build_feature_store_metadata(
    feature_table: pd.DataFrame,
    feature_config: dict[str, Any],
    feature_table_path: Path,
) -> dict[str, object]:
    """Build local feature store metadata for portfolio and pipeline traceability."""
    excluded_columns = {"machine_id", "timestamp", LABEL_COLUMN}
    feature_columns = [column for column in feature_table.columns if column not in excluded_columns]
    return {
        "feature_table_path": str(feature_table_path),
        "generated_at": datetime.now(UTC).isoformat(),
        "row_count": int(len(feature_table)),
        "feature_count": len(feature_columns),
        "entity_keys": ["machine_id"],
        "timestamp_key": "timestamp",
        "label_column": LABEL_COLUMN,
        "feature_version": feature_config["feature_version"],
        "source_datasets": [
            "data/sample/machines.csv",
            "data/sample/sensor_readings.csv",
            "data/sample/maintenance_events.csv",
            "data/sample/failure_events.csv",
        ],
        "feature_groups": {
            "sensor": [
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
            ],
            "rolling_window": [
                column for column in feature_table.columns if "_rolling_" in column
            ],
            "maintenance": [
                "days_since_last_maintenance",
                "last_maintenance_type",
                "cumulative_maintenance_count",
                "cumulative_maintenance_cost",
                "cumulative_downtime_hours",
                "recent_maintenance_flag",
                "average_risk_reduction_score",
            ],
            "machine_lifecycle": [
                "machine_type",
                "manufacturer",
                "site_id",
                "criticality",
                "machine_age_days",
                "expected_lifetime_years",
                "estimated_lifetime_used_ratio",
            ],
            "label": [LABEL_COLUMN],
        },
        "notes": (
            "Local-only feature store simulation. Future milestones can map this "
            "design to BigQuery feature tables and Vertex AI feature management "
            "patterns without adding credentials here."
        ),
    }
