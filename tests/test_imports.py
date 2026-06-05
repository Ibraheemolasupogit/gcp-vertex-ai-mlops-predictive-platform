import vertex_mlops_platform
from vertex_mlops_platform.cli import main


def test_package_imports() -> None:
    assert vertex_mlops_platform.__version__ == "0.1.0"


def test_cli_placeholder_command(capsys) -> None:
    exit_code = main(["train"])

    assert exit_code == 0
    assert "local model training" in capsys.readouterr().out
