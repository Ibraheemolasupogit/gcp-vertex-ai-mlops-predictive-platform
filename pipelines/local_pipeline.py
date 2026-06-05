"""Placeholder local pipeline design.

Future milestones will use this module to orchestrate local data generation,
ingestion, feature engineering, training, evaluation, registration, batch
prediction, monitoring, and reporting.
"""

from __future__ import annotations


def describe_pipeline() -> list[str]:
    """Return the planned local pipeline stages."""
    return [
        "generate synthetic equipment telemetry",
        "ingest local datasets",
        "build feature tables",
        "train and evaluate candidate models",
        "apply deployment gates",
        "register approved models",
        "run batch predictions",
        "monitor drift and performance",
        "write reports",
    ]


if __name__ == "__main__":
    for index, stage in enumerate(describe_pipeline(), start=1):
        print(f"{index}. {stage}")
