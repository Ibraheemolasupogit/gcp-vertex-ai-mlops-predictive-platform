"""Synthetic maintenance and failure event generation."""

from __future__ import annotations

import numpy as np
import pandas as pd

FAILURE_TYPES = [
    "overheating",
    "bearing_wear",
    "pressure_system_failure",
    "electrical_fault",
    "vibration_related_failure",
]

ROOT_CAUSES = {
    "overheating": ["cooling inefficiency", "blocked ventilation", "thermal overload"],
    "bearing_wear": ["lubrication breakdown", "bearing fatigue", "shaft misalignment"],
    "pressure_system_failure": ["seal degradation", "valve instability", "pressure leak"],
    "electrical_fault": ["control board fault", "wiring degradation", "power fluctuation"],
    "vibration_related_failure": ["rotor imbalance", "mounting looseness", "mechanical resonance"],
}

MAINTENANCE_PARTS = {
    "preventive": ["filters", "lubricant", "belts"],
    "corrective": ["bearings", "seals", "couplings"],
    "inspection": ["none"],
    "emergency": ["motor assembly", "pressure valve", "control board"],
}

SEVERITY_FACTORS = {
    "minor": 0.7,
    "moderate": 1.0,
    "major": 1.6,
    "critical": 2.4,
}


def generate_failure_events(
    machines: pd.DataFrame,
    start_date: str,
    end_date: str,
    failure_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate realistic synthetic failures linked to known machines."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    date_span_days = max((end - start).days, 1)
    rows: list[dict[str, object]] = []
    failure_id = 1

    for machine in machines.to_dict("records"):
        age_years = (start - pd.Timestamp(machine["installation_date"])).days / 365.25
        lifetime = float(machine["expected_lifetime_years"])
        age_multiplier = min(1.8, 0.7 + age_years / lifetime)
        criticality_multiplier = {
            "low": 0.75,
            "medium": 1.0,
            "high": 1.2,
            "critical": 1.35,
        }[str(machine["criticality"])]
        machine_failure_probability = min(
            0.85,
            failure_rate * age_multiplier * criticality_multiplier,
        )
        failure_count = int(rng.binomial(2, machine_failure_probability / 2))

        for _ in range(failure_count):
            offset_days = int(rng.integers(10, max(11, date_span_days - 2)))
            failure_date = start + pd.Timedelta(days=offset_days)
            failure_type = _choose_failure_type(str(machine["machine_type"]), rng)
            severity = str(rng.choice(list(SEVERITY_FACTORS), p=[0.26, 0.42, 0.24, 0.08]))
            severity_factor = SEVERITY_FACTORS[severity]

            rows.append(
                {
                    "failure_id": f"F{failure_id:05d}",
                    "machine_id": machine["machine_id"],
                    "failure_date": failure_date.date().isoformat(),
                    "failure_type": failure_type,
                    "severity": severity,
                    "root_cause": str(rng.choice(ROOT_CAUSES[failure_type])),
                    "downtime_hours": round(float(rng.uniform(4, 18) * severity_factor), 2),
                    "repair_cost": round(float(rng.uniform(1200, 8500) * severity_factor), 2),
                }
            )
            failure_id += 1

    return pd.DataFrame(rows).sort_values(["machine_id", "failure_date"]).reset_index(drop=True)


def generate_maintenance_events(
    machines: pd.DataFrame,
    failures: pd.DataFrame,
    start_date: str,
    end_date: str,
    maintenance_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate synthetic maintenance events, including post-failure work."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    date_span_days = max((end - start).days, 1)
    rows: list[dict[str, object]] = []
    maintenance_id = 1

    for machine in machines.to_dict("records"):
        planned_count = max(1, int(rng.poisson(maintenance_rate)))
        for _ in range(planned_count):
            maintenance_type = str(rng.choice(["preventive", "inspection"], p=[0.68, 0.32]))
            maintenance_date = start + pd.Timedelta(days=int(rng.integers(1, date_span_days)))
            rows.append(
                _maintenance_row(
                    maintenance_id,
                    str(machine["machine_id"]),
                    maintenance_date,
                    maintenance_type,
                    rng,
                )
            )
            maintenance_id += 1

    for failure in failures.to_dict("records"):
        maintenance_type = (
            "emergency" if failure["severity"] in {"major", "critical"} else "corrective"
        )
        maintenance_date = pd.Timestamp(failure["failure_date"]) + pd.Timedelta(
            days=int(rng.integers(0, 3))
        )
        maintenance_date = min(maintenance_date, end)
        rows.append(
            _maintenance_row(
                maintenance_id,
                str(failure["machine_id"]),
                maintenance_date,
                maintenance_type,
                rng,
                failure_severity=str(failure["severity"]),
            )
        )
        maintenance_id += 1

    return pd.DataFrame(rows).sort_values(["machine_id", "maintenance_date"]).reset_index(drop=True)


def _choose_failure_type(machine_type: str, rng: np.random.Generator) -> str:
    if machine_type in {"pump", "hydraulic_press"}:
        probabilities = [0.18, 0.18, 0.36, 0.10, 0.18]
    elif machine_type == "compressor":
        probabilities = [0.30, 0.22, 0.20, 0.10, 0.18]
    elif machine_type == "generator":
        probabilities = [0.25, 0.18, 0.10, 0.30, 0.17]
    else:
        probabilities = [0.12, 0.34, 0.08, 0.14, 0.32]
    return str(rng.choice(FAILURE_TYPES, p=probabilities))


def _maintenance_row(
    maintenance_id: int,
    machine_id: str,
    maintenance_date: pd.Timestamp,
    maintenance_type: str,
    rng: np.random.Generator,
    failure_severity: str | None = None,
) -> dict[str, object]:
    severity_factor = SEVERITY_FACTORS.get(failure_severity or "moderate", 1.0)
    base_cost = {
        "inspection": 350,
        "preventive": 900,
        "corrective": 2600,
        "emergency": 6200,
    }[maintenance_type]
    base_downtime = {
        "inspection": 1.0,
        "preventive": 2.5,
        "corrective": 7.0,
        "emergency": 16.0,
    }[maintenance_type]
    risk_reduction = {
        "inspection": (0.05, 0.18),
        "preventive": (0.20, 0.45),
        "corrective": (0.35, 0.65),
        "emergency": (0.45, 0.78),
    }[maintenance_type]

    return {
        "maintenance_id": f"PM{maintenance_id:05d}",
        "machine_id": machine_id,
        "maintenance_date": maintenance_date.date().isoformat(),
        "maintenance_type": maintenance_type,
        "technician_team": str(rng.choice(["team_alpha", "team_beta", "team_delta", "team_omega"])),
        "downtime_hours": round(float(rng.uniform(0.7, 1.3) * base_downtime * severity_factor), 2),
        "parts_replaced": ";".join(
            rng.choice(MAINTENANCE_PARTS[maintenance_type], size=1).tolist()
        ),
        "maintenance_cost": round(float(rng.uniform(0.8, 1.35) * base_cost * severity_factor), 2),
        "risk_reduction_score": round(float(rng.uniform(*risk_reduction)), 3),
    }
