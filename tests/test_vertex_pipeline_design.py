import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_PATH = ROOT / "pipelines" / "vertex_pipeline.py"


def test_vertex_pipeline_design_files_exist() -> None:
    assert (ROOT / "docs" / "vertex_ai_pipelines_kubeflow_design.md").is_file()
    assert (ROOT / "deployment" / "vertex_pipeline.env.example").is_file()
    assert PIPELINE_PATH.is_file()
    assert (
        ROOT / "pipelines" / "config" / "vertex_pipeline_config.example.yaml"
    ).is_file()
    assert (ROOT / "pipelines" / "components.md").is_file()
    assert (ROOT / "deployment" / "validate_vertex_pipeline_structure.sh").is_file()
    assert (ROOT / "deployment" / "compile_vertex_pipeline_dry_run.sh").is_file()
    assert (ROOT / "evidence" / "vertex_ai_pipelines" / "README.md").is_file()


def test_pipeline_skeleton_contains_expected_component_names() -> None:
    pipeline_source = PIPELINE_PATH.read_text(encoding="utf-8")
    expected_components = [
        "validate_data_component",
        "build_features_component",
        "train_model_component",
        "evaluate_model_component",
        "run_approval_gates_component",
        "register_model_component",
        "generate_model_card_component",
    ]

    for component_name in expected_components:
        assert component_name in pipeline_source
    assert "predictive_maintenance_mlops_pipeline" in pipeline_source


def test_pipeline_skeleton_is_safe_without_kubeflow_dependency() -> None:
    pipeline_source = PIPELINE_PATH.read_text(encoding="utf-8")

    assert "except ImportError" in pipeline_source
    assert "dsl = None" in pipeline_source
    assert "gcloud" not in pipeline_source
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in pipeline_source


def test_vertex_pipeline_docs_mention_required_concepts_and_evidence() -> None:
    docs = (ROOT / "docs" / "vertex_ai_pipelines_kubeflow_design.md").read_text(
        encoding="utf-8"
    )

    assert "Vertex AI Pipelines" in docs
    assert "Kubeflow" in docs
    assert "Evidence Screenshots" in docs
    assert "artifact lineage" in docs.lower()
    assert "deferred to R14" in docs


def test_vertex_pipeline_helpers_are_local_and_safe() -> None:
    validate_helper = (
        ROOT / "deployment" / "validate_vertex_pipeline_structure.sh"
    ).read_text(encoding="utf-8")
    compile_helper = (
        ROOT / "deployment" / "compile_vertex_pipeline_dry_run.sh"
    ).read_text(encoding="utf-8")

    assert "set -euo pipefail" in validate_helper
    assert "python3 -m py_compile" in validate_helper
    assert "No pipeline jobs or GCP commands were run" in validate_helper
    assert "set -euo pipefail" in compile_helper
    assert "Kubeflow Pipelines SDK is not installed" in compile_helper
    assert "Dry run only" in compile_helper
    assert "No pipeline job was submitted" in compile_helper


def test_vertex_pipeline_files_do_not_contain_real_project_ids_or_secrets() -> None:
    paths = [
        ROOT / "docs" / "vertex_ai_pipelines_kubeflow_design.md",
        ROOT / "deployment" / "vertex_pipeline.env.example",
        PIPELINE_PATH,
        ROOT / "pipelines" / "config" / "vertex_pipeline_config.example.yaml",
        ROOT / "pipelines" / "components.md",
        ROOT / "deployment" / "validate_vertex_pipeline_structure.sh",
        ROOT / "deployment" / "compile_vertex_pipeline_dry_run.sh",
        ROOT / "evidence" / "vertex_ai_pipelines" / "README.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined
    assert "PRIVATE KEY" not in combined
    assert "BEGIN PRIVATE KEY" not in combined


def test_deployment_evidence_checklist_mentions_r13_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "R13 Vertex AI Pipeline job created" in checklist
    assert "Pipeline graph captured" in checklist
    assert "Validation component completed" in checklist
    assert "Model registration component completed" in checklist
    assert "Model Registry candidate linked to pipeline" in checklist
