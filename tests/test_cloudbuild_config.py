import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _cloudbuild() -> dict[str, object]:
    with (ROOT / "cloudbuild.yaml").open() as config_file:
        return yaml.safe_load(config_file)


def test_cloudbuild_yaml_exists() -> None:
    assert (ROOT / "cloudbuild.yaml").is_file()


def test_cloudbuild_contains_docker_build_push_and_cloud_run_deploy_steps() -> None:
    config = _cloudbuild()
    steps = config["steps"]
    step_ids = {step["id"] for step in steps}
    serialized = (ROOT / "cloudbuild.yaml").read_text(encoding="utf-8")

    assert {"build-docker-image", "push-docker-image", "deploy-cloud-run"}.issubset(step_ids)
    assert "docker" in steps[0]["name"]
    assert '"push"' in serialized
    assert "gcloud run deploy" in serialized


def test_cloudbuild_uses_required_substitutions() -> None:
    content = (ROOT / "cloudbuild.yaml").read_text(encoding="utf-8")

    for substitution in [
        "_PROJECT_ID",
        "_REGION",
        "_ARTIFACT_REPOSITORY",
        "_IMAGE_NAME",
        "_IMAGE_TAG",
        "_SERVICE_NAME",
        "_PORT",
        "_ALLOW_UNAUTHENTICATED",
    ]:
        assert f"${{{substitution}}}" in content or f'"{substitution}"' in content


def test_cloudbuild_does_not_contain_real_looking_project_ids() -> None:
    content = (ROOT / "cloudbuild.yaml").read_text(encoding="utf-8")
    real_project_pattern = re.compile(r"\b[a-z][a-z0-9-]{4,28}-[0-9]{3,}\b")

    assert not real_project_pattern.search(content)
    assert "serviceAccountKey" not in content
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in content


def test_cloudbuild_supporting_files_exist() -> None:
    assert (ROOT / "deployment" / "cloudbuild.substitutions.example.yaml").is_file()
    assert (ROOT / "deployment" / "submit_cloud_build.sh").is_file()
    assert (ROOT / "docs" / "cloud_build_ci_cd.md").is_file()


def test_submit_helper_is_parameterized_and_references_gcloud_builds_submit() -> None:
    script = (ROOT / "deployment" / "submit_cloud_build.sh").read_text(encoding="utf-8")

    assert "set -euo pipefail" in script
    assert "gcloud builds submit" in script
    assert "--substitutions=" in script
    assert "${PROJECT_ID}" in script
    assert "${REGION}" in script


def test_deployment_evidence_checklist_mentions_cloud_build_evidence() -> None:
    checklist = (ROOT / "docs" / "deployment_evidence_checklist.md").read_text(
        encoding="utf-8"
    )

    assert "cloudbuild.yaml" in checklist
    assert "Cloud Build manual run submitted" in checklist
    assert "Cloud Run deploy step success" in checklist
