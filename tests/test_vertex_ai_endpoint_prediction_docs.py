import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vertex_ai_endpoint_docs_templates_examples_and_evidence_exist() -> None:
    assert (ROOT / "docs" / "vertex_ai_endpoint_prediction.md").is_file()
    assert (ROOT / "deployment" / "vertex_ai_prediction.env.example").is_file()
    assert (
        ROOT / "deployment" / "vertex_ai_endpoint_deployment.template.yaml"
    ).is_file()
    assert (ROOT / "examples" / "vertex_online_prediction_request.json").is_file()
    assert (ROOT / "examples" / "vertex_batch_prediction_input.jsonl").is_file()
    assert (ROOT / "deployment" / "create_vertex_ai_endpoint.sh").is_file()
    assert (ROOT / "deployment" / "deploy_model_to_vertex_endpoint.sh").is_file()
    assert (ROOT / "deployment" / "run_vertex_online_prediction.sh").is_file()
    assert (ROOT / "deployment" / "run_vertex_batch_prediction.sh").is_file()
    assert (
        ROOT / "evidence" / "vertex_ai_endpoint_prediction" / "README.md"
    ).is_file()


def test_vertex_ai_endpoint_scripts_default_to_dry_run() -> None:
    expected_confirmations = {
        "create_vertex_ai_endpoint.sh": "CONFIRM_CREATE_VERTEX_ENDPOINT:-false",
        "deploy_model_to_vertex_endpoint.sh": "CONFIRM_DEPLOY_VERTEX_MODEL:-false",
        "run_vertex_online_prediction.sh": (
            "CONFIRM_RUN_VERTEX_ONLINE_PREDICTION:-false"
        ),
        "run_vertex_batch_prediction.sh": "CONFIRM_RUN_VERTEX_BATCH_PREDICTION:-false",
    }

    for script_name, confirmation in expected_confirmations.items():
        script = (ROOT / "deployment" / script_name).read_text(encoding="utf-8")
        assert "set -euo pipefail" in script
        assert confirmation in script
        assert "Dry run only" in script


def test_vertex_ai_endpoint_scripts_reference_expected_gcloud_commands() -> None:
    create_endpoint = (
        ROOT / "deployment" / "create_vertex_ai_endpoint.sh"
    ).read_text(encoding="utf-8")
    deploy_model = (
        ROOT / "deployment" / "deploy_model_to_vertex_endpoint.sh"
    ).read_text(encoding="utf-8")
    online_prediction = (
        ROOT / "deployment" / "run_vertex_online_prediction.sh"
    ).read_text(encoding="utf-8")
    batch_prediction = (
        ROOT / "deployment" / "run_vertex_batch_prediction.sh"
    ).read_text(encoding="utf-8")

    assert "gcloud ai endpoints create" in create_endpoint
    assert "gcloud ai endpoints deploy-model" in deploy_model
    assert "gcloud ai endpoints predict" in online_prediction
    assert "gcloud ai batch-prediction-jobs create" in batch_prediction


def test_vertex_ai_prediction_examples_exclude_target_fields() -> None:
    online_request = json.loads(
        (ROOT / "examples" / "vertex_online_prediction_request.json").read_text(
            encoding="utf-8"
        )
    )
    assert "instances" in online_request
    assert len(online_request["instances"]) >= 1
    for instance in online_request["instances"]:
        assert "failure_within_label_window" not in instance
        assert "current_temperature" in instance
        assert "current_vibration" in instance

    batch_lines = (
        ROOT / "examples" / "vertex_batch_prediction_input.jsonl"
    ).read_text(encoding="utf-8").strip().splitlines()
    assert len(batch_lines) >= 2
    for line in batch_lines:
        record = json.loads(line)
        assert "failure_within_label_window" not in record
        assert "current_temperature" in record
        assert "current_vibration" in record


def test_vertex_ai_endpoint_docs_mention_required_concepts_and_evidence() -> None:
    docs = (ROOT / "docs" / "vertex_ai_endpoint_prediction.md").read_text(
        encoding="utf-8"
    )

    assert "Vertex AI endpoint" in docs
    assert "online prediction" in docs
    assert "batch prediction" in docs
    assert "Evidence Screenshots" in docs
    assert "Cloud Run API wrapper in front of a Vertex AI endpoint is deferred to R11" in docs


def test_vertex_ai_endpoint_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "vertex_ai_endpoint_prediction.md",
        ROOT / "deployment" / "vertex_ai_prediction.env.example",
        ROOT / "deployment" / "vertex_ai_endpoint_deployment.template.yaml",
        ROOT / "deployment" / "create_vertex_ai_endpoint.sh",
        ROOT / "deployment" / "deploy_model_to_vertex_endpoint.sh",
        ROOT / "deployment" / "run_vertex_online_prediction.sh",
        ROOT / "deployment" / "run_vertex_batch_prediction.sh",
        ROOT / "evidence" / "vertex_ai_endpoint_prediction" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r10_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "R10 Vertex AI endpoint created" in checklist
    assert "Model deployed to endpoint" in checklist
    assert "Endpoint ID captured" in checklist
    assert "Online prediction response captured" in checklist
    assert "Batch output Cloud Storage location captured" in checklist
