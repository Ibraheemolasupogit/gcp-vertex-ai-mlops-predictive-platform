"""Synthetic machine inventory generation for predictive maintenance demos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MachineProfile:
    """Baseline operating profile for a machine type."""

    temperature: float
    vibration: float
    pressure: float
    lifetime_years: int


MACHINE_PROFILES = {
    "pump": MachineProfile(temperature=62.0, vibration=3.2, pressure=145.0, lifetime_years=12),
    "compressor": MachineProfile(
        temperature=78.0,
        vibration=4.4,
        pressure=205.0,
        lifetime_years=10,
    ),
    "conveyor": MachineProfile(temperature=48.0, vibration=2.5, pressure=95.0, lifetime_years=15),
    "generator": MachineProfile(temperature=86.0, vibration=5.0, pressure=160.0, lifetime_years=14),
    "hydraulic_press": MachineProfile(
        temperature=70.0,
        vibration=3.8,
        pressure=230.0,
        lifetime_years=11,
    ),
}

MANUFACTURERS = ["Apex Industrial", "Northline Systems", "OmniWorks", "KineticForge"]
SITES = ["site_north", "site_south", "site_east", "site_west", "site_central"]
CRITICALITY = ["low", "medium", "high", "critical"]


def generate_machines(
    number_of_machines: int,
    start_date: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate a deterministic synthetic machine inventory."""
    start = pd.Timestamp(start_date)
    rows: list[dict[str, object]] = []
    machine_types = list(MACHINE_PROFILES)

    for index in range(1, number_of_machines + 1):
        machine_type = str(rng.choice(machine_types, p=[0.24, 0.20, 0.22, 0.18, 0.16]))
        profile = MACHINE_PROFILES[machine_type]
        age_days = int(rng.integers(180, profile.lifetime_years * 365))
        installation_date = start - pd.Timedelta(days=age_days)
        baseline_noise = rng.normal(1.0, 0.06, size=3)

        rows.append(
            {
                "machine_id": f"M{index:04d}",
                "machine_type": machine_type,
                "installation_date": installation_date.date().isoformat(),
                "site_id": str(rng.choice(SITES)),
                "manufacturer": str(rng.choice(MANUFACTURERS)),
                "expected_lifetime_years": profile.lifetime_years,
                "criticality": str(rng.choice(CRITICALITY, p=[0.20, 0.38, 0.25, 0.17])),
                "baseline_temperature": round(profile.temperature * baseline_noise[0], 2),
                "baseline_vibration": round(profile.vibration * baseline_noise[1], 2),
                "baseline_pressure": round(profile.pressure * baseline_noise[2], 2),
            }
        )

    return pd.DataFrame(rows)
