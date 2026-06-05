from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_key_project_files_exist() -> None:
    expected_files = [
        "README.md",
        "LICENSE",
        ".gitignore",
        "requirements.txt",
        "pyproject.toml",
        "Makefile",
        ".github/workflows/python-ci.yml",
        "dashboard/streamlit_app.py",
        "pipelines/local_pipeline.py",
        "sql/bigquery_feature_table.sql",
    ]

    for relative_path in expected_files:
        assert (ROOT / relative_path).is_file(), f"Missing {relative_path}"


def test_key_project_directories_exist() -> None:
    expected_dirs = [
        "configs",
        "src/vertex_mlops_platform",
        "data/raw",
        "data/processed",
        "data/sample",
        "outputs/sample",
        "reports/sample",
        "docs",
        "diagrams",
        "scripts",
        "tests",
    ]

    for relative_path in expected_dirs:
        assert (ROOT / relative_path).is_dir(), f"Missing {relative_path}"
