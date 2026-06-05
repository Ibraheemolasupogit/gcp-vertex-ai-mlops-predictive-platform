"""Safe placeholder for local batch prediction."""

from vertex_mlops_platform.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["batch-predict"]))
