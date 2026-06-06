from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from vertex_mlops_platform.serving.api import app

ROOT = Path(__file__).resolve().parents[1]
TARGET_COLUMN = "failure_within_label_window"


def _sample_request() -> dict[str, object]:
    request_path = ROOT / "data" / "sample" / "prediction_request.json"
    return json.loads(request_path.read_text(encoding="utf-8"))


def test_fastapi_app_imports_successfully() -> None:
    assert app.title == "Predictive Maintenance Local API"


def test_root_returns_service_metadata() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service_name"] == "predictive-maintenance-local-api"
    assert "/predict" in payload["available_endpoints"]
    assert "local" in payload["local_only_notice"].lower()


def test_health_returns_model_status() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"healthy"} or payload["status"].startswith("unhealthy")
    assert "model_loaded" in payload
    assert "metadata_loaded" in payload
    assert "timestamp" in payload


def test_predict_returns_prediction_fields() -> None:
    client = TestClient(app)

    response = client.post("/predict", json=_sample_request())

    assert response.status_code == 200
    payload = response.json()
    assert {"prediction_class", "prediction_probability", "risk_band"}.issubset(payload)
    assert payload["risk_band"] in {"low", "medium", "high", "critical"}
    assert payload["model_version"]
    assert "local" in payload["local_only_notice"].lower()


def test_predict_rejects_target_leakage_field() -> None:
    client = TestClient(app)
    request = _sample_request()
    request[TARGET_COLUMN] = 1

    response = client.post("/predict", json=request)

    assert response.status_code == 422
    assert TARGET_COLUMN in response.text


def test_predict_batch_returns_predictions_for_multiple_records() -> None:
    client = TestClient(app)
    request = _sample_request()

    response = client.post("/predict-batch", json={"records": [request, request]})

    assert response.status_code == 200
    payload = response.json()
    assert payload["record_count"] == 2
    assert len(payload["predictions"]) == 2
    assert {"prediction_class", "prediction_probability", "risk_band"}.issubset(
        payload["predictions"][0]
    )


def test_predict_batch_rejects_invalid_records() -> None:
    client = TestClient(app)
    request = _sample_request()
    request.pop("current_temperature")

    response = client.post("/predict-batch", json={"records": [request]})

    assert response.status_code == 422
    assert "current_temperature" in response.text


def test_api_does_not_require_docker_or_gcp() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    notice = response.json()["local_only_notice"].lower()
    assert "gcp" in notice
    assert "credentials" in notice
