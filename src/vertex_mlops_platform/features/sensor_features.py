"""Sensor and machine lifecycle feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_sensor_features(sensor_readings: pd.DataFrame, machines: pd.DataFrame) -> pd.DataFrame:
    """Create point-in-time sensor, baseline, and lifecycle features."""
    readings = sensor_readings.copy()
    machine_columns = [
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
    machine_profile = machines[machine_columns].copy()
    features = readings.merge(machine_profile, on="machine_id", how="left", validate="many_to_one")

    features["timestamp"] = pd.to_datetime(features["timestamp"], errors="coerce")
    features["installation_date"] = pd.to_datetime(features["installation_date"], errors="coerce")
    features = features.rename(
        columns={
            "temperature": "current_temperature",
            "vibration": "current_vibration",
            "pressure": "current_pressure",
            "runtime_hours": "current_runtime_hours",
            "energy_consumption": "current_energy_consumption",
            "operating_load": "current_operating_load",
        }
    )

    features["temperature_delta_from_machine_baseline"] = (
        features["current_temperature"] - features["baseline_temperature"]
    )
    features["vibration_delta_from_machine_baseline"] = (
        features["current_vibration"] - features["baseline_vibration"]
    )
    features["pressure_delta_from_machine_baseline"] = (
        features["current_pressure"] - features["baseline_pressure"]
    )
    features["temperature_pressure_ratio"] = _safe_divide(
        features["current_temperature"],
        features["current_pressure"],
    )
    features["vibration_load_ratio"] = _safe_divide(
        features["current_vibration"],
        features["current_operating_load"],
    )
    features["energy_per_runtime_hour"] = _safe_divide(
        features["current_energy_consumption"],
        features["current_runtime_hours"],
    )

    features["machine_age_days"] = (
        features["timestamp"] - features["installation_date"]
    ).dt.days.clip(lower=0)
    expected_lifetime_days = features["expected_lifetime_years"] * 365.25
    features["estimated_lifetime_used_ratio"] = _safe_divide(
        features["machine_age_days"],
        expected_lifetime_days,
    ).clip(lower=0, upper=2)

    return features.drop(
        columns=[
            "baseline_temperature",
            "baseline_vibration",
            "baseline_pressure",
            "installation_date",
        ]
    )


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    safe_denominator = denominator.replace(0, np.nan)
    return (numerator / safe_denominator).replace([np.inf, -np.inf], np.nan).fillna(0)
