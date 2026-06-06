"""Pydantic schemas for the local FastAPI prediction service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

LOCAL_ONLY_NOTICE = (
    "Local development service only. No GCP resources, credentials, or deployment are used."
)


class PredictionRequest(BaseModel):
    """Flexible prediction request validated against model metadata at runtime."""

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def reject_empty_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not data:
            raise ValueError("Prediction request must be a non-empty JSON object.")
        return data


class PredictionResponse(BaseModel):
    """Single prediction response."""

    prediction_class: int
    prediction_probability: float
    risk_band: str
    model_name: str
    model_version: str
    request_id: str
    timestamp: str
    local_only_notice: str = LOCAL_ONLY_NOTICE


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""

    records: list[dict[str, Any]] = Field(..., min_length=1)


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""

    predictions: list[dict[str, Any]]
    record_count: int
    model_name: str
    model_version: str
    request_id: str
    timestamp: str
    local_only_notice: str = LOCAL_ONLY_NOTICE


class HealthResponse(BaseModel):
    """Health response for local model serving."""

    status: str
    prediction_mode: str
    model_loaded: bool
    model_name: str | None
    model_version: str | None
    model_artifact_path: str | None
    metadata_loaded: bool
    timestamp: str
