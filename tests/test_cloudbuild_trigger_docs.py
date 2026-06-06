import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_trigger_documentation_exists() -> None:
    assert (ROOT / "docs" / "github_cloud_build_trigger.md").is_file()


def test_trigger_template_helper_and_evidence_folder_exist() -> None:
    assert (ROOT / "deployment" / "cloud_build_trigger.template.yaml").is_file()
    assert (ROOT / "deployment" / "create_cloud_build_trigger.sh").is_file()
    assert (ROOT / "evidence" / "cloud_build_trigger" / "README.md").is_file()


def test_trigger_helper_defaults_to_dry_run_and_requires_confirmation() -> None:
    helper = (ROOT / "deployment" / "create_cloud_build_trigger.sh").read_text(
        encoding="utf-8"
    )

    assert "CONFIRM_CREATE_TRIGGER:-false" in helper
    assert "Dry run only" in helper
    assert "gcloud builds triggers create github" in helper
    assert "set -euo pipefail" in helper


def test_trigger_docs_include_required_concepts() -> None:
    docs = (ROOT / "docs" / "github_cloud_build_trigger.md").read_text(encoding="utf-8")

    assert "GitHub repository connected to Google Cloud Build" in docs
    assert "Cloud Build trigger" in docs
    assert "^main$" in docs
    assert "Evidence Screenshots" in docs
    assert "traffic splitting" in docs


def test_trigger_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "github_cloud_build_trigger.md",
        ROOT / "deployment" / "cloud_build_trigger.template.yaml",
        ROOT / "deployment" / "create_cloud_build_trigger.sh",
        ROOT / "evidence" / "cloud_build_trigger" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_trigger_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "GitHub repository connected to Cloud Build" in checklist
    assert "Cloud Build triggered automatically" in checklist
    assert "Cloud Run revision updated from trigger" in checklist
