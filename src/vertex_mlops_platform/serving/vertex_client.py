"""Vertex AI endpoint proxy helpers.

This module intentionally avoids importing Google Cloud libraries. It provides
the request/response transformation layer and a dry-run client interface that
can be replaced by a real Vertex AI prediction client in a later milestone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vertex_mlops_platform.prediction.predictor import risk_band


def build_endpoint_resource_name(project_id: str, region: str, endpoint_id: str) -> str:
    """Build the canonical Vertex AI endpoint resource name."""
    if not project_id or not region or not endpoint_id:
        raise ValueError("project_id, region, and endpoint_id are required.")
    return f"projects/{project_id}/locations/{region}/endpoints/{endpoint_id}"


def to_vertex_instances(record: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Convert a local prediction request into Vertex AI instances format."""
    if "failure_within_label_window" in record:
        raise ValueError("Prediction requests must not include target/leakage fields.")
    return {"instances": [record]}


def normalize_vertex_prediction_response(
    response: dict[str, Any],
    *,
    model_name: str = "vertex-ai-endpoint",
    model_version: str = "vertex-proxy",
) -> dict[str, Any]:
    """Normalize a Vertex AI-style prediction response to the local API shape."""
    predictions = response.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        raise ValueError("Vertex AI response must include at least one prediction.")

    first_prediction = predictions[0]
    if isinstance(first_prediction, dict):
        prediction_class = int(first_prediction.get("prediction_class", 0))
        probability = float(
            first_prediction.get(
                "prediction_probability",
                first_prediction.get("probability", 0.0),
            )
        )
        band = str(first_prediction.get("risk_band", risk_band(probability)))
    else:
        probability = float(first_prediction)
        prediction_class = int(probability >= 0.5)
        band = risk_band(probability)

    return {
        "prediction_class": prediction_class,
        "prediction_probability": probability,
        "risk_band": band,
        "model_name": model_name,
        "model_version": model_version,
    }


@dataclass(frozen=True)
class VertexEndpointClient:
    """Dry-run Vertex AI endpoint client for proxy-mode tests and design."""

    project_id: str
    region: str
    endpoint_id: str
    timeout_seconds: int = 30

    @property
    def endpoint_resource_name(self) -> str:
        """Return the canonical endpoint resource name."""
        return build_endpoint_resource_name(
            self.project_id,
            self.region,
            self.endpoint_id,
        )

    def predict_stub(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a deterministic dry-run prediction without calling Vertex AI."""
        payload = to_vertex_instances(record)
        temperature = float(record.get("current_temperature", 0.0))
        vibration = float(record.get("current_vibration", 0.0))
        probability = min(max((temperature / 160.0 + vibration / 12.0) / 2.0, 0.0), 1.0)
        vertex_response = {
            "endpoint": self.endpoint_resource_name,
            "deployed_model_id": "dry-run",
            "predictions": [
                {
                    "prediction_class": int(probability >= 0.5),
                    "prediction_probability": probability,
                    "risk_band": risk_band(probability),
                }
            ],
            "request": payload,
        }
        return normalize_vertex_prediction_response(
            vertex_response,
            model_name="vertex-ai-endpoint-dry-run",
            model_version="proxy-stub",
        )
