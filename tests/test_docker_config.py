from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_exists() -> None:
    assert (ROOT / "Dockerfile").is_file()


def test_dockerignore_exists() -> None:
    assert (ROOT / ".dockerignore").is_file()


def test_dockerfile_references_uvicorn_and_cloud_run_port() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "uvicorn vertex_mlops_platform.serving.api:app" in dockerfile
    assert "EXPOSE 8080" in dockerfile
    assert "${PORT:-8080}" in dockerfile
    assert "--host 0.0.0.0" in dockerfile


def test_required_docker_helper_scripts_exist() -> None:
    for script in [
        "scripts/docker_build_local.sh",
        "scripts/docker_run_local.sh",
        "scripts/docker_test_local.sh",
    ]:
        assert (ROOT / script).is_file()


def test_required_runtime_artifacts_are_not_excluded_by_dockerignore() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    ignored_entries = {line.strip() for line in dockerignore if line.strip()}

    assert "models/" not in ignored_entries
    assert "models/*" not in ignored_entries
    assert "models/predictive_maintenance_model.joblib" not in ignored_entries
    assert "models/model_metadata.json" not in ignored_entries


def test_docker_documentation_exists() -> None:
    assert (ROOT / "docs" / "docker_serving.md").is_file()
