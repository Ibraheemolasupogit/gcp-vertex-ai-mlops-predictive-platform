"""Synthetic sensor reading generation linked to machine and failure behavior."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_sensor_readings(
    machines: pd.DataFrame,
    failures: pd.DataFrame,
    start_date: str,
    end_date: str,
    reading_frequency_hours: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate sensor readings with pre-failure degradation patterns."""
    timestamps = pd.date_range(
        start=pd.Timestamp(start_date),
        end=pd.Timestamp(end_date),
        freq=f"{reading_frequency_hours}h",
        inclusive="left",
    )
    failure_lookup = _failure_lookup(failures)
    rows: list[dict[str, object]] = []
    reading_id = 1

    for machine in machines.to_dict("records"):
        machine_id = str(machine["machine_id"])
        machine_type = str(machine["machine_type"])
        type_load_factor = _load_factor(machine_type)
        runtime_hours = float(rng.uniform(1000, 12000))

        for timestamp in timestamps:
            operating_load = float(np.clip(rng.normal(type_load_factor, 0.11), 0.25, 1.0))
            runtime_hours += reading_frequency_hours * operating_load
            degradation = _pre_failure_degradation(timestamp, failure_lookup.get(machine_id, []))
            daily_cycle = np.sin(2 * np.pi * timestamp.hour / 24)

            temperature = (
                float(machine["baseline_temperature"])
                + 5.5 * operating_load
                + 1.8 * daily_cycle
                + degradation["temperature"]
                + rng.normal(0, 1.7)
            )
            vibration = (
                float(machine["baseline_vibration"])
                + 0.8 * operating_load
                + degradation["vibration"]
                + abs(rng.normal(0, 0.35))
            )
            pressure = (
                float(machine["baseline_pressure"])
                + 8.0 * operating_load
                + degradation["pressure"]
                + rng.normal(0, 3.8 + degradation["pressure_noise"])
            )
            energy_consumption = (
                12.0
                + 0.42 * temperature
                + 5.0 * operating_load
                + 1.8 * vibration
                + rng.normal(0, 2.1)
            )

            rows.append(
                {
                    "reading_id": f"R{reading_id:08d}",
                    "machine_id": machine_id,
                    "timestamp": timestamp.isoformat(),
                    "temperature": round(float(np.clip(temperature, 20, 135)), 2),
                    "vibration": round(float(np.clip(vibration, 0.1, 18)), 3),
                    "pressure": round(float(np.clip(pressure, 50, 280)), 2),
                    "runtime_hours": round(runtime_hours, 2),
                    "energy_consumption": round(float(np.clip(energy_consumption, 5, 95)), 2),
                    "operating_load": round(operating_load, 3),
                }
            )
            reading_id += 1

    return pd.DataFrame(rows)


def _failure_lookup(failures: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
    if failures.empty:
        return {}
    grouped: dict[str, list[dict[str, object]]] = {}
    for failure in failures.to_dict("records"):
        grouped.setdefault(str(failure["machine_id"]), []).append(failure)
    return grouped


def _pre_failure_degradation(
    timestamp: pd.Timestamp,
    machine_failures: list[dict[str, object]],
) -> dict[str, float]:
    signal = {"temperature": 0.0, "vibration": 0.0, "pressure": 0.0, "pressure_noise": 0.0}

    for failure in machine_failures:
        failure_date = pd.Timestamp(failure["failure_date"])
        hours_to_failure = (failure_date - timestamp).total_seconds() / 3600
        if not 0 <= hours_to_failure <= 24 * 10:
            continue

        intensity = 1 - (hours_to_failure / (24 * 10))
        failure_type = str(failure["failure_type"])
        severity_boost = {
            "minor": 0.7,
            "moderate": 1.0,
            "major": 1.35,
            "critical": 1.7,
        }[str(failure["severity"])]

        if failure_type == "overheating":
            signal["temperature"] += 18 * intensity * severity_boost
            signal["energy"] = 4 * intensity
        elif failure_type == "bearing_wear":
            signal["vibration"] += 4.0 * intensity * severity_boost
            signal["temperature"] += 5 * intensity
        elif failure_type == "pressure_system_failure":
            signal["pressure"] += 20 * np.sin(intensity * np.pi * 4)
            signal["pressure_noise"] += 8 * intensity * severity_boost
        elif failure_type == "electrical_fault":
            signal["temperature"] += 8 * intensity * severity_boost
            signal["pressure_noise"] += 3 * intensity
        elif failure_type == "vibration_related_failure":
            signal["vibration"] += 5.5 * intensity * severity_boost
            signal["pressure_noise"] += 4 * intensity

    return signal


def _load_factor(machine_type: str) -> float:
    return {
        "pump": 0.67,
        "compressor": 0.74,
        "conveyor": 0.58,
        "generator": 0.80,
        "hydraulic_press": 0.70,
    }.get(machine_type, 0.65)
