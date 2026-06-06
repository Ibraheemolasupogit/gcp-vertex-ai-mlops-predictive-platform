"""Lightweight prediction input validation schemas."""

from __future__ import annotations

from typing import Any

import pandas as pd


class PredictionInputError(ValueError):
    """Raised when prediction input does not match model metadata."""


def validate_prediction_record(
    record: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Validate and normalize a single prediction record."""
    if not isinstance(record, dict):
        raise PredictionInputError("Prediction input must be a JSON object.")

    target_column = metadata["target_column"]
    if target_column in record:
        raise PredictionInputError(
            f"Prediction input must not include target column: {target_column}"
        )

    required_columns = list(metadata["feature_columns"])
    missing_columns = [column for column in required_columns if column not in record]
    if missing_columns:
        raise PredictionInputError(
            "Prediction input is missing required feature columns: "
            + ", ".join(missing_columns)
        )

    return {column: record[column] for column in required_columns}


def validate_prediction_dataframe(
    dataframe: pd.DataFrame,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    """Validate and normalize a batch prediction DataFrame."""
    if not isinstance(dataframe, pd.DataFrame):
        raise PredictionInputError("Batch prediction input must be a pandas DataFrame.")
    target_column = metadata["target_column"]
    if target_column in dataframe.columns:
        raise PredictionInputError(
            f"Prediction input must not include target column: {target_column}"
        )

    required_columns = list(metadata["feature_columns"])
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise PredictionInputError(
            "Batch prediction input is missing required feature columns: "
            + ", ".join(missing_columns)
        )
    return dataframe[required_columns].copy()
