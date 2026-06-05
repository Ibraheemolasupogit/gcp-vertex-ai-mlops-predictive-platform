"""Maintenance history feature engineering with point-in-time safeguards."""

from __future__ import annotations

import pandas as pd


def add_maintenance_features(
    feature_table: pd.DataFrame,
    maintenance_events: pd.DataFrame,
    recent_maintenance_window_days: int,
) -> pd.DataFrame:
    """Add maintenance features using only events at or before each reading timestamp."""
    readings = feature_table.sort_values(["machine_id", "timestamp"]).copy()
    maintenance = maintenance_events.copy()
    maintenance["maintenance_timestamp"] = pd.to_datetime(
        maintenance["maintenance_date"],
        errors="coerce",
    )
    maintenance = maintenance.sort_values(["machine_id", "maintenance_timestamp"])
    maintenance["cumulative_maintenance_count"] = maintenance.groupby("machine_id").cumcount() + 1
    maintenance["cumulative_maintenance_cost"] = maintenance.groupby("machine_id")[
        "maintenance_cost"
    ].cumsum()
    maintenance["cumulative_downtime_hours"] = maintenance.groupby("machine_id")[
        "downtime_hours"
    ].cumsum()
    maintenance["average_risk_reduction_score"] = maintenance.groupby("machine_id")[
        "risk_reduction_score"
    ].expanding().mean().reset_index(level=0, drop=True)

    maintenance_snapshot = maintenance[
        [
            "machine_id",
            "maintenance_timestamp",
            "maintenance_type",
            "cumulative_maintenance_count",
            "cumulative_maintenance_cost",
            "cumulative_downtime_hours",
            "average_risk_reduction_score",
        ]
    ].rename(columns={"maintenance_type": "last_maintenance_type"})

    merged = pd.merge_asof(
        readings.sort_values("timestamp"),
        maintenance_snapshot.sort_values("maintenance_timestamp"),
        left_on="timestamp",
        right_on="maintenance_timestamp",
        by="machine_id",
        direction="backward",
        allow_exact_matches=True,
    ).sort_values(["machine_id", "timestamp"])

    merged["days_since_last_maintenance"] = (
        merged["timestamp"] - merged["maintenance_timestamp"]
    ).dt.total_seconds() / 86_400
    merged["recent_maintenance_flag"] = (
        merged["days_since_last_maintenance"].le(recent_maintenance_window_days).fillna(False)
    ).astype(int)

    fill_zero_columns = [
        "cumulative_maintenance_count",
        "cumulative_maintenance_cost",
        "cumulative_downtime_hours",
        "average_risk_reduction_score",
    ]
    merged[fill_zero_columns] = merged[fill_zero_columns].fillna(0)
    merged["days_since_last_maintenance"] = merged["days_since_last_maintenance"].fillna(-1)
    merged["last_maintenance_type"] = merged["last_maintenance_type"].fillna("none")

    return merged.drop(columns=["maintenance_timestamp"])
