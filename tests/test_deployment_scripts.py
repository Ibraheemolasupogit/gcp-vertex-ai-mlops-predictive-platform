import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT = ROOT / "deployment"


REQUIRED_ENV_VARS = {
    "PROJECT_ID",
    "REGION",
    "ARTIFACT_REPOSITORY",
    "IMAGE_NAME",
    "IMAGE_TAG",
    "SERVICE_NAME",
    "PORT",
    "ALLOW_UNAUTHENTICATED",
}


def test_env_example_exists_and_contains_required_variables() -> None:
    env_example = DEPLOYMENT / "env.example"
    content = env_example.read_text(encoding="utf-8")

    assert env_example.is_file()
    for variable in REQUIRED_ENV_VARS:
        assert f"{variable}=" in content


def test_deployment_scripts_exist() -> None:
    for script_name in [
        "create_artifact_registry_repo.sh",
        "build_tag_push_image.sh",
        "deploy_cloud_run.sh",
        "test_cloud_run_service.sh",
    ]:
        assert (DEPLOYMENT / script_name).is_file()


def test_deployment_scripts_reference_expected_gcloud_commands() -> None:
    create_repo = (DEPLOYMENT / "create_artifact_registry_repo.sh").read_text(encoding="utf-8")
    build_push = (DEPLOYMENT / "build_tag_push_image.sh").read_text(encoding="utf-8")
    deploy = (DEPLOYMENT / "deploy_cloud_run.sh").read_text(encoding="utf-8")

    assert "gcloud artifacts repositories create" in create_repo
    assert "gcloud auth configure-docker" in build_push
    assert "docker push" in build_push
    assert "gcloud run deploy" in deploy
    assert "gcloud run services describe" in deploy


def test_deployment_scripts_are_parameterized() -> None:
    combined = "\n".join(
        script.read_text(encoding="utf-8") for script in DEPLOYMENT.glob("*.sh")
    )

    for variable in ["PROJECT_ID", "REGION", "IMAGE_NAME", "SERVICE_NAME"]:
        assert f"${{{variable}" in combined or f"${variable}" in combined
    assert "set -euo pipefail" in combined


def test_deployment_scripts_do_not_contain_real_looking_project_ids() -> None:
    combined = "\n".join(
        script.read_text(encoding="utf-8") for script in DEPLOYMENT.glob("*.sh")
    )
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(combined)
    assert "serviceAccountKey" not in combined
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in combined


def test_manual_deployment_documentation_and_evidence_readme_exist() -> None:
    assert (ROOT / "docs" / "manual_cloud_run_deployment.md").is_file()
    assert (ROOT / "evidence" / "README.md").is_file()
