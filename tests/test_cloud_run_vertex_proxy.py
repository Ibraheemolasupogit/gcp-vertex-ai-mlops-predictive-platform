import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from vertex_mlops_platform.serving.api import app
from vertex_mlops_platform.serving.proxy_config import (
    LOCAL_MODEL_MODE,
    VERTEX_ENDPOINT_MODE,
    load_proxy_config,
)
from vertex_mlops_platform.serving.vertex_client import (
    VertexEndpointClient,
    build_endpoint_resource_name,
    normalize_vertex_prediction_response,
    to_vertex_instances,
)

ROOT = Path(__file__).resolve().parents[1]


def _sample_request() -> dict[str, object]:
    request_path = ROOT / "data" / "sample" / "prediction_request.json"
    return json.loads(request_path.read_text(encoding="utf-8"))


def test_cloud_run_vertex_proxy_docs_templates_examples_and_evidence_exist() -> None:
    assert (ROOT / "docs" / "cloud_run_vertex_ai_proxy.md").is_file()
    assert (ROOT / "deployment" / "cloud_run_vertex_proxy.env.example").is_file()
    assert (ROOT / "deployment" / "test_cloud_run_vertex_proxy_dry_run.sh").is_file()
    assert (ROOT / "examples" / "vertex_proxy_request.json").is_file()
    assert (ROOT / "examples" / "vertex_proxy_response.json").is_file()
    assert (ROOT / "evidence" / "cloud_run_vertex_proxy" / "README.md").is_file()


def test_vertex_client_builds_endpoint_resource_name() -> None:
    resource_name = build_endpoint_resource_name(
        "demo-project",
        "europe-west2",
        "endpoint-123",
    )

    assert resource_name == (
        "projects/demo-project/locations/europe-west2/endpoints/endpoint-123"
    )


def test_request_transformation_produces_vertex_instances() -> None:
    record = _sample_request()

    payload = to_vertex_instances(record)

    assert "instances" in payload
    assert payload["instances"] == [record]
    assert "failure_within_label_window" not in payload["instances"][0]


def test_request_transformation_rejects_target_leakage_field() -> None:
    record = _sample_request()
    record["failure_within_label_window"] = 1

    with pytest.raises(ValueError, match="target/leakage"):
        to_vertex_instances(record)


def test_vertex_response_normalisation_works() -> None:
    normalised = normalize_vertex_prediction_response(
        {
            "predictions": [
                {
                    "prediction_class": 1,
                    "prediction_probability": 0.61,
                }
            ]
        }
    )

    assert normalised["prediction_class"] == 1
    assert normalised["prediction_probability"] == 0.61
    assert normalised["risk_band"] in {"low", "medium", "high", "critical"}


def test_vertex_client_stub_prediction_does_not_require_gcp_credentials() -> None:
    client = VertexEndpointClient(
        project_id="demo-project",
        region="europe-west2",
        endpoint_id="endpoint-123",
    )

    prediction = client.predict_stub(_sample_request())

    assert prediction["model_name"] == "vertex-ai-endpoint-dry-run"
    assert prediction["risk_band"] in {"low", "medium", "high", "critical"}


def test_proxy_config_defaults_to_local_model() -> None:
    config = load_proxy_config({})

    assert config.prediction_mode == LOCAL_MODEL_MODE
    assert not config.vertex_enabled


def test_proxy_config_validates_vertex_settings_when_enabled() -> None:
    with pytest.raises(ValueError, match="Missing Vertex AI proxy configuration"):
        load_proxy_config({"PREDICTION_MODE": "vertex_endpoint", "ENABLE_VERTEX_PROXY": "true"})

    config = load_proxy_config(
        {
            "PREDICTION_MODE": "vertex",
            "ENABLE_VERTEX_PROXY": "true",
            "VERTEX_PROJECT_ID": "demo-project",
            "VERTEX_ENDPOINT_REGION": "europe-west2",
            "VERTEX_ENDPOINT_ID": "endpoint-123",
        }
    )

    assert config.prediction_mode == VERTEX_ENDPOINT_MODE
    assert config.vertex_enabled


def test_health_includes_prediction_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PREDICTION_MODE", raising=False)
    monkeypatch.delenv("ENABLE_VERTEX_PROXY", raising=False)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["prediction_mode"] == LOCAL_MODEL_MODE


def test_existing_predict_still_works_in_local_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PREDICTION_MODE", "local_model")
    monkeypatch.setenv("ENABLE_VERTEX_PROXY", "false")
    client = TestClient(app)

    response = client.post("/predict", json=_sample_request())

    assert response.status_code == 200
    payload = response.json()
    assert {"prediction_class", "prediction_probability", "risk_band"}.issubset(payload)
    assert "local" in payload["local_only_notice"].lower()


def test_docs_and_proxy_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "cloud_run_vertex_ai_proxy.md",
        ROOT / "deployment" / "cloud_run_vertex_proxy.env.example",
        ROOT / "deployment" / "test_cloud_run_vertex_proxy_dry_run.sh",
        ROOT / "examples" / "vertex_proxy_request.json",
        ROOT / "examples" / "vertex_proxy_response.json",
        ROOT / "evidence" / "cloud_run_vertex_proxy" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r11_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "R11 Cloud Run service configured with Vertex endpoint variables" in checklist
    assert "Cloud Run service account has Vertex AI predict permission" in checklist
    assert "/health` shows vertex endpoint mode" in checklist
    assert "Normalised response returned by Cloud Run" in checklist
