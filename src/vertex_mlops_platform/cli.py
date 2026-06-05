"""Command-line placeholders for future local MLOps workflows."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create the project CLI parser."""
    parser = argparse.ArgumentParser(
        prog="vertex-mlops-platform",
        description="Run local predictive maintenance MLOps workflow placeholders.",
    )
    parser.add_argument(
        "command",
        choices=[
            "generate-demo-data",
            "train",
            "batch-predict",
            "monitor",
            "run-all-local",
        ],
        help="Placeholder command to describe the future workflow action.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a safe placeholder CLI command."""
    args = build_parser().parse_args(argv)
    messages = {
        "generate-demo-data": "Milestone 2 will generate synthetic predictive maintenance data.",
        "train": "A later milestone will run local model training and evaluation.",
        "batch-predict": "A later milestone will run batch prediction with registered models.",
        "monitor": "A later milestone will evaluate drift, quality, and retraining signals.",
        "run-all-local": "A later milestone will orchestrate the full local workflow.",
    }
    print(messages[args.command])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
