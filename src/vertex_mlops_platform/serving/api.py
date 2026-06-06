"""Local FastAPI application for predictive maintenance model serving."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException

from vertex_mlops_platform.prediction.model_loader import load_model_bundle
from vertex_mlops_platform.prediction.predictor import predict_batch, predict_single
from vertex_mlops_platform.prediction.schemas import PredictionInputError
from vertex_mlops_platform.serving.schemas import (
    LOCAL_ONLY_NOTICE,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)

SERVICE_NAME = "predictive-maintenance-local-api"
SERVICE_VERSION = "0.1.0"

app = FastAPI(
    title="Predictive Maintenance Local API",
    version=SERVICE_VERSION,
    description="Local-only model serving API for synthetic predictive maintenance data.",
)


@app.get("/")
def root() -> dict[str, Any]:
    """Return basic local service metadata."""
    return {
        "service_name": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "running",
        "description": "Local FastAPI wrapper around the predictive maintenance model.",
        "available_endpoints": ["/", "/health", "/predict", "/predict-batch"],
        "local_only_notice": LOCAL_ONLY_NOTICE,
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Check whether the local model and metadata can be loaded."""
    try:
        _, metadata = load_model_bundle()
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            model_name=metadata.get("model_name"),
            model_version=metadata.get("model_version"),
            model_artifact_path=metadata.get("model_artifact_path"),
            metadata_loaded=True,
            timestamp=_timestamp(),
        )
    except FileNotFoundError as exc:
        return HealthResponse(
            status=f"unhealthy: {exc}",
            model_loaded=False,
            model_name=None,
            model_version=None,
            model_artifact_path=None,
            metadata_loaded=False,
            timestamp=_timestamp(),
        )


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """Run a single local prediction."""
    model, metadata = _load_bundle_or_503()
    try:
        prediction = predict_single(model, metadata, request.model_dump())
    except PredictionInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PredictionResponse(
        **prediction,
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
        request_id=str(uuid4()),
        timestamp=_timestamp(),
    )


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch_endpoint(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """Run local batch predictions."""
    model, metadata = _load_bundle_or_503()
    dataframe = pd.DataFrame(request.records)
    try:
        prediction_frame = predict_batch(model, metadata, dataframe)
    except PredictionInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return BatchPredictionResponse(
        predictions=prediction_frame.to_dict(orient="records"),
        record_count=len(request.records),
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
        request_id=str(uuid4()),
        timestamp=_timestamp(),
    )


def _load_bundle_or_503() -> tuple[Any, dict[str, Any]]:
    try:
        return load_model_bundle()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()
