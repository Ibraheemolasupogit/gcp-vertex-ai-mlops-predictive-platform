"""Reusable local prediction utilities independent of API frameworks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from vertex_mlops_platform.prediction.schemas import (
    validate_prediction_dataframe,
    validate_prediction_record,
)


def risk_band(probability: float) -> str:
    """Map failure probability to a human-readable risk band."""
    if probability >= 0.75:
        return "critical"
    if probability >= 0.50:
        return "high"
    if probability >= 0.25:
        return "medium"
    return "low"


def predict_single(
    model: Any,
    metadata: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    """Run prediction for one validated record."""
    normalized_record = validate_prediction_record(record, metadata)
    dataframe = pd.DataFrame([normalized_record])
    batch_result = predict_batch(model, metadata, dataframe)
    return {
        "prediction_class": int(batch_result.iloc[0]["prediction_class"]),
        "prediction_probability": float(batch_result.iloc[0]["prediction_probability"]),
        "risk_band": str(batch_result.iloc[0]["risk_band"]),
    }


def predict_batch(
    model: Any,
    metadata: dict[str, Any],
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Run batch predictions for a validated DataFrame."""
    features = validate_prediction_dataframe(dataframe, metadata)
    predictions = model.predict(features).astype(int)
    probabilities = _positive_probabilities(model, features)

    result = pd.DataFrame(
        {
            "prediction_class": predictions.astype(int),
            "prediction_probability": probabilities,
        }
    )
    result["risk_band"] = result["prediction_probability"].map(risk_band)
    return result


def _positive_probabilities(model: Any, features: pd.DataFrame) -> list[float]:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)
        if probabilities.shape[1] >= 2:
            return [float(value) for value in probabilities[:, 1]]
    predictions = model.predict(features)
    return [float(value) for value in predictions]
