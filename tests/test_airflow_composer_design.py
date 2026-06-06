import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = ROOT / "airflow" / "dags" / "predictive_maintenance_continuous_training_dag.py"


def test_airflow_composer_design_files_exist() -> None:
    assert (
        ROOT / "docs" / "cloud_composer_airflow_continuous_training.md"
    ).is_file()
    assert (ROOT / "deployment" / "composer.env.example").is_file()
    assert DAG_PATH.is_file()
    assert (
        ROOT
        / "airflow"
        / "dags"
        / "config"
        / "continuous_training_config.example.yaml"
    ).is_file()
    assert (ROOT / "deployment" / "validate_airflow_dag_structure.sh").is_file()
    assert (ROOT / "evidence" / "cloud_composer_airflow" / "README.md").is_file()


def test_dag_file_contains_expected_task_names() -> None:
    dag_source = DAG_PATH.read_text(encoding="utf-8")
    expected_tasks = [
        "check_new_data",
        "validate_data",
        "build_features",
        "submit_vertex_training_job",
        "collect_training_metrics",
        "run_approval_gates",
        "register_candidate_model",
        "notify_reviewer",
    ]

    for task_name in expected_tasks:
        assert task_name in dag_source


def test_dag_file_is_safe_without_airflow_dependency() -> None:
    dag_source = DAG_PATH.read_text(encoding="utf-8")

    assert "except ImportError" in dag_source
    assert "dag = None" in dag_source
    assert "gcloud" not in dag_source
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in dag_source


def test_composer_docs_mention_required_concepts_and_evidence() -> None:
    docs = (
        ROOT / "docs" / "cloud_composer_airflow_continuous_training.md"
    ).read_text(encoding="utf-8")

    assert "Cloud Composer" in docs
    assert "Airflow DAG" in docs
    assert "continuous training" in docs
    assert "Evidence Screenshots" in docs
    assert "Vertex AI Pipelines and Kubeflow design are deferred to R13" in docs


def test_validate_dag_helper_is_local_and_safe() -> None:
    helper = (ROOT / "deployment" / "validate_airflow_dag_structure.sh").read_text(
        encoding="utf-8"
    )

    assert "set -euo pipefail" in helper
    assert "python3 -m py_compile" in helper
    assert "No Airflow or GCP commands were run" in helper
    assert "gcloud" not in helper


def test_composer_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "cloud_composer_airflow_continuous_training.md",
        ROOT / "deployment" / "composer.env.example",
        DAG_PATH,
        ROOT
        / "airflow"
        / "dags"
        / "config"
        / "continuous_training_config.example.yaml",
        ROOT / "deployment" / "validate_airflow_dag_structure.sh",
        ROOT / "evidence" / "cloud_composer_airflow" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r12_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "R12 Cloud Composer environment created" in checklist
    assert "DAG graph view captured" in checklist
    assert "Vertex AI training task triggered" in checklist
    assert "Approval gate task completed" in checklist
    assert "DAG logs captured" in checklist
