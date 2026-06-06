import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cloud_run_traffic_docs_and_templates_exist() -> None:
    assert (ROOT / "docs" / "cloud_run_revisions_traffic_splitting.md").is_file()
    assert (ROOT / "deployment" / "traffic_split.env.example").is_file()
    assert (ROOT / "deployment" / "update_cloud_run_traffic_split.sh").is_file()
    assert (ROOT / "deployment" / "describe_cloud_run_revisions.sh").is_file()
    assert (ROOT / "evidence" / "cloud_run_traffic_splitting" / "README.md").is_file()


def test_traffic_split_helper_defaults_to_dry_run() -> None:
    helper = (ROOT / "deployment" / "update_cloud_run_traffic_split.sh").read_text(
        encoding="utf-8"
    )

    assert "CONFIRM_UPDATE_TRAFFIC:-false" in helper
    assert "Dry run only" in helper
    assert "gcloud run services update-traffic" in helper
    assert "ROLLBACK_TO_STABLE" in helper


def test_revision_describe_helper_defaults_to_dry_run() -> None:
    helper = (ROOT / "deployment" / "describe_cloud_run_revisions.sh").read_text(
        encoding="utf-8"
    )

    assert "CONFIRM_DESCRIBE_REVISIONS:-false" in helper
    assert "Dry run only" in helper
    assert "gcloud run revisions list" in helper
    assert "gcloud run services describe" in helper


def test_docs_mention_revisions_traffic_splitting_rollback_and_evidence() -> None:
    docs = (ROOT / "docs" / "cloud_run_revisions_traffic_splitting.md").read_text(
        encoding="utf-8"
    )

    assert "Cloud Run revisions" in docs
    assert "Traffic splitting" in docs or "traffic splitting" in docs
    assert "Rollback" in docs
    assert "Evidence Screenshots" in docs
    assert "Vertex AI deployment is deferred" in docs


def test_traffic_split_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "cloud_run_revisions_traffic_splitting.md",
        ROOT / "deployment" / "traffic_split.env.example",
        ROOT / "deployment" / "update_cloud_run_traffic_split.sh",
        ROOT / "deployment" / "describe_cloud_run_revisions.sh",
        ROOT / "evidence" / "cloud_run_traffic_splitting" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r8_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "Cloud Run revisions visible" in checklist
    assert "Stable revision identified" in checklist
    assert "Candidate revision identified" in checklist
    assert "Rollback evidence captured" in checklist
