"""Rolling window feature engineering for sensor readings."""

from __future__ import annotations

import pandas as pd

ROLLING_AGGREGATIONS = {
    "current_temperature": ["mean", "max", "min", "std"],
    "current_vibration": ["mean", "max", "std"],
    "current_pressure": ["mean", "min", "std"],
    "current_operating_load": ["mean"],
    "current_energy_consumption": ["mean"],
}

FEATURE_NAME_PREFIX = {
    "current_temperature": "temperature",
    "current_vibration": "vibration",
    "current_pressure": "pressure",
    "current_operating_load": "operating_load",
    "current_energy_consumption": "energy_consumption",
}


def add_rolling_window_features(
    features: pd.DataFrame,
    rolling_windows_hours: list[int],
) -> pd.DataFrame:
    """Add time-based rolling features per machine without looking forward."""
    if not rolling_windows_hours:
        return features.copy()

    enriched = features.sort_values(["machine_id", "timestamp"]).copy()
    primary_window = rolling_windows_hours[0]

    for window_hours in rolling_windows_hours:
        window_label = f"{window_hours}h"
        suffix = "" if window_hours == primary_window else f"_{window_label}"
        rolling_features = _rolling_features_for_window(enriched, window_label, suffix)
        enriched = enriched.merge(
            rolling_features,
            on=["machine_id", "timestamp"],
            how="left",
            validate="one_to_one",
        )

    rolling_columns = [
        column
        for column in enriched.columns
        if "_rolling_" in column and enriched[column].dtype.kind in {"f", "i"}
    ]
    enriched[rolling_columns] = enriched[rolling_columns].fillna(0)
    return enriched


def _rolling_features_for_window(
    features: pd.DataFrame,
    window_label: str,
    suffix: str,
) -> pd.DataFrame:
    indexed = features.set_index("timestamp")
    per_machine: list[pd.DataFrame] = []

    for machine_id, machine_frame in indexed.groupby("machine_id", sort=False):
        rolling = machine_frame[list(ROLLING_AGGREGATIONS)].rolling(
            window=window_label,
            min_periods=1,
        )
        aggregated = rolling.agg(ROLLING_AGGREGATIONS)
        aggregated.columns = [
            f"{FEATURE_NAME_PREFIX[source]}_rolling_{aggregation}{suffix}"
            for source, aggregation in aggregated.columns
        ]
        aggregated["machine_id"] = machine_id
        aggregated["timestamp"] = aggregated.index
        per_machine.append(aggregated.reset_index(drop=True))

    return pd.concat(per_machine, ignore_index=True)
