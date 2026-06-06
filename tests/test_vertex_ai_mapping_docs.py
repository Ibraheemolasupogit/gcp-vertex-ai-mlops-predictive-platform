import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vertex_ai_mapping_docs_templates_and_evidence_exist() -> None:
    assert (
        ROOT / "docs" / "vertex_ai_custom_training_model_registry.md"
    ).is_file()
    assert (ROOT / "deployment" / "vertex_ai.env.example").is_file()
    assert (
        ROOT / "deployment" / "vertex_ai_custom_training_job.template.yaml"
    ).is_file()
    assert (
        ROOT / "deployment" / "vertex_ai_model_registry_metadata.template.json"
    ).is_file()
    assert (ROOT / "deployment" / "submit_vertex_ai_training_job.sh").is_file()
    assert (ROOT / "deployment" / "register_vertex_ai_model.sh").is_file()
    assert (ROOT / "evidence" / "vertex_ai_model_registry" / "README.md").is_file()


def test_vertex_ai_training_helper_defaults_to_dry_run() -> None:
    helper = (ROOT / "deployment" / "submit_vertex_ai_training_job.sh").read_text(
        encoding="utf-8"
    )

    assert "set -euo pipefail" in helper
    assert "CONFIRM_SUBMIT_VERTEX_TRAINING:-false" in helper
    assert "Dry run only" in helper
    assert "gcloud ai custom-jobs create" in helper


def test_vertex_ai_registry_helper_defaults_to_dry_run() -> None:
    helper = (ROOT / "deployment" / "register_vertex_ai_model.sh").read_text(
        encoding="utf-8"
    )

    assert "set -euo pipefail" in helper
    assert "CONFIRM_REGISTER_VERTEX_MODEL:-false" in helper
    assert "Dry run only" in helper
    assert "gcloud ai models upload" in helper
    assert "SERVING_CONTAINER_IMAGE_URI" in helper


def test_vertex_ai_docs_mention_required_concepts_and_evidence() -> None:
    docs = (
        ROOT / "docs" / "vertex_ai_custom_training_model_registry.md"
    ).read_text(encoding="utf-8")

    assert "Vertex AI custom training" in docs
    assert "Model Registry" in docs
    assert "Cloud Storage" in docs
    assert "Evidence Screenshots" in docs
    assert "Vertex AI endpoint deployment is deferred to R10" in docs


def test_vertex_ai_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "vertex_ai_custom_training_model_registry.md",
        ROOT / "deployment" / "vertex_ai.env.example",
        ROOT / "deployment" / "vertex_ai_custom_training_job.template.yaml",
        ROOT / "deployment" / "vertex_ai_model_registry_metadata.template.json",
        ROOT / "deployment" / "submit_vertex_ai_training_job.sh",
        ROOT / "deployment" / "register_vertex_ai_model.sh",
        ROOT / "evidence" / "vertex_ai_model_registry" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r9_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "R9 Vertex AI API enabled" in checklist
    assert "Staging bucket prepared" in checklist
    assert "Custom training job submitted" in checklist
    assert "Vertex AI Model Registry entry created" in checklist
    assert "Model approval and lifecycle mapping captured" in checklist
