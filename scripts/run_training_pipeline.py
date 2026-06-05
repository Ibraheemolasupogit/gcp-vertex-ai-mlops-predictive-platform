"""Safe placeholder for the local training pipeline."""

from vertex_mlops_platform.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["train"]))
