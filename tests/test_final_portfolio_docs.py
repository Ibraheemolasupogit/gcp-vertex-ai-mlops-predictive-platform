import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"


def test_final_portfolio_docs_exist() -> None:
    expected_docs = [
        "explainability.md",
        "monitoring_logging.md",
        "model_versioning_strategy.md",
        "screenshot_evidence_guide.md",
        "final_portfolio_architecture.md",
        "repository_health_check.md",
    ]

    for doc_name in expected_docs:
        assert (ROOT / "docs" / doc_name).is_file()
    assert (EVIDENCE_DIR / "README.md").is_file()
    assert (ROOT / "scripts" / "generate_monitoring_summary.py").is_file()


def test_final_docs_mention_required_topics() -> None:
    explainability = (ROOT / "docs" / "explainability.md").read_text(
        encoding="utf-8"
    )
    monitoring = (ROOT / "docs" / "monitoring_logging.md").read_text(
        encoding="utf-8"
    )
    versioning = (ROOT / "docs" / "model_versioning_strategy.md").read_text(
        encoding="utf-8"
    )
    screenshots = (ROOT / "docs" / "screenshot_evidence_guide.md").read_text(
        encoding="utf-8"
    )

    assert "explainability" in explainability.lower()
    assert "feature_importance.csv" in explainability
    assert "monitoring" in monitoring.lower()
    assert "logging" in monitoring.lower()
    assert "model versioning" in versioning.lower()
    assert "redact" in screenshots.lower()
    assert "Do not add fake screenshots" in screenshots


def test_evidence_readme_indexes_expected_folders() -> None:
    readme = (EVIDENCE_DIR / "README.md").read_text(encoding="utf-8")
    expected_folders = [
        "cloud_build_trigger",
        "cloud_composer_airflow",
        "cloud_run_traffic_splitting",
        "cloud_run_vertex_proxy",
        "vertex_ai_endpoint_prediction",
        "vertex_ai_model_registry",
        "vertex_ai_pipelines",
    ]

    for folder in expected_folders:
        assert folder in readme
        assert (EVIDENCE_DIR / folder).is_dir()
    assert "Do not add fake screenshots" in readme


def test_no_fake_screenshot_files_are_added() -> None:
    screenshot_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    screenshots = [
        path
        for path in EVIDENCE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in screenshot_extensions
    ]

    assert screenshots == []


def test_monitoring_summary_script_generates_required_keys() -> None:
    subprocess.run(
        ["python3", "scripts/generate_monitoring_summary.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary_path = ROOT / "outputs" / "monitoring_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    expected_keys = {
        "generated_at",
        "data_quality_status",
        "model_metrics_summary",
        "approval_status",
        "feature_table_metadata",
        "recommended_monitoring_signals",
        "local_only_notice",
    }
    assert expected_keys.issubset(summary)
    assert "request_count" in summary["recommended_monitoring_signals"]
    assert "GCP monitoring resources are queried" in summary["local_only_notice"]


def test_final_docs_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "docs" / "explainability.md",
        ROOT / "docs" / "monitoring_logging.md",
        ROOT / "docs" / "model_versioning_strategy.md",
        ROOT / "docs" / "screenshot_evidence_guide.md",
        ROOT / "docs" / "final_portfolio_architecture.md",
        ROOT / "docs" / "repository_health_check.md",
        EVIDENCE_DIR / "README.md",
        ROOT / "scripts" / "generate_monitoring_summary.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined
